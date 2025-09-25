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
    """Patch CMakeLists.txt to enable kernel generation"""
    cmake_file = "CMakeLists.txt"
    if not os.path.exists(cmake_file):
        print(f"Warning: {cmake_file} not found")
        return
    
    backup_file(cmake_file)
    
    with open(cmake_file, 'r') as f:
        content = f.read()
    
    # Add kernel generation flags if not already present
    if "ROCBLAS_KERNEL_GEN" not in content:
        # Find a good place to add the flag (after other ROCBLAS flags)
        pattern = r'(set\(ROCBLAS_[^)]+\)\s*\n)'
        replacement = r'\1set(ROCBLAS_KERNEL_GEN ON CACHE BOOL "Enable kernel generation")\n'
        content = re.sub(pattern, replacement, content)
        
        with open(cmake_file, 'w') as f:
            f.write(content)
        print(f"Patched {cmake_file} with kernel generation flag")

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

def main():
    """Main patching function"""
    print("Patching rocBLAS for kernel generation...")
    
    # Change to rocBLAS root directory
    rocblas_root = "/root/Sina/rocBLAS"
    os.chdir(rocblas_root)
    
    print(f"Working in: {os.getcwd()}")
    
    # Apply patches
    patch_cmake_file()
    patch_install_script()
    patch_library_cmake()
    patch_kernel_files()
    
    print("Patching completed!")

if __name__ == "__main__":
    main()
