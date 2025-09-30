#!/usr/bin/env python3
"""
Fix compile commands in YAML files to use correct flag syntax.
Changes --no-hipblaslt to --no_hipblaslt (underscore instead of dash).
"""

import yaml
from pathlib import Path
import sys

def fix_compile_command(yaml_file: Path) -> bool:
    """Fix the compile command in a YAML file."""
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        if 'compile_command' not in data:
            return False

        changed = False
        for i, cmd in enumerate(data['compile_command']):
            if '--no-hipblaslt' in cmd:
                data['compile_command'][i] = cmd.replace('--no-hipblaslt', '--no_hipblaslt')
                changed = True

        if changed:
            with open(yaml_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=1000)
            return True

        return False

    except Exception as e:
        print(f"  ? Error: {yaml_file.name}: {e}")
        return False

def main():
    script_dir = Path(__file__).parent
    kernelgen_dir = script_dir.parent

    print(f"Fixing compile commands in: {kernelgen_dir}")
    print(f"Changing: --no-hipblaslt -> --no_hipblaslt")
    print(f"{'='*60}")

    yaml_files = sorted(kernelgen_dir.glob('rocblas_*.yaml'))

    if not yaml_files:
        print(f"No YAML files found")
        return 1

    print(f"Found {len(yaml_files)} YAML files...\n")

    fixed = 0
    for yaml_file in yaml_files:
        if fix_compile_command(yaml_file):
            print(f"? Fixed: {yaml_file.name}")
            fixed += 1

    print(f"\n{'='*60}")
    print(f"Fixed {fixed}/{len(yaml_files)} files")

    return 0

if __name__ == "__main__":
    sys.exit(main())
