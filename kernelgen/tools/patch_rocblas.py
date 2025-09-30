#!/usr/bin/env python3
"""
Script to patch rocBLAS for kernel generation
This script adds necessary modifications to enable kernel generation and profiling
"""

import os
import re
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = f"{file_path}.backup"
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")

def patch_cmake_file():
    """Patch CMakeLists.txt to enable kernel generation and fix hipblaslt version"""
    cmake_file = "CMakeLists.txt"
    if not os.path.exists(cmake_file):
        print(f"Warning: {cmake_file} not found")
        return

    backup_file(cmake_file)

    with open(cmake_file, 'r') as f:
        content = f.read()

    # Fix hipblaslt version requirement - make it more flexible
    if "HIPBLASLT_VERSION 1.0.0" in content:
        print("Fixing hipblaslt version requirement...")
        content = content.replace(
            'set( HIPBLASLT_VERSION 1.0.0 CACHE STRING "The version of HipBLASLt to be used" )',
            'set( HIPBLASLT_VERSION 0.12.0 CACHE STRING "The version of HipBLASLt to be used" )'
        )
        print("Updated HIPBLASLT_VERSION from 1.0.0 to 0.12.0")

    # Make hipblaslt optional instead of required
    if "find_package( hipblaslt ${HIPBLASLT_VERSION} REQUIRED" in content:
        content = content.replace(
            "find_package( hipblaslt ${HIPBLASLT_VERSION} REQUIRED CONFIG",
            "find_package( hipblaslt ${HIPBLASLT_VERSION} CONFIG"
        )
        print("Made hipblaslt dependency optional instead of required")

    # Add ccache configuration
    ccache_config = '''
# Enable ccache if available
find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    message(STATUS "Found ccache: ${CCACHE_FOUND}")
    set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_FOUND}")
    set(CMAKE_C_COMPILER_LAUNCHER "${CCACHE_FOUND}")

    # Enable ccache for HIP compilation
    set(CMAKE_HIP_COMPILER_LAUNCHER "${CCACHE_FOUND}")

    message(STATUS "ccache enabled for C/C++/HIP compilation")
else()
    message(STATUS "ccache not available - compilation will not be cached")
endif()

'''

    # Add ccache config if not already present
    if "Enable ccache if available" not in content:
        # Insert after cmake_minimum_required
        pattern = r'(cmake_minimum_required\([^)]+\)\s*\n)'
        replacement = r'\1' + ccache_config
        content = re.sub(pattern, replacement, content)
        print("Added ccache configuration")

    # Add kernel generation flags if not already present
    if "ROCBLAS_KERNEL_GEN" not in content:
        # Find a good place to add the flag (after other ROCBLAS flags)
        pattern = r'(set\(ROCBLAS_[^)]+\)\s*\n)'
        replacement = r'\1set(ROCBLAS_KERNEL_GEN ON CACHE BOOL "Enable kernel generation")\n'
        content = re.sub(pattern, replacement, content)
        print("Added kernel generation flag")

    with open(cmake_file, 'w') as f:
        f.write(content)
    print(f"Patched {cmake_file} with all improvements")

def patch_install_script():
    """Patch install.sh to include kernel generation flags"""
    install_file = "install.sh"
    if not os.path.exists(install_file):
        print(f"Warning: {install_file} not found")
        return

    backup_file(install_file)

    with open(install_file, 'r') as f:
        content = f.read()

    # Add kernel generation flags to cmake command
    if "ROCBLAS_KERNEL_GEN=ON" not in content:
        # Find cmake command and add the flag
        pattern = r'(cmake[^"]*"[^"]*)(-DROCBLAS_[^"]*)"'
        replacement = r'\1-DROCBLAS_KERNEL_GEN=ON \2"'
        content = re.sub(pattern, replacement, content)

        with open(install_file, 'w') as f:
            f.write(content)
        print(f"Patched {install_file} with kernel generation flag")

def patch_library_cmake():
    """Patch library/CMakeLists.txt for kernel generation"""
    cmake_file = "library/CMakeLists.txt"
    if not os.path.exists(cmake_file):
        print(f"Warning: {cmake_file} not found")
        return

    backup_file(cmake_file)

    with open(cmake_file, 'r') as f:
        content = f.read()

    # Add kernel generation compilation flags
    kernel_flags = """
# Kernel generation flags
if(ROCBLAS_KERNEL_GEN)
    add_compile_definitions(ROCBLAS_KERNEL_GEN=1)
    add_compile_options(-fno-omit-frame-pointer)
    add_compile_options(-g)
endif()
"""

    if "ROCBLAS_KERNEL_GEN" not in content:
        # Add after the first set of compile definitions
        pattern = r'(add_compile_definitions\([^)]+\)\s*\n)'
        replacement = r'\1' + kernel_flags
        content = re.sub(pattern, replacement, content, count=1)

        with open(cmake_file, 'w') as f:
            f.write(content)
        print(f"Patched {cmake_file} with kernel generation flags")

def patch_kernel_files():
    """Patch kernel files to add profiling markers"""
    kernel_dirs = [
        "library/src/blas1",
        "library/src/blas2",
        "library/src/blas3",
        "library/src/blas_ex"
    ]

    for kernel_dir in kernel_dirs:
        if not os.path.exists(kernel_dir):
            continue

        for file_path in Path(kernel_dir).glob("*_kernels.cpp"):
            patch_kernel_file(str(file_path))

def patch_kernel_file(file_path):
    """Patch a single kernel file to add profiling markers"""
    backup_file(file_path)

    with open(file_path, 'r') as f:
        content = f.read()

    # Add profiling markers to kernel functions
    if "ROCBLAS_KERNEL_GEN" not in content:
        # Add include for profiling
        include_pattern = r'(#include[^\n]*\n)'
        profiling_include = '#ifdef ROCBLAS_KERNEL_GEN\n#include <roctracer/roctracer.h>\n#endif\n'

        # Add after the last include
        includes = re.findall(include_pattern, content)
        if includes:
            last_include = includes[-1]
            content = content.replace(last_include, last_include + profiling_include)

        # Add profiling markers to kernel launches
        kernel_pattern = r'(ROCBLAS_KERNEL\s+[^{]*\{)'
        profiling_marker = '''
#ifdef ROCBLAS_KERNEL_GEN
    roctracer_start();
#endif
'''

        content = re.sub(kernel_pattern, r'\1' + profiling_marker, content)

        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Patched {file_path} with profiling markers")

def detect_hipblaslt_version():
    """Detect the installed hipblaslt version"""
    try:
        import subprocess
        result = subprocess.run(['pkg-config', '--modversion', 'hipblaslt'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"Detected hipblaslt version: {version}")
            return version
    except:
        pass

    # Try to read from cmake config file
    cmake_config = "/opt/rocm/lib/cmake/hipblaslt/hipblaslt-config.cmake"
    if os.path.exists(cmake_config):
        try:
            with open(cmake_config, 'r') as f:
                content = f.read()
                # Look for version information
                version_match = re.search(r'set\(PACKAGE_VERSION["\s]*([0-9.]+)', content)
                if version_match:
                    version = version_match.group(1)
                    print(f"Detected hipblaslt version from cmake config: {version}")
                    return version
        except:
            pass

    # Default fallback
    print("Could not detect hipblaslt version, using default 0.12.0")
    return "0.12.0"

def main():
    """Main patching function"""
    print("Patching rocBLAS for kernel generation and compatibility...")

    # Change to rocBLAS root directory
    if os.path.exists("/root/Sina/rocBLAS"):
        rocblas_root = "/root/Sina/rocBLAS"
    else:
        # Assume we're running from within rocBLAS directory
        rocblas_root = os.getcwd()

    os.chdir(rocblas_root)
    print(f"Working in: {os.getcwd()}")

    # Detect hipblaslt version first
    hipblaslt_version = detect_hipblaslt_version()

    # Apply patches
    patch_cmake_file()
    patch_install_script()
    patch_library_cmake()
    patch_kernel_files()

    print(f"Patching completed! Ready to build with hipblaslt {hipblaslt_version}")

if __name__ == "__main__":
    main()
