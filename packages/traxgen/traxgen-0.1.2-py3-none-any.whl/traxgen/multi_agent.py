from typing import List, Dict, Any, Union, Tuple
from itertools import product
import json
from .parser import parse_routine_to_planner
from .planner import TrajectoryPlanner
from copy import deepcopy

def generate_multi_agent_trajectory(
    agent_sequence: List[str],
    customer_data: Dict[str, Any],
    routine_data: Dict[str, Dict[str, Any]],
) -> Tuple[List[List[str]], List[List[TrajectoryPlanner]]]:
    all_trajectories_by_agent = []
    all_planner_variants_by_agent = []
    
    for agent_name in agent_sequence:
        workflow_data = routine_data[agent_name]

        base_planner = parse_routine_to_planner(workflow_data, customer_data)
        valid_trajs = base_planner.generate_valid_trajectories()

        if not valid_trajs:
            raise ValueError(f"No valid trajectories for agent: {agent_name}")

        planners_for_agent = []

        for traj in valid_trajs:
            planner_variant = TrajectoryPlanner(
                tools=base_planner.tools,
                customer_data=base_planner.customer_data,
                soft_ordering=base_planner.soft_ordering,   
                conditionals=base_planner.conditionals,
                ordered_tools=traj,                         
                agent_name=base_planner.agent_name,
                tool_args=base_planner.tool_args
            )
            # rebuild its graph so any downstream checks still know about the order
            planner_variant.graph = planner_variant.build_graph_with_order(traj)
            planners_for_agent.append(planner_variant)

        all_trajectories_by_agent.append(valid_trajs)
        all_planner_variants_by_agent.append(planners_for_agent)

    multi_agent_trajectories = []
    planner_combinations = []

    trajectory_products = list(product(*all_trajectories_by_agent))
    planner_products = list(product(*all_planner_variants_by_agent))

    for traj_combo, planner_combo in zip(trajectory_products, planner_products):
        combined = []
        for idx, traj in enumerate(traj_combo):
            agent_name = planner_combo[idx].agent_name
            combined.append(f"{agent_name}_agent")

            if idx < len(traj_combo) - 1:
                traj = [step for step in traj if step != "complete_case"]

            combined.extend(traj)

        multi_agent_trajectories.append(combined)
        planner_combinations.append(list(planner_combo))

    return multi_agent_trajectories, planner_combinations
