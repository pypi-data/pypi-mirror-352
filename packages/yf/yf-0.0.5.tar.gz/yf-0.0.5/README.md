# yf
Diagnosing dictionaries

To install:	```pip install yf```

## Overview
The `yf` package provides a suite of tools designed to assist in the diagnosis and inspection of dictionaries, particularly useful for debugging and data validation in Python applications. It includes functions for printing dictionary key paths, validating dictionary contents against specified criteria, comparing dictionaries, and generating example dictionaries from a list of dictionaries.

## Features

### Key Path Printing
- `print_key_paths(d)`: Prints all key paths in a dictionary.
- `print_key_paths_and_val_peep(d, n_characters_in_val_peep=15)`: Prints key paths along with a preview of their values, truncated to a specified number of characters.

### Dictionary Validation
- `validate_kwargs(kwargs_to_validate, validation_dict, validation_funs=base_validation_funs, all_kwargs_should_be_in_validation_dict=False, ignore_misunderstood_validation_instructions=False)`: Validates a dictionary of keyword arguments (`kwargs_to_validate`) against a set of rules defined in `validation_dict` using the functions specified in `validation_funs`.

### Dictionary Comparison
- `are_equal_on_common_keys(dict1, dict2)`: Checks if two dictionaries are equal based on the keys they both share.
- `first_difference_on_common_keys(dict1, dict2, key_path_so_far=None)`: Finds the first key path where two dictionaries differ.

### Dictionary Analysis
- `json_size_of_fields(d)`: Returns a dictionary where the values are the sizes of the JSON string representations of the corresponding values in the input dictionary.
- `example_dict_from_dict_list(dict_list, recursive=False)`: Generates an example dictionary that includes at least one occurrence of each key found in a list of dictionaries.
- `dict_of_types_of_dict_values(x, recursive=False)`: Returns a dictionary describing the types of the values in the input dictionary, optionally doing so recursively.

## Usage Examples

### Printing Key Paths
```python
d = {'a': {'b': {'c': 1}}}
print_key_paths(d)
```

### Validating Keyword Arguments
```python
validation_rules = {
    'age': {'be at least': 18},
    'name': {'be a': str}
}
kwargs = {'age': 20, 'name': 'John'}
validate_kwargs(kwargs, validation_rules)
```

### Comparing Dictionaries
```python
dict1 = {'a': 1, 'b': 2}
dict2 = {'a': 1, 'b': 3}
are_equal_on_common_keys(dict1, dict2)  # Returns False
first_difference_on_common_keys(dict1, dict2)  # Returns ['b']
```

### Analyzing Dictionary Content
```python
d = {'name': 'Alice', 'data': [1, 2, 3]}
json_size_of_fields(d)
```

### Generating Example Dictionary from List
```python
dict_list = [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}]
example_dict_from_dict_list(dict_list)
```

## Function Documentation
Each function in the `yf` package is documented with Python docstrings, providing a detailed description of its purpose, parameters, return values, and usage examples. This documentation is accessible via the Python help system or by reading the source code directly.

## Installation
To install the `yf` package, use the following pip command:
```bash
pip install yf
```

This package is a powerful tool for developers working with complex data structures in Python, providing robust functionalities for dictionary diagnostics and validation.