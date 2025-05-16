#!/bin/bash
# Startup script for Azure App Service

# Make sure the script fails on errors
set -e

# Log startup information
echo "===== STARTUP SCRIPT RUNNING ====="
echo "Date: $(date)"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Directory contents:"
ls -la
echo "Environment variables (sanitized):"
env | grep -v -E "KEY|TOKEN|SECRET|PASSWORD|PUBLISH" | sort

# Make sure scripts are executable
echo "Making scripts executable..."
chmod +x app_standalone.py

# Set PORT to Azure's expected value if not already set
if [[ -z "${PORT}" ]]; then
  echo "Setting PORT to 8000"
  export PORT=8000
fi

echo "Starting Gunicorn on port $PORT..."

# On Azure, we need to ensure the server runs in the foreground
exec gunicorn --bind=0.0.0.0:$PORT \
  --timeout=120 \
  --workers=2 \
  --threads=2 \
  --log-level=info \
  --access-logfile=- \
  --error-logfile=- \
  app_standalone:application 