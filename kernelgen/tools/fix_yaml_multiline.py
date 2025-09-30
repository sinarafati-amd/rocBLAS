#!/usr/bin/env python3
"""
Fix multiline YAML commands that are incorrectly formatted.
This script joins multiline commands into single lines and optionally
disables correctness testing for faster iteration.
"""

import yaml
from pathlib import Path
import sys
import argparse

def fix_multiline_commands(yaml_file: Path, disable_correctness: bool = False) -> bool:
    """
    Fix multiline commands in YAML file.

    Args:
        yaml_file: Path to YAML file
        disable_correctness: If True, comment out correctness commands

    Returns:
        True if changes were made
    """
    try:
        with open(yaml_file, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)

        changed = False

        # Fix performance_command (join multiline)
        if 'performance_command' in data:
            new_perf_cmds = []
            for cmd in data['performance_command']:
                if isinstance(cmd, str):
                    # Join lines and remove extra whitespace
                    fixed_cmd = ' '.join(cmd.split())
                    new_perf_cmds.append(fixed_cmd)
                    if fixed_cmd != cmd.strip():
                        changed = True
            data['performance_command'] = new_perf_cmds

        # Handle correctness_command
        if disable_correctness and 'correctness_command' in data:
            # Replace with echo command
            data['correctness_command'] = ['echo "Correctness testing disabled for faster iteration"']
            changed = True

        # Write back with proper formatting
        if changed:
            with open(yaml_file, 'w') as f:
                # Use custom dumper to preserve formatting
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=1000)
            return True

        return False

    except Exception as e:
        print(f"  ? Error processing {yaml_file.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Fix YAML multiline commands')
    parser.add_argument('--disable-correctness', action='store_true',
                       help='Disable correctness testing for faster iteration')
    parser.add_argument('--yaml-dir', default='kernelgen',
                       help='Directory containing YAML files')
    args = parser.parse_args()

    # Get YAML directory
    if Path(args.yaml_dir).is_absolute():
        yaml_dir = Path(args.yaml_dir)
    else:
        script_dir = Path(__file__).parent
        yaml_dir = script_dir.parent / args.yaml_dir

    if not yaml_dir.exists():
        yaml_dir = Path(args.yaml_dir)

    print(f"Fixing YAML files in: {yaml_dir}")
    if args.disable_correctness:
        print("  -> Disabling correctness testing")
    print(f"{'='*60}")

    # Find all rocblas_*.yaml files
    yaml_files = sorted(yaml_dir.glob('rocblas_*.yaml'))

    if not yaml_files:
        print(f"No rocblas_*.yaml files found in {yaml_dir}")
        return 1

    print(f"Found {len(yaml_files)} YAML files to process...\n")

    fixed_count = 0

    for yaml_file in yaml_files:
        result = fix_multiline_commands(yaml_file, args.disable_correctness)
        if result:
            print(f"? Fixed: {yaml_file.name}")
            fixed_count += 1
        else:
            print(f"?  Skipped: {yaml_file.name} (no changes needed)")

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Fixed: {fixed_count}")
    print(f"  Total: {len(yaml_files)}")

    if fixed_count > 0:
        print(f"\n? Successfully updated {fixed_count} YAML file(s)!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
