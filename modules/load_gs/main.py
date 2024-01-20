#!/usr/bin/env python3

import libcalamares
import json

gs = libcalamares.globalstorage
gs_file = '/iso/nix-cfg/calamares.gs'

with open(filename, 'r') as file:
    data_with_types = json.load(file)

for key, item in data_with_types.items():
    value = item["value"]
    value_type = item["type"]

    # Convert the value back to its original type
    if value_type == "bool":
        gs.insert(key, bool(value))
    elif value_type == "NoneType":
        gs.insert(key, None)
    elif value_type == "int":
        gs.insert(key, int(value))
    elif value_type == "float":
        gs.insert(key, float(value))
    elif value_type == "list" or value_type == "dict":
        # Assuming the list or dict is already in the correct format
        gs.insert(key, value)
    elif value_type == "str":
        gs.insert(key, value)
    else:
        # For any other type, insert the value as is
        gs.insert(key, value)
