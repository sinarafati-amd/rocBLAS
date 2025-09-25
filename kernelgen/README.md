# rocBLAS KernelGen

This directory contains tools and configurations for generating and optimizing rocBLAS kernels 

## Overview

The rocBLAS KernelGen system is designed to:
1. Analyze rocBLAS function implementations
2. Generate YAML configuration files for each function
3. Enable kernel-level performance analysis

## Directory Structure

```
kernelgen/
├── README.md                           # This file
├── tools/                              # Kernel generation tools
│   ├── generate_yaml_configs.py       # Main YAML generator
│   ├── patch_rocblas_and_build.sh     # Build script with patches
│   ├── patch_rocblas.py               # rocBLAS patching script
│   ├── generate_optimized_bench_commands.py  # AI bench optimizer
│   ├── rocblas-bench_context.py        # AI prompt template
│   ├── validate_yaml_configs.py        # YAML validation
│   └── analyze_yaml_configs.py         # YAML analysis
└── *.yaml                              # Generated YAML configs (one per function)
```

## YAML Configuration Format

Each YAML file contains:

```yaml
source_file_path:          # List of source files to analyze
  - library/src/blas1/rocblas_axpy.cpp
  - library/src/blas1/rocblas_axpy.hpp
gen_file_path:            # Files to generate (usually same as source)
target_kernel_functions:  # List of kernel functions to optimize
  - rocblas_axpy_kernel
  - rocblas_axpy_impl
compile_command:         # Build command
  - ./install.sh --architecture gfx942 --clients --relwithdebinfo
correctness_command:     # Test command
  - build/release-debug/clients/staging/rocblas-test --gtest_filter="*AXPY.*"
performance_command:     # Benchmark command with profiling
  - rocprof-compute profile -n kernelgen --path rocprof_compute_profile --no-roof --join-type kernel -b SQ -b TCP -b TCC -- build/release-debug/clients/staging/rocblas-bench -f axpy -r s -m 3000 -n 3000 --lda 3000 --iters 2
  - rocprof-compute analyze --path rocprof_compute_profile -b 2
```

## Usage

### 1. Generate YAML Configurations

```bash
cd /root/Sina/rocBLAS
python3 kernelgen/tools/generate_yaml_configs.py
```

This will:
- Scan all BLAS1, BLAS2, BLAS3, and BLAS_EX functions
- Generate YAML configs for each function
- Analyze dependencies and kernel functions
- Create optimized file lists for LLM processing

### 2. Patch rocBLAS for Kernel Generation

```bash
cd /root/Sina/rocBLAS
python3 kernelgen/tools/patch_rocblas.py
```

This will:
- Add kernel generation flags to CMake
- Patch kernel files with profiling markers
- Enable kernel-level analysis

### 3. Build rocBLAS with Patches

```bash
cd /root/Sina/rocBLAS
bash kernelgen/tools/patch_rocblas_and_build.sh
```

This will:
- Apply all patches
- Build rocBLAS with kernel generation support
- Install dependencies

### 4. Optimize Benchmark Commands (Optional)

Requires Claude API key in `kernelgen/tools/claude_api_key.txt`:

```bash
cd /root/Sina/rocBLAS
python3 kernelgen/tools/generate_optimized_bench_commands.py
```

This will:
- Use AI to optimize benchmark parameters
- Generate better performance test commands
- Update YAML files with optimized commands

### 5. Validate Configurations

```bash
cd /root/Sina/rocBLAS
python3 kernelgen/tools/validate_yaml_configs.py
```

### 6. Analyze Configurations

```bash
cd /root/Sina/rocBLAS
python3 kernelgen/tools/analyze_yaml_configs.py
```

## Function Categories

The system automatically categorizes functions:

- **BLAS1**: Level 1 BLAS operations (axpy, dot, scal, etc.)
- **BLAS2**: Level 2 BLAS operations (gemv, ger, symv, etc.)
- **BLAS3**: Level 3 BLAS operations (gemm, syrk, trmm, etc.)
- **BLAS_EX**: Extended precision operations
- **Auxiliary**: Utility functions

## Kernel Function Detection

The system identifies:
1. **Host-side template functions**: `rocblas_*_impl`, `rocblas_*_template`
2. **GPU kernel functions**: Functions marked with `ROCBLAS_KERNEL`, `__global__`, or `__launch_bounds__`
3. **Algorithm-specific kernels**: Filtered to prevent cross-contamination

## Performance Analysis

Each YAML config includes:
- **Compile command**: Builds rocBLAS with profiling support
- **Correctness command**: Runs unit tests for the function
- **Performance command**: Runs benchmarks with rocprof-compute profiling

## AI Optimization

The AI optimization system:
- Analyzes function implementations
- Generates optimal benchmark parameters
- Considers matrix sizes, data types, and iteration counts
- Creates commands that stress GPU kernels effectively

## Dependencies

- Python 3.6+
- PyYAML
- rocBLAS source code
- rocprof-compute (for profiling)
- Claude API key (for AI optimization)

## Notes

- YAML files are generated automatically from source code analysis
- Kernel functions are filtered to remove generic utilities
- Source files are prioritized by importance and relevance
- Cross-algorithm contamination is prevented through categorization
- Maximum file limits prevent LLM context overflow
