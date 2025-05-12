#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y ffmpeg

# Install Python dependencies
pip install --upgrade pip
pip install numpy==1.24.3  # Install numpy first
pip install -r requirements.txt

# Print installed packages for debugging
pip freeze 