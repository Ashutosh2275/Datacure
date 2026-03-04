"""
Routes module initialization.
Registers all blueprint routes with the Flask application.
"""
from app.routes.auth import auth_bp
from app.routes.patients import patients_bp
from app.routes.appointments import appointments_bp, prescriptions_bp
from app.routes.ai import ai_bp
from app.routes.users import users_bp
from app.routes.billing import billing_bp
from app.routes.inventory import inventory_bp
from app.routes.wards import wards_bp
from app.routes.admin import admin_bp
from app.routes.audit import audit_bp


def register_routes(app):
    """
    Register all route blueprints with Flask app.
    
    Args:
        app: Flask application instance
    """
    # Core authentication & patient management
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(prescriptions_bp)
    
    # AI & Analytics
    app.register_blueprint(ai_bp)
    
    # Hospital operations
    app.register_blueprint(users_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(wards_bp)
    
    # Admin & Compliance
    app.register_blueprint(admin_bp)
    app.register_blueprint(audit_bp)


__all__ = [
    'auth_bp',
    'patients_bp',
    'appointments_bp',
    'prescriptions_bp',
    'ai_bp',
    'users_bp',
    'billing_bp',
    'inventory_bp',
    'wards_bp',
    'admin_bp',
    'audit_bp',
    'register_routes'
]
