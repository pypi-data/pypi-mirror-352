from typing import Dict, List, Any, Tuple, Set
import networkx as nx
import operator
import sys
from itertools import permutations
import matplotlib.pyplot as plt
from traxgen.utils import Tool, get_nested_value
from traxgen.visualizer import visualize_given_graph
import json


class TrajectoryPlanner:
    def __init__(self, tools: Dict[str, Tool], customer_data: Dict[str, Any], soft_ordering: List[str], conditionals: List[Dict[str, Any]] = None, ordered_tools = [], agent_name = "", tool_args = None):
        self.tools = tools
        self.constraints = []
        self.customer_data = customer_data
        self.conditionals = conditionals or []
        self.graph = nx.DiGraph()
        self.soft_ordering = soft_ordering
        self.ordered_tools = ordered_tools or []
        self.agent_name = agent_name
        self.tool_args = tool_args or {}
        self.end_after = None
        self.tools_to_skip = set()
        self.override_sequence = None
        self.param_overrides: Dict[str, Dict[str, str]] = {}
        self.full_override_tools: set[str] = set() 

    def _evaluate_single_condition(self, condition):
        actual_value = get_nested_value(self.customer_data, condition['field'])
    
        if 'compare_to' in condition:
            expected_value = get_nested_value(self.customer_data, condition['compare_to'])
            
        elif 'value' in condition:
            expected_value = condition['value']
    
        return self.evaluate_condition(actual_value, condition['operator'], expected_value)

    def evaluate_all_of(self, all_of_conditions):
        return all(self._evaluate_single_condition(condition) for condition in all_of_conditions)
    
    def evaluate_any_of(self, all_of_conditions):
        return any(self._evaluate_single_condition(condition) for condition in all_of_conditions)

    def evaluate_if_block(self, cond_list: List[Dict[str,Any]]) -> bool:
        results = []
        for clause in cond_list:
            if "all_of" in clause:
                results.append(self.evaluate_all_of(clause["all_of"]))
            elif "any_of" in clause:
                results.append(self.evaluate_any_of(clause["any_of"]))
            else:
                # simple field/operator/value
                field = clause["field"]
                op = clause["operator"]
                
                # Determine the actual value from customer data
                actual = get_nested_value(self.customer_data, field) if "[" in field else self.customer_data.get(field)
                
                # Determine the expected value from either 'value' or 'compare_to'
                if "compare_to" in clause:
                    compare_field = clause["compare_to"]
                    expected = get_nested_value(self.customer_data, compare_field) if "[" in compare_field else self.customer_data.get(compare_field)
                else:
                    expected = clause.get("value")
                results.append(self.evaluate_condition(actual, op, expected))
        return all(results)
    
    def evaluate_multiple_conditions(self, conditions: Dict[str, Dict[str, Any]]) -> bool:
        for field, condition in conditions.items():
            if not isinstance(condition, dict) or len(condition) != 1:
                raise ValueError(f"Invalid condition format for field '{field}': {condition}")
            op_str, expected_value = next(iter(condition.items()))
            actual_value = get_nested_value(self.customer_data, field) \
                           if '[' in field and ']' in field else self.customer_data.get(field)
            if not self.evaluate_condition(actual_value, op_str, expected_value):
                return False  # If any condition fails
        return True  # All conditions passed

    
    def _get_params_for_tool(self, tool: str) -> Dict[str, Any]:
        """
        Merge base args + conditional overrides, then resolve values.
        """
        # 1) if this tool was override_params, start from scratch; else  from the declared signature
        if tool in self.full_override_tools:
            merged: Dict[str, Any] = {}
        else:
            merged = dict(self.tool_args.get(tool, {}))

        # 2) apply any conditional overrides
        for param, expr in self.param_overrides.get(tool, {}).items():
            if expr is None:
                merged.pop(param, None)
            else:
                merged[param] = expr

        # 3) resolve each via get_nested_value
        params: Dict[str, Any] = {}
        for p_name, var in merged.items():
            params[p_name] = get_nested_value(self.customer_data, var) or var

        return params

    def apply_conditional_actions(self):
        # reset between calls
        self.tools_to_skip.clear()
        self.end_after = None
        self.override_sequence = None
        self.param_overrides.clear() 
        self.full_override_tools.clear()
    
        for cond in self.conditionals:
            passed  = self.evaluate_if_block(cond["if"])
            actions = cond.get("then") if passed else cond.get("else", [])
            for blk in actions or []:
                act = blk["action"]
                tg  = blk["target"]
                tgts = tg if isinstance(tg, list) else [tg]
    
                if act == "skip":
                    self.tools_to_skip.update(tgts)
                elif act == "end_after":
                    self.end_after = tgts[0]
                elif act == "override_trajectory":
                    self.override_sequence = tgts
                    
                elif act == "override_params":
                    # mark these tools as “full override” and store their new params
                    for tool in tgts:
                        self.full_override_tools.add(tool)
                        self.param_overrides.setdefault(tool, {}).update(blk["params"])

                else:
                    raise ValueError(f"Unknown action {act}")
  

    def add_tools_to_graph(self):
        # 1) Run your single pass of all conditionals
        self.apply_conditional_actions()
    
        # 2) Build a graph with all steps
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(self.ordered_tools)
    
        # 3) Prune out every tool the skip‐list told us to skip
        for t in list(self.graph.nodes()):
            if t in self.tools_to_skip:
                self.graph.remove_node(t)
    
        # 4) If there's an end_after, truncate
        if self.end_after and self.end_after in self.graph:
            nodes = list(self.graph.nodes())
            idx   = nodes.index(self.end_after)
            for n in nodes[idx+1:]:
                self.graph.remove_node(n)
    
        # 5) If override_sequence was set, enforce it now
        if self.override_sequence:
            # remove any not in override
            for n in list(self.graph.nodes()):
                if n not in self.override_sequence:
                    self.graph.remove_node(n)
            # re-add missing ones in that exact order
            for n in self.override_sequence:
                if n not in self.graph:
                    self.graph.add_node(n)
    
        # 6) Finally wire up edges in the remaining ordering
        remaining = [n for n in self.ordered_tools if n in self.graph]
        self.graph = self.build_graph_with_order(remaining)

    def evaluate_condition(self, actual_value, op_str, expected_value) -> bool:
        if expected_value is None:
            if op_str == "==":
               return actual_value is None
            if op_str == "!=":
                return actual_value is not None

        # in not in
        if op_str == "in":
            return actual_value in expected_value
        if op_str == "not in":
            return actual_value not in expected_value

        if op_str == 'contains':
            return expected_value in actual_value
        if op_str == 'not contains':
            return expected_value not in actual_value

        # None
        if expected_value == "None" and op_str == "==":
            return actual_value is None
        if expected_value == "None" and op_str == "!=":
            return actual_value is not None

        if actual_value is None:
            return False #because we have already tested for expected value none first

        # num coercion
        if isinstance(actual_value, (int, float)) and isinstance(expected_value, str):
            try:
                expected_value = type(actual_value)(expected_value)
            except ValueError:
                actual_value = str(actual_value)

        # boolean coercion
        if isinstance(actual_value, bool) and isinstance(expected_value, str):
            if expected_value.lower() == "true":
                expected_value = True
            elif expected_value.lower() == "false":
                expected_value = False

        # coerce lists (and other non‐strs) to string for plain equality/inequality
        if isinstance(actual_value, str) and not isinstance(expected_value, str):
            expected_value = str(expected_value)

        ops = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            "not": operator.ne,
        }
        return ops[op_str](actual_value, expected_value)
        

    def build_graph_with_order(self, tool_order: List[str]) -> nx.DiGraph:
        graph = nx.DiGraph()
        graph.add_nodes_from(tool_order)
        for i in range(len(tool_order) - 1):
            graph.add_edge(tool_order[i], tool_order[i + 1])
        return graph

    def generate_soft_variants(self, ordered_tools: List[str], soft_blocks: List[List[str]]) -> List[List[str]]:
        
        soft_blocks = [sorted(block, key=lambda x: ordered_tools.index(x)) for block in soft_blocks]
    
        #base trajectory is full list of tools
        variants = [ordered_tools[:]]
    
        for block in soft_blocks:
            new_variants = []
            for variant in variants:
                # start & end indices of current soft block in this variant
                start_idx = variant.index(block[0])
                end_idx = variant.index(block[-1]) + 1
    
                before = variant[:start_idx]
                after = variant[end_idx:]
    
                # all permutations of the soft block
                for perm in permutations(block):
                    new_variants.append(before + list(perm) + after)
    
            variants = new_variants  # update base for next soft block
    
        return variants

    def get_google_trajectory(self, trajectories: List[List[str]]) -> List[List[Dict[str, Any]]]:
        result = []
        for traj in trajectories:
            full_traj = []
            for tool in traj:
                params = self._get_params_for_tool(tool)
                full_traj.append({
                    "tool_name": tool,
                    "tool_input": params
                })
            result.append(full_traj)
        return result

    @staticmethod
    def format_google_multi_agent_trajectory(split: Dict[str, List[str]], planners: List) -> List[List[Dict[str, Any]]]:
        result = []
        planner_lookup = {p.agent_name: p for p in planners}
    
        for agent, tools in split.items():
            planner = planner_lookup[agent]
            for tool in tools:
                # args = planner.tool_args.get(tool, {})
                # resolved_args = {
                #     k: get_nested_value(planner.customer_data, v) or v for k, v in args.items()
                # }
                params = planner._get_params_for_tool(tool)

                result.append({
                    "tool_name": tool,
                    "tool_input": params
                })
        return result


    def get_langchain_tool_trajectory(
        self,
        trajectories: List[List[Dict[str, Any]]],
        has_result: bool = False
    ) -> List[List[Dict[str, Any]]]:
        formatted = []
        for traj in trajectories:
            dialogue = []
            for step in traj:
                tool_name = step["tool_name"]
                # CORRECTED: use tool_name, not name
                params = self._get_params_for_tool(tool_name)

                dialogue.append({
                    "role": "assistant",
                    "tool_calls": [{
                        "name": tool_name,
                        "arguments": params
                    }]
                })

                if has_result:
                    # simulate or pull from step if you want actual results
                    dialogue.append({
                        "role": "tool",
                        "content": f"{tool_name} result"
                    })

            formatted.append(dialogue)
        return formatted

    @staticmethod    
    def format_langchain_multi_agent_trajectory(self, split: Dict[str, List[str]], planners: List, has_result: bool = False ) -> List[List[Dict[str, Any]]]:
        result = []
        planner_lookup = {p.agent_name: p for p in planners}

        for agent, tools in split.items():
            planner = planner_lookup[agent]
            dialogue = []
            for tool in tools:
                params = planner._get_params_for_tool(tool)
                dialogue.append({
                    "role": "assistant",
                    "tool_calls": [{
                        "name": tool,
                        "arguments": params
                    }]
                })
                if has_result:
                    dialogue.append({
                        "role": "tool",
                        "content": f"{tool} result"
                    })
            result.append(dialogue)

        return result


    def format_traxgen_trajectory(self, trajectory: List[str]) -> List[List[str]]:
        def fmt(traj):
            lines = [f"agent: {self.agent_name.lower()}"]
            for tool in traj:
                params = self._get_params_for_tool(tool)
                args_str = ", ".join(f"{k}={v}" for k, v in params.items())
                lines.append(f"tool: {tool}({args_str})")
            return lines

        # wrap single vs. list-of-lists
        if trajectory and isinstance(trajectory[0], str):
            return [fmt(trajectory)]
        else:
            return [fmt(traj) for traj in trajectory]

    @staticmethod
    def format_traxgen_multi_agent_trajectory(split: Dict[str, List[str]], planners: List) -> List[str]:
        result = []
        planner_lookup = {p.agent_name: p for p in planners}

        for agent, tools in split.items():
            planner = planner_lookup[agent]
            result.append(f"agent: {agent.lower()}")
            for tool in tools:
                params = planner._get_params_for_tool(tool)
                args_str = ", ".join(f"{k}={v}" for k, v in params.items())
                result.append(f"tool: {tool}({args_str})")
        return result

    def generate_valid_trajectories(self) -> List[List[str]]:
        self.add_tools_to_graph()
        
        if not self.graph.nodes():
            print("ERROR: No nodes in graph!")
            return []  
            
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Hard constraints form a cycle!")
    
        #extract the post‑prune tool set
        surviving_tools = set(self.graph.nodes())
        
        # base ordering (override_sequence takes precedence)
        base_tools = self.override_sequence or self.ordered_tools
        
        # only permute soft‑blocks if *all* of their tools survived pruning
        soft_blocks = [
            block for block in self.soft_ordering
            if (
                isinstance(block, list)
                and all(tool in surviving_tools for tool in block)
            )
        ]
        
        # generate raw permutations (or a single base if no soft‑blocks)
        all_tool_orders = (
            self.generate_soft_variants(base_tools, soft_blocks)
            if soft_blocks
            else [base_tools]
        )
        
        # filter out any pruned tools *and* dedupe identical trajectories
        seen: Set[Tuple[str, ...]] = set()
        valid_trajectories: List[List[str]] = []
        
        for order in all_tool_orders:
            filtered = tuple(t for t in order if t in surviving_tools)
            if filtered not in seen:
                seen.add(filtered)
                valid_trajectories.append(list(filtered))
        
        return valid_trajectories
