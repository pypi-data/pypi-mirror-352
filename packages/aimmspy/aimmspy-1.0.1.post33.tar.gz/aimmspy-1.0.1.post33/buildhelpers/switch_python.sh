#!/bin/bash


VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Error: No Python version specified."
    exit 1
fi
pyenv global $VERSION
if [ $? -ne 0 ]; then
    echo "Error: Python version $VERSION not found."
    exit 1
fi
echo "Switched to Python version $VERSION"
# Verify the switch
python --version
if [ $? -ne 0 ]; then
    echo "Error: Failed to verify Python version."
    exit 1
fi