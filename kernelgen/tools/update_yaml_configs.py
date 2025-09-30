#!/usr/bin/env python3
"""
Update all rocBLAS YAML configuration files to handle build compatibility issues.
This script can disable hipblaslt dependency or adjust other build parameters as needed.
"""

import os
import yaml
from pathlib import Path
import argparse

def update_yaml_configs(kernelgen_dir="kernelgen", disable_hipblaslt=False, update_arch=None):
    """
    Update YAML configuration files with compatibility fixes.

    Args:
        kernelgen_dir: Directory containing YAML files
        disable_hipblaslt: Whether to add --no-hipblaslt flag to build commands
        update_arch: Update architecture if specified
    """

    yaml_files = list(Path(kernelgen_dir).glob("rocblas_*.yaml"))

    if not yaml_files:
        print(f"No rocBLAS YAML files found in {kernelgen_dir}")
        return

    print(f"Updating {len(yaml_files)} YAML configuration files...")

    updated_count = 0

    for yaml_file in yaml_files:
        try:
            # Load the YAML file
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)

            modified = False

            # Update compile commands
            if 'compile_command' in config:
                new_compile_commands = []
                for cmd in config['compile_command']:
                    new_cmd = cmd

                    # Add --no-hipblaslt flag if requested
                    if disable_hipblaslt and '--no-hipblaslt' not in cmd:
                        if './install.sh' in cmd:
                            new_cmd = cmd + ' --no-hipblaslt'
                            modified = True
                            print(f"  Added --no-hipblaslt to compile command in {yaml_file.name}")

                    # Update architecture if specified
                    if update_arch:
                        if '--architecture' in cmd:
                            # Replace existing architecture
                            import re
                            new_cmd = re.sub(r'--architecture\s+\w+', f'--architecture {update_arch}', new_cmd)
                            modified = True
                            print(f"  Updated architecture to {update_arch} in {yaml_file.name}")
                        elif './install.sh' in cmd and '--architecture' not in cmd:
                            # Add architecture if missing
                            new_cmd = cmd.replace('./install.sh', f'./install.sh --architecture {update_arch}')
                            modified = True
                            print(f"  Added architecture {update_arch} to {yaml_file.name}")

                    new_compile_commands.append(new_cmd)

                if modified:
                    config['compile_command'] = new_compile_commands

            # Update performance commands if needed
            if 'performance_command' in config:
                new_perf_commands = []
                for cmd in config['performance_command']:
                    new_cmd = cmd

                    # Fix rocprof-compute path issues
                    if 'rocprof-compute' in cmd and '/opt/rocm/bin/rocprof-compute' not in cmd:
                        new_cmd = cmd.replace('rocprof-compute', '/opt/rocm/bin/rocprof-compute')
                        modified = True
                        print(f"  Fixed rocprof-compute path in {yaml_file.name}")

                    new_perf_commands.append(new_cmd)

                if modified:
                    config['performance_command'] = new_perf_commands

            # Write the updated config back to file if modified
            if modified:
                with open(yaml_file, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False,
                             allow_unicode=True, width=1000)
                updated_count += 1

        except Exception as e:
            print(f"Error updating {yaml_file}: {e}")

    print(f"Updated {updated_count} YAML configuration files")

    return updated_count

def main():
    parser = argparse.ArgumentParser(
        description="Update rocBLAS YAML configs for build compatibility"
    )
    parser.add_argument(
        '--disable-hipblaslt',
        action='store_true',
        help='Add --no-hipblaslt flag to compile commands'
    )
    parser.add_argument(
        '--architecture',
        help='Update GPU architecture (e.g., gfx942, gfx90a)'
    )
    parser.add_argument(
        '--kernelgen-dir',
        default='kernelgen',
        help='Directory containing YAML files (default: kernelgen)'
    )

    args = parser.parse_args()

    if not args.disable_hipblaslt and not args.architecture:
        print("No updates specified. Use --disable-hipblaslt or --architecture")
        print("Example: python update_yaml_configs.py --disable-hipblaslt")
        return

    # Perform updates
    updated = update_yaml_configs(
        kernelgen_dir=args.kernelgen_dir,
        disable_hipblaslt=args.disable_hipblaslt,
        update_arch=args.architecture
    )

    if updated > 0:
        print(f"? Successfully updated {updated} YAML configuration files")

        if args.disable_hipblaslt:
            print("? All compile commands now include --no-hipblaslt flag")

        if args.architecture:
            print(f"? All compile commands now use architecture: {args.architecture}")

    else:
        print("i  No files needed updating")

if __name__ == "__main__":
    main()
