import random
import datetime
from collections import defaultdict
import re
from .validator import extract_variable_fields, extract_fields_from_conditionals 


def parse_random_value(value_str):
    if isinstance(value_str, tuple):
        value_str = list(value_str)
    if isinstance(value_str, list):
        if all(isinstance(i, tuple) for i in value_str):  # list of tuples
            options = value_str
            weights = [1 for _ in options]
            selected_tuple = random.choices(options, weights=weights, k=1)[0]
            return list(selected_tuple)
        elif all(isinstance(i, str) for i in value_str):
            return value_str 
        else:
            return random.choice(value_str)
    if isinstance(value_str, str):
        if value_str.startswith("random_int("):
            start, end = map(int, re.findall(r"\d+", value_str))
            return random.randint(start, end)
        elif value_str.startswith("random_float("):
            start, end = map(float, re.findall(r"[\d.]+", value_str))
            return round(random.uniform(start, end), 2)
        elif "random_date" in value_str:
            start_date, end_date = re.findall(r"'(.*?)'", value_str)
            return random_date(start_date, end_date)  
    return value_str  

def random_date(start_date: str, end_date: str) -> str:
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_date = start + datetime.timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")


def resolve_path(data: dict, path: str):
    """
    path: something like "booking_info['cabin_class']" 
          or "outer['inner']['deep']"
    """
    # find all the parts: first the root key, then each bracketed key
    # e.g. "booking_info['cabin_class']" → ['booking_info', 'cabin_class']
    parts = re.findall(r"([a-zA-Z_]\w*)|\['([^']+)'\]", path)
    # parts is list of tuples; flatten it
    keys = [p[0] or p[1] for p in parts]

    cur = data
    for k in keys:
        # whenever you hit something that isn’t a dict, bail
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur

    
def apply_same_as(field_key, other_field, probability, customer_data, user_field_values):
    cfg = user_field_values.get(field_key, {})
    # decide if we should copy
    if random.random() < probability:
        # if it's nested, use our resolver; otherwise just a flat lookup
        if "['" in other_field:
            return resolve_path(customer_data, other_field)
        else:
            return customer_data.get(other_field)

    # fallback sampling logic continues as before...
    dist = cfg
    if set(cfg.keys()) <= {'same_as', 'probability'}:
        dist = user_field_values.get(other_field, {})

    options = list(dist.keys())
    weights = list(dist.values())
    chosen = random.choices(options, weights=weights, k=1)[0]
    return parse_random_value(chosen)

def convert_to_hashable(field):
    if isinstance(field, list):
        return tuple(field)  # or frozenset(field) if ordering doesn't matter
    return field

def generate_customer_profile(required_fields: set, user_field_values: dict) -> dict:
    customer_data = {}

    def sort_key(f):
        cfg = user_field_values.get(f, {})
        return (1 if 'same_as' in cfg else 0, f)

    for field in sorted(required_fields, key=sort_key):
        # print(f"[DEBUG] Processing field: {field}")
        cfg = user_field_values.get(field, {})
        is_nested = "['" in field

        if is_nested:
            match = re.match(r"([a-zA-Z_]\w*)\['([^']+)'\](\['([^']+)'\])?", field)
            if not match:
                raise ValueError(f"Unsupported field format: {field}")
            outer = match.group(1)
            inner = match.group(2)
            inner2 = match.group(4)  # This will be None if it's not a second-level nested field

            # Ensure outer field exists
            customer_data.setdefault(outer, {})

            # If second level exists, ensure inner field is a dictionary
            if inner2:
                customer_data[outer].setdefault(inner, {})
            else:
                customer_data[outer].setdefault(inner, {})
        
        # decide value
        if 'same_as' in cfg:
            other = cfg['same_as']
            prob  = cfg.get('probability', 1.0)
            val   = apply_same_as(field, other, prob, customer_data, user_field_values)
        else:
            # pure random choice
            options = list(cfg.keys())
            weights = list(cfg.values())

            chosen = random.choices(options, weights=weights, k=1)[0]
            val = parse_random_value(chosen)
        
        # Handle boolean, null conversion
        if isinstance(val, str):
            if val.lower() == 'true':
                val = True
            elif val.lower() == 'false':
                val = False
            elif val.lower() == 'null':
                val = None

        field = convert_to_hashable(field)

        # write it back
        if is_nested:
            if inner2:
                customer_data[outer][inner][inner2] = val
            else:
                customer_data[outer][inner] = val
        else:
            customer_data[field] = val

    return customer_data