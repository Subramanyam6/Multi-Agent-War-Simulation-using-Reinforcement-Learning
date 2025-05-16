#!/usr/bin/env python3
"""
Standalone Flask application for AWS AppRunner
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

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint"""
    user_agent = request.headers.get('User-Agent', '')
    logger.info(f"Request at root with User-Agent: {user_agent}")
    
    # Special handling for health checks
    if 'ELB-HealthChecker' in user_agent or 'AppRunner' in user_agent:
        response = Response("Healthy", status=200, mimetype="text/plain")
        return response
    
    return jsonify({
        "status": "ok",
        "message": "AWS AppRunner Flask Application is running",
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
        "environ": dict(os.environ),
        "cwd": os.getcwd(),
        "directory_contents": os.listdir('.'),
        "headers": dict(request.headers)
    }
    return jsonify(env_info)

# Define application variable for wsgi
application = app

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port) 