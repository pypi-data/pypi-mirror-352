import os
import json
from typing import TypedDict, List, Dict, Any, Union
import re

# def get_nested_value(data, field_path):
#     field_path = field_path.replace("']['", ".").replace("['", ".").replace("']", "")
    
#     # Split the field_path into keys
#     keys = field_path.split(".")
    
#     # Traverse the dictionary based on the keys
#     for key in keys:
#         if isinstance(data, dict) and key in data:
#             data = data[key]
#         else:
#             return None  # Return None if key doesn't exist
#     return data

class Tool(TypedDict, total=False):
    required_fields: List[str]
    produces: List[str]


# def get_nested_value(data: dict, field_path: str):
#     """
#     works with things like:
#         data["foo"]["bar"]
#         data["inventory_info"][ dynamic_key ]["availability"]
#     where dynamic_key might be another bracketed
#     expression like user_provided_info['product_id'].
#     """
#     # Match root name then any number of [expr] pieces
#     m = re.match(r"^([a-zA-Z_]\w*)(\[.*\])?$", field_path)
#     if not m:
#         return None

#     root, rest = m.groups()
#     current = data.get(root)
#     if rest:
#         # find each bracketed part: e.g. "[user_provided_info['product_id']]" or "['availability']"
#         for expr in re.findall(r"\[([^\]]+)\]", rest):
#             # if it's quoted, strip the quotes _once_ and treat as literal
#             if (expr.startswith("'") and expr.endswith("'")) or (expr.startswith('"') and expr.endswith('"')):
#                 key = expr[1:-1]
#             else:
#                 # otherwise treat expr as _another_ nested path and resolve it
#                 key = get_nested_value(data, expr)
#             if not isinstance(current, dict):
#                 return None
#             current = current.get(key)
#     return current


def get_nested_value(data: Dict[str, Any], expression: str) -> Any:
    """
    Retrieve a value from `data` given an expression like:
       "inventory_info[user_provided_info['product_id']]['availability']"
    Supports arbitrarily nested brackets, and will evaluate inner expressions
    (e.g. user_provided_info['product_id']) first.
    """
    # 1) Peel off the “root” before the first '['
    first_bracket = expression.find('[')
    if first_bracket == -1:
        # No brackets at all, just a plain field
        return data.get(expression)
    
    root = expression[:first_bracket]
    rest = expression[first_bracket:]
    
    current = data.get(root)
    # 2) Process each [ … ] block
    while rest:
        if not rest.startswith('['):
            return None  # malformed
        # find matching closing ']' by counting depth
        depth = 0
        for i, ch in enumerate(rest):
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    break
        else:
            return None  # no matching bracket
        
        inner = rest[1:i]      # everything between [ and its matching ]
        rest = rest[i+1:]      # consume this block
        
        # 3) Determine the actual key to use
        if (inner.startswith("'") and inner.endswith("'")) or \
           (inner.startswith('"') and inner.endswith('"')):
            # literal string key
            key = inner[1:-1]
        else:
            # dynamic: evaluate recursively
            key = get_nested_value(data, inner)
        
        # 4) Index into current
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except Exception:
                return None
        else:
            return None
    
    return current


    
def save_trajectory_to_json(trajectory, output_file="output/multi_agent_trajectory.json"):
    """
    Save the multi-agent trajectory to a JSON file.
    
    Args:
        trajectory: The multi-agent trajectory to save (flattened format)
        output_file: Path to the output JSON file
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Format the trajectory data
    trajectory_data = []
    current_agent = None
    current_steps = []
    
    for item in trajectory:
        if item.endswith("_agent"):  # This is an agent marker
            # Save previous agent data if exists
            if current_agent and current_steps:
                trajectory_data.append({
                    "agent": current_agent.replace("_agent", ""),
                    "steps": current_steps
                })
                current_steps = []
            
            # Start a new agent
            current_agent = item
        else:
            current_steps.append(item)
    
    # Add the last agent
    if current_agent and current_steps:
        trajectory_data.append({
            "agent": current_agent.replace("_agent", ""),
            "steps": current_steps
        })
    
    # Save to JSON file
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(trajectory_data, file, indent=2)
    
    print(f"Trajectory saved to {output_file}")


def split_trajectory_by_agent(flat_trajectory: List[str]) -> Dict[str, List[str]]:
    split = {}
    current_agent = None

    for item in flat_trajectory:
        if item.endswith("_agent"):
            current_agent = item.replace("_agent", "")
            split[current_agent] = []
        else:
            if current_agent is None:
                raise ValueError("Tool step encountered before any agent declaration.")
            split[current_agent].append(item)

    return split


