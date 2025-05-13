from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../../dist/public', static_url_path='')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure CSRF protection to work with AJAX requests
    csrf.init_app(app)
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Disable automatic CSRF checks
    app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken']  # Accept CSRF token from this header
    
    # Enable CORS for all routes with full preflight support
    CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True, "allow_headers": "*", "expose_headers": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})
    
    # Register blueprints
    from app.routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Exempt specific routes from CSRF protection if needed
    from app.routes import availability_routes, profile_routes
    csrf.exempt(availability_routes)
    csrf.exempt(profile_routes)  # Exempt profile routes from CSRF protection
    
    # Handle errors
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    # Add a health check route
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}, 200
    
    # Add a route for session-based auth
    @app.route('/api/user', methods=['GET'])
    def current_user_route():
        from flask import session, jsonify
        from app.models import User
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(None), 401
            
        user = User.query.get(user_id)
        if not user:
            return jsonify(None), 401
            
        return jsonify(user.to_dict())
    
    # Add route to get CSRF token
    @app.route('/api/csrf-token', methods=['GET'])
    def get_csrf_token():
        from flask import jsonify, session
        from flask_wtf.csrf import generate_csrf
        
        # Generate a CSRF token using the proper function
        token = generate_csrf()
        
        return jsonify({'csrf_token': token})
    
    # Serve the React app - catch all route
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app

from app import models