#!/usr/bin/env python3
"""
Script to analyze YAML configuration files for rocBLAS kernelgen
Provides statistics and insights about the generated configurations
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict, Counter

def analyze_yaml_file(file_path: str) -> Dict:
    """Analyze a single YAML configuration file"""
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        return {'error': str(e)}
    
    analysis = {
        'filename': os.path.basename(file_path),
        'function_name': os.path.basename(file_path).replace('.yaml', '').replace('rocblas_', ''),
        'source_files_count': len(config.get('source_file_path', [])),
        'gen_files_count': len(config.get('gen_file_path', [])),
        'kernel_functions_count': len(config.get('target_kernel_functions', [])),
        'compile_commands_count': len(config.get('compile_command', [])),
        'correctness_commands_count': len(config.get('correctness_command', [])),
        'performance_commands_count': len(config.get('performance_command', [])),
        'source_files': config.get('source_file_path', []),
        'kernel_functions': config.get('target_kernel_functions', []),
        'blas_level': 'unknown'
    }
    
    # Determine BLAS level based on function name
    function_name = analysis['function_name'].lower()
    if any(blas1_func in function_name for blas1_func in ['asum', 'axpy', 'copy', 'dot', 'iamax', 'iamin', 'nrm2', 'rot', 'rotg', 'rotm', 'rotmg', 'scal', 'swap']):
        analysis['blas_level'] = 'BLAS1'
    elif any(blas2_func in function_name for blas2_func in ['gbmv', 'gemv', 'ger', 'hbmv', 'hemv', 'her', 'her2', 'hpmv', 'hpr', 'hpr2', 'sbmv', 'spmv', 'spr', 'spr2', 'symv', 'syr', 'syr2', 'tbmv', 'tbsv', 'tpmv', 'tpsv', 'trmv', 'trsv']):
        analysis['blas_level'] = 'BLAS2'
    elif any(blas3_func in function_name for blas3_func in ['dgmm', 'geam', 'gemm', 'hemm', 'her2k', 'herk', 'herkx', 'symm', 'syr2k', 'syrk', 'syrkx', 'trmm', 'trsm', 'trtri']):
        analysis['blas_level'] = 'BLAS3'
    elif 'ex' in function_name:
        analysis['blas_level'] = 'BLAS_EX'
    
    return analysis

def main():
    """Main analysis function"""
    kernelgen_dir = "kernelgen"
    
    if not os.path.exists(kernelgen_dir):
        print(f"Error: {kernelgen_dir} directory not found")
        return
    
    yaml_files = list(Path(kernelgen_dir).glob("*.yaml"))
    
    if not yaml_files:
        print("No YAML files found in kernelgen directory")
        return
    
    print(f"Analyzing {len(yaml_files)} YAML configuration files...")
    
    analyses = []
    blas_level_counts = Counter()
    total_source_files = 0
    total_kernel_functions = 0
    all_kernel_functions = set()
    all_source_files = set()
    
    for yaml_file in yaml_files:
        analysis = analyze_yaml_file(str(yaml_file))
        if 'error' in analysis:
            print(f"Error analyzing {yaml_file}: {analysis['error']}")
            continue
        
        analyses.append(analysis)
        blas_level_counts[analysis['blas_level']] += 1
        total_source_files += analysis['source_files_count']
        total_kernel_functions += analysis['kernel_functions_count']
        all_kernel_functions.update(analysis['kernel_functions'])
        all_source_files.update(analysis['source_files'])
    
    # Print summary statistics
    print(f"\n{'='*60}")
    print("Analysis Summary")
    print(f"{'='*60}")
    print(f"Total configuration files: {len(analyses)}")
    print(f"Total source files referenced: {len(all_source_files)}")
    print(f"Total unique kernel functions: {len(all_kernel_functions)}")
    print(f"Average source files per config: {total_source_files / len(analyses):.1f}")
    print(f"Average kernel functions per config: {total_kernel_functions / len(analyses):.1f}")
    
    # BLAS level distribution
    print(f"\nBLAS Level Distribution:")
    for level, count in blas_level_counts.most_common():
        print(f"  {level}: {count} functions")
    
    # Top kernel functions
    kernel_function_counts = Counter()
    for analysis in analyses:
        for kernel in analysis['kernel_functions']:
            kernel_function_counts[kernel] += 1
    
    print(f"\nTop 10 Most Common Kernel Functions:")
    for kernel, count in kernel_function_counts.most_common(10):
        print(f"  {kernel}: {count} functions")
    
    # Source file distribution
    source_file_counts = Counter()
    for analysis in analyses:
        for source_file in analysis['source_files']:
            source_file_counts[source_file] += 1
    
    print(f"\nTop 10 Most Referenced Source Files:")
    for source_file, count in source_file_counts.most_common(10):
        print(f"  {source_file}: {count} functions")
    
    # Functions with most kernel functions
    print(f"\nFunctions with Most Kernel Functions:")
    sorted_by_kernels = sorted(analyses, key=lambda x: x['kernel_functions_count'], reverse=True)
    for analysis in sorted_by_kernels[:10]:
        print(f"  {analysis['function_name']}: {analysis['kernel_functions_count']} kernels")
    
    # Functions with most source files
    print(f"\nFunctions with Most Source Files:")
    sorted_by_sources = sorted(analyses, key=lambda x: x['source_files_count'], reverse=True)
    for analysis in sorted_by_sources[:10]:
        print(f"  {analysis['function_name']}: {analysis['source_files_count']} files")

if __name__ == "__main__":
    main()
