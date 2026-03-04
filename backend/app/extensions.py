"""
Flask extensions initialization.
Centralizes database, serialization, and other extension setup.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()


def init_extensions(app):
    """
    Initialize all Flask extensions.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    ma.init_app(app)
    
    # Create upload folders
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER', './uploads')
    log_folder = os.path.dirname(app.config.get('LOG_FILE', './logs/app.log'))
    model_folder = app.config.get('MODEL_CACHE_DIR', './ai/models')
    
    for folder in [upload_folder, log_folder, model_folder]:
        os.makedirs(folder, exist_ok=True)


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin to add soft delete capability to models."""
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def soft_delete(self):
        """Soft delete - mark as deleted without removing from database."""
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
    
    @classmethod
    def query_active(cls):
        """Query only non-deleted records."""
        return cls.query.filter(cls.deleted_at.is_(None))
