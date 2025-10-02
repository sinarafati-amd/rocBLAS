#!/bin/bash

# Script to apply patches without modifying original source files permanently
# This creates a temporary patched version for building

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCHES_DIR="$SCRIPT_DIR/patches"

echo "Applying rocBLAS patches for build compatibility..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository. Please run from rocBLAS root directory."
    exit 1
fi

# Create a backup branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/original-source; then
    echo "Creating backup branch 'original-source'..."
    git branch original-source
fi

# Apply patches
echo "Applying hipBLASLT API compatibility patch..."
if [ -f "$PATCHES_DIR/hipblaslt_api_fix.patch" ]; then
    git apply "$PATCHES_DIR/hipblaslt_api_fix.patch"
    echo "? Applied hipBLASLT API fix patch"
else
    echo "Warning: hipblaslt_api_fix.patch not found"
fi

echo "Patches applied successfully!"
echo ""
echo "To restore original files after build:"
echo "  git checkout original-source -- ."
echo ""
echo "To build with patches:"
echo "  ./install.sh --architecture gfx942 --clients --relwithdebinfo"
