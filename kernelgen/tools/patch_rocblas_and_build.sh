#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Change to the root directory of the project (two levels up from kernelgen/tools/)
cd "$SCRIPT_DIR/../.."

# Save the root directory path
ROOT_DIR=$(pwd)

echo "Running from root directory: $ROOT_DIR"
echo "Patching and building rocBLAS with kernel generation support..."

# Install ccache if needed
echo "Installing ccache for faster compilation..."
sudo apt-get update
sudo apt-get install -y ccache

# Set up ccache
export CCACHE_DIR="$HOME/.ccache"
export PATH="/usr/lib/ccache:$PATH"
ccache --max-size=20G
echo "ccache configuration:"
ccache --show-stats

# Run patch_rocblas.py from the root directory
echo "Applying rocBLAS patches..."
python3 kernelgen/tools/patch_rocblas.py

# Check if patch was successful
if [ $? -ne 0 ]; then
    echo "Error: Patching failed!"
    exit 1
fi

# Clean any existing build to ensure patches take effect
if [ -d "build" ]; then
    echo "Cleaning existing build directory..."
    rm -rf build
fi

# Run install.sh with appropriate flags
echo "Starting rocBLAS build..."
echo "Build command: ./install.sh --architecture gfx942 --clients --relwithdebinfo --no_hipblaslt"

# Use more flexible build options to avoid hipblaslt issues
./install.sh --architecture gfx942 --clients --relwithdebinfo --no_hipblaslt

# Check build result
if [ $? -eq 0 ]; then
    echo "? rocBLAS build completed successfully!"
    echo "ccache stats after build:"
    ccache --show-stats

    # Verify that the build produced the expected binaries
    if [ -f "build/release-debug/clients/staging/rocblas-bench" ]; then
        echo "? rocblas-bench binary created successfully"
    else
        echo "?  Warning: rocblas-bench binary not found"
    fi

    if [ -f "build/release-debug/clients/staging/rocblas-test" ]; then
        echo "? rocblas-test binary created successfully"
    else
        echo "?  Warning: rocblas-test binary not found"
    fi

else
    echo "? rocBLAS build failed!"
    echo "You may need to:"
    echo "1. Check hipblaslt compatibility"
    echo "2. Disable hipblaslt with: ./install.sh --architecture gfx942 --clients --relwithdebinfo --no-hipblaslt"
    echo "3. Check build logs for specific errors"
    exit 1
fi
