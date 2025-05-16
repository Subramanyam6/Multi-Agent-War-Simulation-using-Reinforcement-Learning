from flask import Flask, Response, request
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('application')

# Create a Flask app
application = Flask(__name__)

# Add health check endpoints
@application.route('/health')
def health_check():
    """Health check endpoint for AppRunner"""
    logger.info("Health check called from application.py")
    response = Response("OK", status=200, mimetype="text/plain")
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

# Add a root health check as well
@application.route('/', defaults={'path': ''})
@application.route('/<path:path>')
def catch_all(path):
    """Root handler for health checks and other paths"""
    user_agent = request.headers.get('User-Agent', '')
    logger.info(f"Request at path: {path}, User-Agent: {user_agent}")
    
    if 'ELB-HealthChecker' in user_agent or 'AppRunner' in user_agent:
        logger.info(f"Health check from: {user_agent}")
        response = Response("Healthy", status=200, mimetype="text/plain")
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response
    
    # For other requests, try to import the app functions dynamically
    # to avoid circular imports
    try:
        from app import index
        return index()
    except Exception as e:
        logger.error(f"Error handling request: {str(e)}")
        return Response("Service is running but application routes not available", 
                        status=200, mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    application.run(host='0.0.0.0', port=port)