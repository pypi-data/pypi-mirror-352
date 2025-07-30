# Traxgen

**Traxgen** is a Python package for generating synthetic multi-agent trajectories for simulation, research, and evaluation purposes. It provides a modular framework to configure agent behaviors, environments, and export formats, making it suitable for academia and industry alike.


## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Trajectory Types Support](#trajectory-types-support)
  - [Traxgen Style](#traxgen-style)
  - [Tool Only](#tool-only)
  - [Google Style](#google-style)
  - [LangChain Tool Style](#langchain-tool-style)
- [Main Functions](#main-functions)
  - [generate_trajectories](#generate_trajectories)
  - [get_required_fields](#get_required_fieldsroutine_data)
  - [generate_field_template](#generate_field_templaterequired_fields)
  - [generate_user_profiles](#generate_user_profiles)
- [Example Inputs](#example-inputs)
  - [customer_data](#customer_data)
  - [routine_data](#routine_data)
- [Routine JSON Files Explained](#routine-json-files-explained)
  - [Agent](#agent)
  - [Steps](#steps)
  - [Soft Ordering](#soft-ordering)
  - [Conditionals](#conditionals)
  - [Operators](#Supported-Operators)
  - [Actions](#Common-Actions-in-Conditionals)
  - [Example of a Full Routine](#example-of-a-full-routine)
- [License](#license)

---

## Introduction

Traxgen simplifies the creation of realistic agent-based trajectories by allowing users to define detailed workflows and behaviors. Whether you are simulating customer support interactions, logistics flows, or other multi-agent scenarios, Traxgen ensures reproducibility and flexibility.

This page contains all information needed to install, configure, and use Traxgen effectively, with examples to help you get started quickly.

---

## Features

- **Modular framework** for trajectory generation that can be extended or customized.
- **Multi-agent support**, enabling complex interactions among agents.
- **Configurable simulation parameters** to model real-world scenarios.
- **Export options** include standard formats like JSON for interoperability with other tools.
- **Flexible trajectory styles**, accommodating different evaluation ecosystems.

---

## Installation

Install Traxgen via pip:

```bash
pip install traxgen
```

---

## Usage

Below is a minimal example to generate and save trajectories:

```python
from traxgen import generate_trajectories

# Sample input data
customer_data = [
    {"customer_id": 12345, "name": "Alice", "payment_method": "Card"},
    {"customer_id": 67890, "name": "Bob", "payment_method": "Cash"}
]

# Routine definitions (example JSON loaded into Python objects)
import json
routine_data = {
    "book_train": json.load(open("routine_data/book_train.json")),
    "submit_time_off": json.load(open("routine_data/submit_time_off.json"))
}

# Generate trajectories in 'traxgen' style and save to file
trajectories = generate_trajectories(
    customer_data=customer_data,
    routine_data=routine_data,
    id_field="customer_id",
    trajectory_format="traxgen",
    output_path="output/trajectories.json",
    output_mode="trajectory_only"
)

print("Generated trajectories:", trajectories)
```

---


## Trajectory Types Support

Traxgen supports multiple trajectory output styles. Choose the one that best fits your evaluation pipeline.

| Trajectory Type         | Description                                                                                   |
|-------------------------|-----------------------------------------------------------------------------------------------|
| **Traxgen Style**       | Captures agent name and tool calls with arguments in a nested list format.                   |
| **Tool Only**           | Minimalistic, listing only the sequence of tool call names.                                   |
| **Google Style**        | Compatible with Google's Vertex AI evaluation service, using dictionaries for tool calls.    |
| **LangChain Tool Style**| Format designed for the LangChain tool evaluation ecosystem.                                  |

---

### Traxgen Style

```json
[["agent: orchestrator",
    "tool: ask_for_order_id()",
    "tool: get_order_status(order_id=63920)",
    "tool: return_order_status(order_status=Delivered)",
    "tool: close_case(order_id=63920)"]]
```

---

### Tool Only

```plaintext
['ask_for_order_id', 'get_order_status', 'return_order_status', 'close_case']
```

---

### Google Style

```plaintext
[[{'tool_name': 'ask_for_order_id', 'tool_input': {}},
  {'tool_name': 'get_order_status', 'tool_input': {'order_id': 63920}},
  {'tool_name': 'return_order_status', 'tool_input': {'order_status': 'Delivered'}},
  {'tool_name': 'close_case', 'tool_input': {'order_id': 63920}}]]
```

---

### LangChain Tool Style

```json
[
  { "role": "assistant", "tool_calls": [{ "name": "ask_for_order_id", "arguments": {} }]},
  { "role": "assistant", "tool_calls": [{ "name": "get_order_status", "arguments": { "order_id": 63920 }}]},
  { "role": "assistant", "tool_calls": [{ "name": "return_order_status", "arguments": { "order_status": "Delivered" }}]},
  { "role": "assistant", "tool_calls": [{ "name": "close_case", "arguments": { "order_id": 63920 }}]}
]
```

---

## Main Functions

### `generate_trajectories(...)`

Generates user-specific trajectories based on an input sequence of agents and a defined routine.

**Arguments:**

- `customer_data` (list of dict): Customer records to generate trajectories for.
- `routine_data` (dict): Maps routine names to JSON objects defining workflows.
- `id_field` (str): Key to identify each customer (default: `'customer_id'`).
- `trajectory_format` (str or list): Output style(s) (one of `"traxgen"`, `"tool_only"`, `"google"`, `"langchain"`).
- `output_path` (str, optional): File path to save generated trajectories.
- `output_mode` (str): `"trajectory_only"` (default) or `"data_and_trajectory"`.
- `external_data` (dict, optional): Additional data sources in JSON format.
- `enable_visualization` (bool): If `True`, visualize trajectories (default: `False`).

**Returns:**  
- If `output_mode='trajectory_only'`: List of generated trajectories.
- If `output_mode='data_and_trajectory'`: customer_data with ground truth trajectory field.

Example (if `output_mode='trajectory_only'` and `trajectory_format = traxgen`):

```python
[
  [
    "agent: assistant",
    "tool: ask_for_order_id()",
    "tool: get_order_status(order_id=63920)",
    "tool: return_order_status(order_status=Delivered)",
    "tool: close_case(order_id=63920)"
  ],
  ...
]
```
---

### `get_required_fields(routine_data)`

Extracts a list of required fields from the provided routines, ensuring correct data alignment before trajectory generation.

**Arguments:**

- `routine_data` (dict): Maps routine names to JSON objects defining workflows.

**Returns:**  
A list of required field names such as:

```python
['agent_sequence', 'field1', 'field2', ...]
```

---

### `generate_field_template(required_fields)`
Creates a template dictionary defining distributions or generators for each required field. Useful for setting up synthetic data sampling workflows.

**Arguments:**

- `required_fields` (list): List of required fields names. 

**Returns:** 
A dictionary mapping fields to sampling instructions. Example:

```json
{
  "customer_id": { "random_int(1000, 9999)": 1.0 },
  "payment_method": { "Card": 0.7, "Cash": 0.3 }
}
```

---

### `generate_user_profiles(...)`
Generates synthetic customer profiles by sampling from field distributions.

**Arguments:**
- `fields` (list): List of required field names.
- `field_distributions` (dict): Value distributions or generators for each field.
- `num_samples` (int): Number of synthetic profiles to generate.
- `write_to_file` (bool): If `True`, save profiles to disk.
- `output_path` (str, optional): File path to save generated profiles.
  
**Returns:** 
A list of customer profile dictionaries. Example: 
```plaintext
[
  {
    "customer_id": 1234,
    "payment_method": "Card",
    ...
  },
  {
    "customer_id": 5678,
    "payment_method": "Cash",
    ...
  }
]
```


## Example Inputs

### `customer_data`

`customer_data` should be a JSON array (list) of customer dictionaries, for example:

```json
[
  {
    "customer_id": 12345,
    "name": "Alice",
    "address": "123 Main St",
    "payment_method": "Card"
  },
  {
    "customer_id": 67890,
    "name": "Bob",
    "address": "456 Oak Ave",
    "payment_method": "Cash"
  }
]
```

### `routine_data`
`routine_data` is a dictionary mapping routine names to JSON objects defining agent workflows. Example:

```python
import json

routine_data = {
    "book_train": json.load(open("routine_data/book_train.json")),
    "submit_time_off": json.load(open("routine_data/submit_time_off.json"))
}
```

## Routine JSON Files Explained

The routine JSON files define the behavior and workflow of your agents. Each routine JSON consists of four main components:

### `agent`
The `agent` field defines the unique identifier or name of the routine.

### `steps`

- This is an **ordered list** of *all possible* tool calls the routine might execute.
- Each step includes the tool call syntax with parameters and expected output variables.
- We list **all potential steps**, even if some won't be used in every individual trajectory.
- Parameters are mapped to data locations (e.g., customer data or extra inputs).

**Example snippet:**

```json
"steps": [
  "ask_for_basic_flight_details()",
  "get_customer_preferences(customer_id = customer_id)",
  "search_regular_flights(origin = user_provided_info['origin'], destination = user_provided_info['destination'], ...)",
  "create_booking(flight_number = user_provided_info['flight_number'])"
]
```

### `soft_ordering`

- A list of lists where each inner list contains tool call names (without parameters).
- Tool calls inside each inner list can execute in **any order**, enabling multiple valid trajectories by permuting calls.
- For example, two tools means 2! = 2 possible orders; combining groups multiplies permutations.

**Example snippet:**

```json
"soft_ordering": [
  ["add_special_services", "notify_airport_ground_team"],
  ["search_regular_flights", "search_priority_flights"]
]
```

This means:

- `add_special_services` and `notify_airport_ground_team` can happen in any order.
- `search_regular_flights` and `search_priority_flights` can also happen in any order.
- Combining these yields 4 possible valid orderings.


### `conditionals`
Controls which steps execute based on customer data or previous tool outputs.

Each entry follows this structure:

```plaintext
{
  "if": [
    { "field": ..., "operator": ..., "value": ... }
  ],
  "then": [
    { "action": ..., "target": ... }
  ],
  "else": [
    { "action": ..., "target": ... }
  ]
}
```
- The `if` block contains one or more condition objects using a `field`, an `operator`, and a `value`. The `field` references a key in the client data or an external data source provided to the routine (such as API output) whose value is evaluated at runtime.
- The `then` block defines what to do when the condition is met. The `target` can be one individual tool call or a list of tool calls.
- The `else` block (optional) defines what to do when the condition is not met. The `target` can be one individual tool call or a list of tool calls.
- Each `then` or `else` contains one or more {action, target} pairs.


You can also nest conditions using `all_of` or `any_of` as follows:

```plaintext
{
  "conditionals": [
    {
      "if": [{ "all_of": [
        { "field": ..., "operator": ..., "value": ... },
        { "field": ..., "operator": ..., "value": ... }
      ]}],
      "then": [{ "action": ..., "target": ... }],
      "else": [{ "action": ..., "target": ... }]
    }
  ]
}
```

### Supported Operators

Each condition in the `if` block must specify an `operator`. The following operators are supported:

| Operator        | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `==`           | Equal to                                                                    |
| `!=`           | Not equal to                                                                |
| `>`            | Greater than (for numbers only)                                             |
| `<`            | Less than (for numbers only)                                                |
| `>=`           | Greater than or equal to (for numbers only)                                 |
| `<=`           | Less than or equal to (for numbers only)                                    |
| `in`           | Check if `field` is in `value` (e.g., list or set)          |
| `not in`       | Check if `field` is **not** in `value`                      |
| `contains`     | Check if `value` is a substring/item in `field`             |
| `not contains` | Check if `value` is **not** a substring/item in `field`     |
| `not`          | Synonym for `!=`                                                            |



### Common Actions in Conditionals

Within the `conditionals` section, you control the workflow by specifying actions to take when conditions are met or not met. Supported actions are:

| Action              | Description                                                                                       |
|---------------------|-------------------------------------------------------------------------------------------------|
| `skip`              | Ignore (skip) the specified tool call(s) for this case if the condition is met.                 |
| `end_after`         | End the workflow immediately after executing the specified tool call.                           |
| `override_trajectory` | Ignore all other logic and conditionals for this case; use the specified trajectory exactly.   |
| `override_params`   | Change the parameters passed to a tool call for this case. All parameters must be explicitly provided. |


### Example of a Full Routine

``` json
{
  "agent": "account_suspension_request",
  "steps": [
    "ask_suspension_type() -> [suspension_type]",
    "ask_suspension_reason() -> [reason]",
    "get_user_status(employee_id = employee_id) -> [status]",
    "notify_already_suspended(employee_id = employee_id)",
    "ask_reactivation_date() -> [reactivation_date]",
    "suspend_account(employee_id = employee_id, type = user_provided_info['suspension_type'], reason = user_provided_info['suspension_reason'])",
    "send_suspension_confirmation(employee_id = employee_id)",
    "close_case(suspension_id = suspension['suspension_id'])"
  ],
  "soft_ordering": [
    ["ask_suspension_type", "ask_suspension_reason"]
  ],
  "conditionals": [
    {
      "if": [
        {
          "field": "suspension['suspension_status']",
          "operator": "==",
          "value": "suspended"
        }
      ],
      "then": [
        {
          "action": "end_after",
          "target": "notify_already_suspended"
        }
      ],
      "else": [
        {
          "action": "skip",
          "target": "notify_already_suspended"
        }
      ]
    },
    {
      "if": [
        {
          "field": "user_provided_info['suspension_type']",
          "operator": "!=",
          "value": "temporary"
        }
      ],
      "then": [
        {
          "action": "skip",
          "target": "ask_reactivation_date"
        }],
      "else": [
        {
          "action": "override_params",
          "target": "suspend_account",
          "params": {
            "employee_id": "employee_id",
            "type": "user_provided_info['suspension_type']",
            "reason": "user_provided_info['suspension_reason']",
            "reactivation_date": "user_provided_info['reactivation_date']"
          }
        }
      ]
    }
  ]
}
```

---

### License

This project is licensed under the MIT License. 
