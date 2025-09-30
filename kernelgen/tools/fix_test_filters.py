#!/usr/bin/env python3
"""
Fix test filters in rocBLAS YAML files to use correct lowercase patterns.

This script updates all rocblas_*.yaml files in the kernelgen directory to use
the correct test filter patterns that match rocBLAS test naming conventions.
"""

import yaml
from pathlib import Path
import sys

def fix_yaml_test_filter(yaml_file: Path) -> bool:
    """
    Fix the test filter in a single YAML file.

    Args:
        yaml_file: Path to the YAML file

    Returns:
        True if changes were made, False otherwise
    """
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        # Extract function name from filename
        # e.g., rocblas_spmv.yaml -> spmv
        func_name = yaml_file.stem.replace('rocblas_', '')

        # Check if correctness_command exists
        if 'correctness_command' not in data:
            print(f"  ?  No correctness_command found in {yaml_file.name}")
            return False

        changed = False
        for i, cmd in enumerate(data['correctness_command']):
            if '--gtest_filter=' in cmd:
                # Build the old pattern (what we're looking for)
                old_patterns = [
                    f'*{func_name.upper()}.*',  # SPMV.* pattern
                    f'*{func_name.upper().replace("_", "_")}.*',  # Handle underscores
                ]

                # Build the new pattern (what we want)
                new_pattern = f'{func_name.lower()}*:-*stress*'

                # Check if we need to update
                needs_update = False
                for old_pattern in old_patterns:
                    if old_pattern in cmd:
                        needs_update = True
                        # Replace the pattern
                        data['correctness_command'][i] = cmd.replace(
                            f'--gtest_filter="{old_pattern}"',
                            f'--gtest_filter="{new_pattern}"'
                        ).replace(
                            f'--gtest_filter={old_pattern}',
                            f'--gtest_filter={new_pattern}'
                        )
                        print(f"  ? Updated filter: {old_pattern} -> {new_pattern}")
                        changed = True
                        break

                if not needs_update and '--gtest_filter=' in cmd:
                    # Already has a filter, check if it's already correct
                    if func_name.lower() in cmd.lower():
                        print(f"  ?  Filter already correct in {yaml_file.name}")
                    else:
                        print(f"  ?  Unknown filter pattern in {yaml_file.name}: {cmd}")

        # Write back if changed
        if changed:
            with open(yaml_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            return True

        return False

    except Exception as e:
        print(f"  ? Error processing {yaml_file.name}: {e}")
        return False

def main():
    """Main function to fix all YAML files."""
    # Get the kernelgen directory
    script_dir = Path(__file__).parent
    kernelgen_dir = script_dir.parent

    print(f"Fixing test filters in: {kernelgen_dir}")
    print(f"{'='*60}")

    # Find all rocblas_*.yaml files
    yaml_files = sorted(kernelgen_dir.glob('rocblas_*.yaml'))

    if not yaml_files:
        print("No rocblas_*.yaml files found!")
        return 1

    print(f"Found {len(yaml_files)} YAML files to check...\n")

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for yaml_file in yaml_files:
        print(f"Processing: {yaml_file.name}")
        result = fix_yaml_test_filter(yaml_file)
        if result:
            fixed_count += 1
        elif result is False:
            skipped_count += 1
        else:
            error_count += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Fixed: {fixed_count}")
    print(f"  Skipped (already correct or no filter): {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(yaml_files)}")

    if fixed_count > 0:
        print(f"\n? Successfully updated {fixed_count} YAML file(s)!")
        print(f"\nNext steps:")
        print(f"  1. Validate: python3 kernelgen/tools/validate_yaml_configs.py")
        print(f"  2. Test a filter: timeout 30 build/release-debug/clients/staging/rocblas-test --gtest_filter='spmv*'")
    else:
        print(f"\n?  All files already have correct filters or no changes needed.")

    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
