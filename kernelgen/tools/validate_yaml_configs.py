#!/usr/bin/env python3
"""
Script to validate YAML configuration files for rocBLAS kernelgen
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List

def validate_yaml_file(file_path: str) -> Dict[str, List[str]]:
    """
    Validate a single YAML configuration file.
    Returns a dictionary with 'errors' and 'warnings' lists.
    """
    errors = []
    warnings = []
    
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        errors.append(f"Failed to parse YAML: {e}")
        return {'errors': errors, 'warnings': warnings}
    
    # Check required fields
    required_fields = ['source_file_path', 'gen_file_path', 'target_kernel_functions', 
                      'compile_command', 'correctness_command', 'performance_command']
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
        elif not config[field]:
            warnings.append(f"Empty field: {field}")
    
    # Validate source files exist
    if 'source_file_path' in config:
        for file_path in config['source_file_path']:
            if not os.path.exists(file_path):
                warnings.append(f"Source file does not exist: {file_path}")
    
    # Validate gen files exist
    if 'gen_file_path' in config:
        for file_path in config['gen_file_path']:
            if not os.path.exists(file_path):
                warnings.append(f"Gen file does not exist: {file_path}")
    
    # Validate commands
    if 'compile_command' in config:
        for cmd in config['compile_command']:
            if not cmd.strip():
                warnings.append("Empty compile command")
    
    if 'correctness_command' in config:
        for cmd in config['correctness_command']:
            if not cmd.strip():
                warnings.append("Empty correctness command")
    
    if 'performance_command' in config:
        for cmd in config['performance_command']:
            if not cmd.strip():
                warnings.append("Empty performance command")
    
    return {'errors': errors, 'warnings': warnings}

def main():
    """Main validation function"""
    kernelgen_dir = "kernelgen"
    
    if not os.path.exists(kernelgen_dir):
        print(f"Error: {kernelgen_dir} directory not found")
        return
    
    yaml_files = list(Path(kernelgen_dir).glob("*.yaml"))
    
    if not yaml_files:
        print("No YAML files found in kernelgen directory")
        return
    
    print(f"Validating {len(yaml_files)} YAML configuration files...")
    
    total_errors = 0
    total_warnings = 0
    
    for yaml_file in yaml_files:
        print(f"\nValidating: {yaml_file}")
        
        result = validate_yaml_file(str(yaml_file))
        errors = result['errors']
        warnings = result['warnings']
        
        if errors:
            print(f"  ❌ Errors ({len(errors)}):")
            for error in errors:
                print(f"    - {error}")
            total_errors += len(errors)
        
        if warnings:
            print(f"  ⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"    - {warning}")
            total_warnings += len(warnings)
        
        if not errors and not warnings:
            print(f"  ✅ Valid")
    
    print(f"\n{'='*50}")
    print("Validation Summary")
    print(f"{'='*50}")
    print(f"Total files: {len(yaml_files)}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")
    
    if total_errors == 0:
        print("✅ All files are valid!")
    else:
        print("❌ Some files have errors that need to be fixed")

if __name__ == "__main__":
    main()
