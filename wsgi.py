"""
WSGI Entry Point for AWS AppRunner
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wsgi')
logger.info("WSGI module initializing")

# Try to use the minimal app first
try:
    logger.info("Attempting to import app_minimal")
    from app_minimal import app as application
    logger.info("Successfully imported app from app_minimal.py")
except Exception as e:
    logger.warning(f"Could not import app_minimal: {str(e)}")
    
    # Then try to import the application module
    try:
        logger.info("Attempting to import application module")
        from application import application
        logger.info("Successfully imported application from application.py")
    except Exception as e:
        # If that fails, create a minimal Flask application
        logger.error(f"Error importing application: {str(e)}")
        from flask import Flask, Response
        
        application = Flask(__name__)
        
        @application.route('/health')
        def health():
            logger.info("Health check endpoint called via wsgi.py fallback")
            response = Response("OK", status=200, mimetype="text/plain")
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET')
            return response
        
        @application.route('/')
        def root():
            logger.info("Root endpoint called via wsgi.py fallback")
            response = Response("Healthy", status=200, mimetype="text/plain")
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET')
            return response

# Set PORT environment variable for gunicorn
os.environ['PORT'] = os.environ.get('PORT', '8000')

# Log Python environment details
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.executable}")
logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")

# Direct run entry point
if __name__ == "__main__":
    logger.info("Starting application directly via wsgi.py")
    port = int(os.environ.get('PORT', '8000'))
    application.run(host='0.0.0.0', port=port) 