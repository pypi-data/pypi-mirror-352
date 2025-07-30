import os
import json
from typing import Dict, List
from pydantic import BaseModel, ValidationError
import sys
import re

def validate_agent_sequence(agent_sequence: List[str], routine_data: str) -> bool:
    """
    Validates the agent sequence.
    Ensures it's a List[str], non-empty, no duplicates.
    """
    try:
        if type(agent_sequence) == str:
            agent_sequence = [agent_sequence]
        if not isinstance(agent_sequence, list) or not all(isinstance(agent, str) for agent in agent_sequence):
            raise ValueError("Agent_sequence must be a list of strings.")
        
        if len(agent_sequence) == 0:
            raise ValueError("Agent_sequence cannot be empty.")
        
        if len(agent_sequence) != len(set(agent_sequence)):  # No duplicates unless intentional
            raise ValueError("Agent_sequence contains duplicate agents.")
        
        #check that all agent names in agent_sequence are keys in routine_data
        missing_agents = [agent for agent in agent_sequence if agent not in routine_data]
        if missing_agents:
            raise ValueError(f"The following agents are missing from routine_data: {', '.join(missing_agents)}")

        # print("Validation passed: All agent names in agent_sequence are valid and there are no extra agent names in routine_data.")

    except ValueError as e:
        print(f"Error: {e}") 
        sys.exit(1)
    

def validate_styles(styles):
    valid_styles = {"tool_only", "google", "langchain", "traxgen"}
    try:
        invalid_styles = [style for style in styles if style not in valid_styles]
        if invalid_styles:
            print(f"❌ Error: Invalid style(s) detected: {', '.join(invalid_styles)}.")
            sys.exit(1)
        # print("All styles are valid.")
        return True
    except ValueError as e:
        print(f"Error: {e}") 
        sys.exit(1)
        
def validate_return_format(return_format, customer_data, customer_data_path):
    try:
        # Validate return_format
        if return_format not in {"return", "trajectory_only", "data_and_trajectory"}:
            raise ValueError(f"Invalid return_format: {return_format}. Expected 'return', 'trajectory_only' or 'data_and_trajectory'.")
        
        # print("return_format is valid.")
        
        # If 'append' is chosen, ensure customer_data is provided
        if return_format == "data_and_trajectory" and customer_data is None:
            raise ValueError("When return_format is 'data_and_trajectory', customer_data must be provided.")

        # Validate customer_data_path
        if not customer_data_path or customer_data_path == ".":
            customer_data_path = "."  # Default to current directory if not provided
            print("customer_data_path is not provided. Using default path: current directory.")
        
        # else:
        #     continue
            # print(f"return_format '{return_format}' is valid:  {customer_data_path}")
        
        return True
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

def validate_visualize(visualize):
    """
    Validate that 'visualize' is a boolean value (True or False).
    """
    try:
        if not isinstance(visualize, bool):
            raise ValueError(f"❌ Error: Invalid value for 'visualize': {visualize}. It must be a boolean (True or False).")
        
        # print(f"visualize is valid: {visualize}")
        return True
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)        



def validate_conditional_routine_structure(cond, routine_name, path="conditional", steps=None):
    errors = []
    # 1) must be a dict
    if not isinstance(cond, dict):
        return [f"❌ Error: [{routine_name}] {path} must be a dict"]

    keys = set(cond.keys())
    # 2) top-level keys
    required_top = {"if", "then"}
    allowed_top = {"if", "then", "else"}
    missing_top = required_top - keys
    if missing_top:
        errors.append(f"❌ Error: [{routine_name}] {path} missing required field(s): {missing_top}")

    extra_top = keys - allowed_top
    if extra_top:
        errors.append(f"❌ Error: [{routine_name}] {path} has unexpected field(s): {extra_top}")

    # 3) validate IF block
    if_block = cond.get("if")
    if not isinstance(if_block, list):
        errors.append(f"❌ Error: [{routine_name}] {path}['if'] must be a list")
    else:
        # each clause must be simple or grouping
        simple_req = {"field", "operator", "value"}
        compare_to_req = {"field", "operator", "compare_to"}

        for i, clause in enumerate(if_block):
            cl_path = f"{path}['if'][{i}]"
            if not isinstance(clause, dict):
                errors.append(f"❌ Error: [{routine_name}] {cl_path} must be a dict")
                continue

            cl_keys = set(clause.keys())
             # 3a) simple clause style: must have exactly field/operator/value
            if cl_keys == simple_req:
                missing = simple_req - cl_keys
                extra   = cl_keys - simple_req
                if missing:
                    errors.append(f"❌ Error: [{routine_name}] {cl_path} missing required key(s): {missing}")
                if extra:
                    errors.append(f"❌ Error: [{routine_name}] {cl_path} has unexpected key(s): {extra}")
                continue

            # 3b) compare_to clause style: must have exactly field/operator/compare_to
            if cl_keys == compare_to_req:
                missing = compare_to_req - cl_keys
                extra   = cl_keys - compare_to_req
                if missing:
                    errors.append(f"❌ Error: [{routine_name}] {cl_path} missing required key(s): {missing}")
                if extra:
                    errors.append(f"❌ Error: [{routine_name}] {cl_path} has unexpected key(s): {extra}")
                continue

            # 3b) grouping (all_of / any_of)
            if "all_of" in clause or "any_of" in clause:
                key = "all_of" if "all_of" in clause else "any_of"
                if cl_keys != {key}:
                    errors.append(f"❌ Error: [{routine_name}] {cl_path} must only contain '{key}'")
                    continue
                subconds = clause[key]
                if not isinstance(subconds, list):
                    errors.append(f"❌ Error: [{routine_name}] {cl_path}['{key}'] must be a list")
                    continue
                for j, sub in enumerate(subconds):
                    sc_path = f"{cl_path}['{key}'][{j}]"
                    if not isinstance(sub, dict):
                        errors.append(f"❌ Error: [{routine_name}] {sc_path} must be a dict")
                        continue
                    sub_keys = set(sub.keys())
                    if not simple_req.issubset(sub_keys):
                        errors.append(f"❌ Error: [{routine_name}] {sc_path} missing required key(s): {simple_req - sub_keys}")
                    extra_sub = sub_keys - simple_req
                    if extra_sub:
                        errors.append(f"❌ Error: [{routine_name}] {sc_path} has unexpected key(s): {extra_sub}")
                continue

            # 3c) neither
            errors.append(
                f"❌ [{routine_name}] {cl_path} invalid clause: "
                "must be either simple (field/operator/value) or an all_of/any_of grouping"
            )

 # --- THEN/ELSE action lists ---
    valid_actions = {"skip", "end_after", "override_trajectory", "override_params"}
    for branch in ("then", "else"):
        actions = cond.get(branch, [])
        if not isinstance(actions, list):
            errors.append(f"❌ Error: [{routine_name}] {path}['{branch}'] must be a list")
            continue

        for idx, action in enumerate(actions):
            a_path = f"{path}['{branch}'][{idx}]"
            if not isinstance(action, dict):
                errors.append(f"❌ Error: [{routine_name}] {a_path} must be a dict")
                continue

            act = action.get("action")
            tgt = action.get("target")
            # first check action name
            if act not in valid_actions:
                errors.append(f"❌ Error: [{routine_name}] {a_path}.action '{act}' is not valid")
                continue

            # now validate keys depending on action type
            if act == "override_params":
                # must have exactly these keys:
                allowed_keys = {"action", "target", "params"}
                missing = allowed_keys - set(action.keys())
                extra   = set(action.keys()) - allowed_keys
                if missing:
                    errors.append(f"❌ Error: [{routine_name}] {a_path} missing required key(s): {missing}")
                if extra:
                    errors.append(f"❌ Error: [{routine_name}] {a_path} has unexpected key(s): {extra}")

                # params must be a dict of strings to strings
                params = action.get("params")
                if not isinstance(params, dict):
                    errors.append(f"❌ Error: [{routine_name}] {a_path} 'params' must be a dict")
                else:
                    for p_name, expr in params.items():
                        if not isinstance(p_name, str) or not isinstance(expr, str):
                            errors.append(
                                f"❌ Error: [{routine_name}] {a_path} 'params' keys and values must be strings"
                            )
            else:
                # for all other actions, only action+target allowed
                allowed_keys = {"action", "target"}
                missing = allowed_keys - set(action.keys())
                extra   = set(action.keys()) - allowed_keys
                if missing:
                    errors.append(f"❌ Error: [{routine_name}] {a_path} missing required key(s): {missing}")
                if extra:
                    errors.append(f"❌ Error: [{routine_name}] {a_path} has unexpected key(s): {extra}")

    return errors


def validate_routine_format(routine_data: Dict[str, dict]) -> bool:
    """
    Validates the structure of all routines in the routine_data dictionary.
    Exits the program with an error if any routine is invalid.
    """
    try:
        required_keys = {"agent", "steps", "soft_ordering", "conditionals"}

        for routine_name, routine in routine_data.items():
            routine_keys = set(routine.keys())

            # Check for missing keys
            missing = required_keys - routine_keys
            if missing:
                raise ValueError(f"❌ Error: [{routine_name}] Routine: Missing key(s): {', '.join(missing)}")

            # Check for extra keys
            extra = routine_keys - required_keys
            if extra:
                raise ValueError(f"❌ Error: [{routine_name}] Routine: Unexpected extra key(s): {', '.join(extra)}")

            # Validate 'agent'
            if not isinstance(routine.get("agent"), str):
                raise ValueError(f"❌ Error: [{routine_name}] Routine: 'agent' must be a string.")

            # Validate 'steps'
            steps = routine.get("steps")
            if not isinstance(steps, list):
                raise ValueError(f"❌ Error: [{routine_name}] Routine: 'steps' must be a list.")
            
            non_str_steps = [(i, step) for i, step in enumerate(steps) if not isinstance(step, str)]
            if non_str_steps:
                formatted = ", ".join([f"value: {repr(step)}" for i, step in non_str_steps])
                raise ValueError(
                    f"❌ Error: [{routine_name}] Routine: 'steps' must be a list of strings. "
                    f"Invalid item(s) found — {formatted}"
                )

            # Validate 'soft_ordering'
            steps_function_names = [re.match(r"([^\(]+)", step).group(1) for step in steps]
            soft_ordering = routine.get("soft_ordering")
            if not isinstance(soft_ordering, list) or not all(
                isinstance(group, list) and all(isinstance(item, str) for item in group) for group in soft_ordering
            ):
                raise ValueError(f"❌ Error: [{routine_name}] Routine: 'soft_ordering' must be a list of lists of strings.")

            # Check if each item in soft_ordering exists in steps (by base function name)
            missing_in_steps = []
            for group in soft_ordering:
                for item in group:
                    if item not in steps_function_names:
                        missing_in_steps.append(item)

            if missing_in_steps:
                raise ValueError(f"❌ Error: [{routine_name}] Routine: 'soft_ordering' contains tool names not found in 'steps': {', '.join(missing_in_steps)}")


            # Validate 'conditionals'
            conditionals = routine.get("conditionals")
            if not isinstance(conditionals, list):
                raise ValueError(f"❌ Error: [{routine_name}] 'Routine: conditionals' must be a list.")
            
            conditional_errors = []
            for i, cond in enumerate(conditionals):
                if not isinstance(cond, dict):
                    conditional_errors.append(f"❌ Error:[{routine_name}] Routine: Conditional #{i} must be a dictionary.")
                nested_errors = validate_conditional_routine_structure(cond, routine_name, path=f"conditionals[{i}]", steps = steps)
                conditional_errors.extend(nested_errors)

            if conditional_errors:
                raise ValueError("\n".join(conditional_errors))

            # print(f"[{routine_name}] Routine is valid ✅")

        return True

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)



def extract_variable_fields(steps):
    fields = set()
    #find first (...)
    paren_rx = re.compile(r"\w+\(([^)]*)\)")
    #find assignments inside that: param = var
    assign_rx = re.compile(r"[,\s]*\w+\s*=\s*([a-zA-Z_]\w*(?:\['\w+'\])?)")
    #normalize bracketed into a single string
    bracket_rx = re.compile(r"^([a-zA-Z_]\w*)\['(\w+)'\]$")

    for step in steps:
        # 1) bracketed fields *anywhere* in the step
        for obj, fld in re.findall(r"([a-zA-Z_]\w*)\[['\"](\w+)['\"]\]", step):
            fields.add(f"{obj}['{fld}']")

        # 2) simple vars in the first (...) block
        m = paren_rx.match(step)
        if m:
            inside = m.group(1) # ex. "customer_id = customer_id, amount = total_paid"
            for am in assign_rx.finditer(inside):
                var = am.group(1)
                # normalize bracketed
                b = bracket_rx.match(var)
                if b:
                    fields.add(f"{b.group(1)}['{b.group(2)}']")
                else:
                    fields.add(var)

    return fields

def extract_fields_from_conditionals(conditionals):
    """Recursively pull out all field names from conditionals, including bracketed and flat keys."""
    out = set()
    
    def extract_from_expr(expr):
        fields = set()
        if isinstance(expr, str):
            # Handle bracketed access like obj['field']
            for obj, f in re.findall(r"([a-zA-Z_]\w*)\[['\"](\w+)['\"]\]", expr):
                fields.add(f"{obj}['{f}']")
            # If it's a plain field name (no brackets)
            if re.fullmatch(r"[a-zA-Z_]\w*", expr):
                fields.add(expr)
        return fields

    for cond in conditionals:
        if not isinstance(cond, dict):
            continue
        
        if "field" in cond:
            out |= extract_from_expr(cond["field"])            
            
        if "if" in cond:
            for subfield in cond["if"]:
                out |= extract_from_expr(subfield)
                for subfield in cond["if"]:
                    out |= extract_from_expr(subfield)
                    if isinstance(subfield, dict) and "compare_to" in subfield:
                        out |= extract_from_expr(subfield["compare_to"])
                    if isinstance(subfield, dict) and "field" in subfield:
                        out |= extract_from_expr(subfield["field"])                    
                
        # Recursively check then/else branches
        for key in ["then", "else"]:
            branch = cond.get(key)
            if isinstance(branch, dict):
                out |= extract_fields_from_conditionals([branch])

    return out

def validate_customer_data_fields(customer_data, routine_data):
    errors = []

    for routine_name, routine in routine_data.items():
        steps = routine.get("steps", [])
        conditionals = routine.get("conditionals", [])

        param_fields = extract_variable_fields(steps)
        conditional_fields = extract_fields_from_conditionals(conditionals)
        all_fields = param_fields | conditional_fields
        # print(f"▶️  REQUIRED FIELDS for {routine_name}:", all_fields)

        for customer in customer_data:
            customer_id = customer.get("customer_id")

            for field in all_fields:
                if "['" in field:
                    match = re.match(r"([a-zA-Z_]\w*)\['(\w+)'\]", field)
                    if not match:
                        errors.append(f"❌ Error: Invalid nested field format: **{field}**")
                        continue
                    obj, sub = match.groups()
                    if not (isinstance(customer.get(obj), dict) and sub in customer[obj]):
                        errors.append(
                            f"❌ Error: The customer data is missing the field **{field}** for customer {customer_id}, "
                            f"which is needed for the **{routine_name}** routine."
                        )
                else:
                    if field not in customer:
                        errors.append(
                            f"❌ Error: The customer data is missing the field **{field}**, "
                            f"which is needed for the **{routine_name}** routine."
                        )

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        # print("Customer data is valid ✅")
        return True

def validate_customer_data_requirements(routine_data, style, customer_data):
    """
    Validate that customer_data is provided when required by the routine.
    """
    errors = []
    for routine_name, routine in routine_data.items():
        conditionals = routine.get("conditionals", [])

        is_tool_only_without_conditionals = (
            len(style) == 1 and style[0] == "tool_only" and conditionals == []
        )

        if not is_tool_only_without_conditionals and customer_data is None:
            if style[0] != 'tool_only':
                errors.append(f"❌ Error with Routine {routine_name}: Customer data is needed for a {style} trajectory style. Only 'tool_only' trajectory works without customer data.")
            if conditionals != []:
                errors.append(f"❌ Error with Routine {routine_name}: Customer data is required when the routine contains conditinals.")
                
        do_full_validation = (
            customer_data is not None and 
            not is_tool_only_without_conditionals
        )

        if do_full_validation:
            validate_customer_data_fields(customer_data, routine_data)

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)