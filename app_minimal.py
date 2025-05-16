#!/usr/bin/env python3
"""
Minimal Flask web application for AWS AppRunner health checks
"""

from flask import Flask, render_template, request, Response
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('app_minimal')

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page"""
    # Return a simple response for health checks if requested by the health check
    user_agent = request.headers.get('User-Agent', '')
    logger.info(f"Request received at / with User-Agent: {user_agent}")
    if 'ELB-HealthChecker' in user_agent or 'AppRunner' in user_agent:
        logger.info(f"Health check detected from: {user_agent}")
        return "Healthy", 200
    # Otherwise render a simple response
    return "Application is running correctly", 200

@app.route('/health')
def health():
    """Explicit health check endpoint"""
    logger.info("Health check endpoint called")
    response = Response("OK", status=200, mimetype="text/plain")
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False) 