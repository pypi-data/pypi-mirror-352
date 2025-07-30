from typing import Dict
import re
from .planner import TrajectoryPlanner


def parse_routine_to_planner(routine: Dict, customer_data: Dict) -> TrajectoryPlanner:
    tools = {}
    constraints = []
    conditionals = routine.get("conditionals", [])
    soft_ordering = routine.get("soft_ordering", [])
    agent_name = routine.get("agent", "")

    # 1. Parse the steps list
    parsed_steps = []
    for step_str in routine["steps"]:
        # Match pattern: tool(args) -> [produced1, produced2]
        match = re.match(r"(\w+)\((.*?)\)\s*(?:->\s*\[(.*?)\])?", step_str)
        if match:
            tool_name, args_str, produced_str = match.groups()
            args = {}
            if args_str.strip():
                for part in args_str.split(","):
                    key, value = part.split("=")
                    args[key.strip()] = value.strip()
            produced = []
            if produced_str:
                produced = [p.strip() for p in produced_str.split(",")]
            parsed_steps.append((tool_name, args, produced))
        else:
            # If no parentheses or malformed line, treat as tool with no params or outputs
            parsed_steps.append((step_str.strip(), {}, []))

    tool_args = {}
    # 2. Build tools metadata from parsed steps
    for tool_name, args, produced in parsed_steps:
        if tool_name not in tools:
            tools[tool_name] = {
                "required_fields": list(args.keys()),
                "produces": produced
            }
        tool_args[tool_name] = args
    ordered_tools = [tool_name for tool_name, _, _ in parsed_steps]

    return TrajectoryPlanner(tools, customer_data, soft_ordering, conditionals, ordered_tools, agent_name, tool_args)