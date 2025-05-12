#!/usr/bin/env bash
# exit on error
set -o errexit

# Print Python version for debugging
python --version
echo "PYTHONPATH: ${PYTHONPATH}"

# Try to install system dependencies if possible (won't fail the build if it doesn't work)
if [ -x "$(command -v apt-get)" ]; then
  echo "Attempting to install ffmpeg with apt-get..."
  apt-get update || true
  apt-get install -y ffmpeg || true
elif [ -x "$(command -v yum)" ]; then
  echo "Attempting to install ffmpeg with yum..."
  yum -y install ffmpeg || true
else
  echo "Could not install ffmpeg - system package manager not found"
  echo "Animation will fall back to JavaScript-based output"
fi

# Check if ffmpeg is now available
if [ -x "$(command -v ffmpeg)" ]; then
  echo "ffmpeg is available: $(ffmpeg -version | head -n 1)"
else
  echo "ffmpeg is not available, but continuing anyway"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install numpy==1.24.3  # Install numpy first
pip install -r requirements.txt

# Print installed packages for debugging
echo "Installed Python packages:"
pip freeze 