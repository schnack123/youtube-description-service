"""YouTube Description Service - Main Flask Application"""
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps

from src.config import config
from src.routes.descriptions import descriptions_bp
from src.routes.admin import admin_bp

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=config.CORS_ORIGINS)

# Register blueprints
app.register_blueprint(descriptions_bp)
app.register_blueprint(admin_bp)


def require_auth(f):
    """Decorator to require API token authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'success': False, 'error': 'Missing Authorization header'}), 401
        
        # Check Bearer token format
        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Invalid Authorization format'}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        if token != config.API_TOKEN:
            return jsonify({'success': False, 'error': 'Invalid API token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


# Apply authentication to all routes except health check
@app.before_request
def check_auth():
    """Check authentication for all requests except health check"""
    if request.path == '/health':
        return None
    
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({'success': False, 'error': 'Missing Authorization header'}), 401
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'error': 'Invalid Authorization format'}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    if token != config.API_TOKEN:
        return jsonify({'success': False, 'error': 'Invalid API token'}), 401


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'description-service',
        'version': '1.0.0'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f"Starting Description Service on {config.HOST}:{config.PORT}")
    logger.info(f"Using Azure OpenAI: {config.USE_AZURE_OPENAI}")
    logger.info(f"Model: {config.AZURE_OPENAI_DEPLOYMENT if config.USE_AZURE_OPENAI else config.OPENAI_MODEL}")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=(config.LOG_LEVEL == 'DEBUG')
    )

