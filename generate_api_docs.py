#!/usr/bin/env python3
"""
Simple API documentation generator that converts the OpenAPI YAML to JSON
without requiring PyYAML. This is a basic YAML parser for our specific use case.
"""

import json
import re

def simple_yaml_to_json(yaml_content):
    """
    Very basic YAML to JSON converter for our OpenAPI spec.
    This is not a full YAML parser but handles our specific format.
    """
    lines = yaml_content.split('\n')
    result = {}
    stack = [result]
    indent_stack = [-1]
    
    for line in lines:
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        # Calculate indentation
        indent = len(line) - len(line.lstrip())
        
        # Handle list items
        if stripped.startswith('- '):
            # This is a list item
            while len(indent_stack) > 1 and indent <= indent_stack[-1]:
                stack.pop()
                indent_stack.pop()
            
            current = stack[-1]
            if not isinstance(current, list):
                # Convert to list if not already
                stack[-1] = []
                current = stack[-1]
            
            value = stripped[2:].strip()
            if ':' in value:
                # Object in list
                obj = {}
                current.append(obj)
                stack.append(obj)
                indent_stack.append(indent)
                key, val = value.split(':', 1)
                obj[key.strip()] = val.strip() if val.strip() else None
            else:
                # Simple value in list
                current.append(value)
            continue
        
        # Handle key-value pairs
        if ':' in stripped:
            # Pop stack if indentation decreased
            while len(indent_stack) > 1 and indent <= indent_stack[-1]:
                stack.pop()
                indent_stack.pop()
            
            current = stack[-1]
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if not value:
                # Empty value, probably has children
                current[key] = {}
                stack.append(current[key])
                indent_stack.append(indent)
            else:
                # Has value
                # Try to parse as appropriate type
                if value.lower() == 'true':
                    current[key] = True
                elif value.lower() == 'false':
                    current[key] = False
                elif value.lower() == 'null':
                    current[key] = None
                elif value.startswith('"') and value.endswith('"'):
                    current[key] = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    current[key] = value[1:-1]
                elif value.replace('.', '').replace('-', '').isdigit():
                    current[key] = float(value) if '.' in value else int(value)
                else:
                    current[key] = value
    
    return result

def generate_api_docs_json():
    """Generate api_docs.json from api_docs.yaml"""
    try:
        with open('api_docs.yaml', 'r') as f:
            yaml_content = f.read()
        
        # Simple conversion - for production use PyYAML
        json_data = simple_yaml_to_json(yaml_content)
        
        with open('api_docs.json', 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print("Generated api_docs.json from api_docs.yaml")
        return True
        
    except Exception as e:
        print(f"Error generating JSON docs: {e}")
        return False

if __name__ == '__main__':
    generate_api_docs_json()
