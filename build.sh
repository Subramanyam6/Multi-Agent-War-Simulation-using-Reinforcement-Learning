#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install numpy==1.24.3  # Install numpy first
pip install -r requirements.txt

# Print installed packages for debugging
pip freeze 