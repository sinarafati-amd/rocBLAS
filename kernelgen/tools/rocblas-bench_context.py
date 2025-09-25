#!/usr/bin/env python3
"""
Context template for rocBLAS benchmark optimization using Claude AI
"""

template = f'''
You are an expert in GPU computing and rocBLAS optimization. I need you to generate an optimized rocblas-bench command for the FUNCTION_NAME function.

Here is the implementation context:

FUNCTION_IMPLEMENTATION_CONTEXT

Based on this implementation, please generate an optimized rocblas-bench command that:

1. Uses appropriate matrix sizes that will stress the GPU kernels effectively
2. Chooses optimal data types (s, d, c, z) based on the function
3. Sets appropriate parameters like alpha, beta, lda, ldb, ldc
4. Uses reasonable iteration counts for performance measurement
5. Includes any special flags or options that would be beneficial for this specific function

The command should be in the format:
build/release-debug/clients/staging/rocblas-bench [OPTIONS]

Please provide ONLY the rocblas-bench command line, no explanations or additional text.

Consider the following guidelines:
- For BLAS1 functions: Use vector sizes that are large enough to show performance differences
- For BLAS2 functions: Use matrix-vector dimensions that stress memory bandwidth
- For BLAS3 functions: Use square matrices that are large enough to utilize GPU compute units
- For batched functions: Include appropriate batch sizes
- For complex functions: Use both real and complex data types when applicable
- For symmetric/Hermitian functions: Use appropriate uplo and side parameters

Focus on creating a command that will generate meaningful performance data for kernel optimization.
'''
