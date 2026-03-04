"""
Flask application factory and initialization.
"""
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import get_config
from app.extensions import db, ma, cors, init_extensions
from app.utils import setup_logging, get_logger, api_error_handler, APIError


logger = get_logger(__name__)


def create_app(config_class=None):
    """
    Create and configure Flask application.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    logger.info(f"Starting DataCure application in {app.config['FLASK_ENV']} mode")
    
    # Initialize extensions
    init_extensions(app)
    
    # Register error handlers
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return api_error_handler(error)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error_code': 'BAD_REQUEST'
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'error_code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }), 500
    
    # Register blueprints
    register_blueprints(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'DataCure API',
            'environment': app.config['FLASK_ENV']
        }), 200
    
    return app


def register_blueprints(app: Flask):
    """
    Register Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    try:
        # Import blueprints
        from app.routes.auth import auth_bp
        from app.routes.patients import patients_bp, doctors_bp
        from app.routes.appointments import appointments_bp, prescriptions_bp
        from app.routes.ai import ai_bp
        from app.routes.users import users_bp
        from app.routes.billing import billing_bp
        from app.routes.inventory import inventory_bp
        from app.routes.wards import wards_bp
        from app.routes.admin import admin_bp
        from app.routes.audit import audit_bp
        from app.routes.uploads import upload_bp

        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        app.register_blueprint(users_bp, url_prefix='/api/v1/users')
        app.register_blueprint(patients_bp, url_prefix='/api/v1/patients')
        app.register_blueprint(doctors_bp, url_prefix='/api/v1/doctors')
        app.register_blueprint(appointments_bp, url_prefix='/api/v1/appointments')
        app.register_blueprint(prescriptions_bp, url_prefix='/api/v1/prescriptions')
        app.register_blueprint(billing_bp, url_prefix='/api/v1/billing')
        app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
        app.register_blueprint(wards_bp, url_prefix='/api/v1/wards')
        app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')
        app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
        app.register_blueprint(audit_bp, url_prefix='/api/v1/audit')
        app.register_blueprint(upload_bp, url_prefix='/api/v1/uploads')
        
        logger.info("All blueprints registered successfully")
    
    except ImportError as e:
        logger.error(f"Failed to register blueprints: {str(e)}")
        raise


def register_cli_commands(app: Flask):
    """
    Register Flask CLI commands.
    
    Args:
        app: Flask application instance
    """
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command()
    def drop_db():
        """Drop all database tables."""
        if input("Are you sure? (y/n): ").lower() == 'y':
            db.drop_all()
            print('Database dropped.')
    
    @app.cli.command()
    def seed_db():
        """Seed database with initial data."""
        from app.models import Hospital, User, RoleEnum
        
        # Create default hospital
        hospital = Hospital(
            name='Demo Hospital',
            email='hospital@example.com',
            phone='+91-1234567890',
            address='123 Medical Street',
            city='Bangalore',
            state='Karnataka',
            postal_code='560001',
            country='India'
        )
        db.session.add(hospital)
        db.session.commit()
        
        print(f'Database seeded with hospital: {hospital.name}')
