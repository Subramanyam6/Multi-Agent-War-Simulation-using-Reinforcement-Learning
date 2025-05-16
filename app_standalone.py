#!/usr/bin/env python3
"""
Standalone Flask application for AWS AppRunner and Azure App Service
Completely self-contained with no dependencies on other modules
"""

from flask import Flask, Response, request, jsonify
import logging
import os
import sys
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('standalone')
logger.info("Starting standalone application")

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint"""
    user_agent = request.headers.get('User-Agent', '')
    logger.info(f"Request at root with User-Agent: {user_agent}")
    
    # Special handling for health checks
    if any(checker in user_agent for checker in ['ELB-HealthChecker', 'AppRunner', 'HealthCheck']):
        logger.info(f"Health check detected from: {user_agent}")
        response = Response("Healthy", status=200, mimetype="text/plain")
        return response
    
    return jsonify({
        "status": "ok",
        "message": "Flask Application is running",
        "environment": os.environ.get('ENVIRONMENT', 'Not specified'),
        "time": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    response = Response("OK", status=200, mimetype="text/plain")
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

@app.route('/debug')
def debug():
    """Debug endpoint to check environment"""
    env_info = {
        "python_version": sys.version,
        "python_path": sys.executable,
        "environ": {k: v for k, v in os.environ.items() if not k.lower().startswith(('secret', 'key', 'token', 'password'))},
        "cwd": os.getcwd(),
        "directory_contents": os.listdir('.'),
        "request_host": request.host,
        "request_headers": dict(request.headers)
    }
    return jsonify(env_info)

# Define application variable for WSGI
application = app

# Main entry point
if __name__ == "__main__":
    # For Azure Web Apps, use the provided port (typically 8000)
    # For AWS AppRunner, use port 8000
    # For local dev, default to 8000
    port = int(os.environ.get('PORT', os.environ.get('WEBSITES_PORT', 8000)))
    logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port) 