#!/bin/bash
# Startup script for Azure App Service

# Log startup information
echo "Starting application..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Make script executable if needed
chmod +x app_standalone.py

# Start Gunicorn with the standalone app
gunicorn --bind=0.0.0.0:8000 --timeout=120 --workers=2 --threads=2 --log-level=info app_standalone:application 