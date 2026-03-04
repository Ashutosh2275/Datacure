"""
Logging configuration and utilities.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, has_request_context


class RequestIdFilter(logging.Filter):
    """Add request context information to logs."""
    
    def filter(self, record):
        if has_request_context():
            record.request_id = request.remote_addr
            record.user_id = getattr(request, 'user_id', 'anonymous')
        else:
            record.request_id = 'background'
            record.user_id = 'system'
        return True


def setup_logging(app: Flask):
    """
    Configure logging for the application.
    
    Args:
        app: Flask application instance
    """
    log_file = app.config.get('LOG_FILE', './logs/app.log')
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # Create logs directory if not exists
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Add request filter
    logger.addFilter(RequestIdFilter())
    
    # Remove existing handlers (if any)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Formatter with get() to handle missing attributes
    class SafeFormatter(logging.Formatter):
        def format(self, record):
            if not hasattr(record, 'user_id'):
                record.user_id = 'anonymous'
            if not hasattr(record, 'request_id'):
                record.request_id = 'background'
            return super().format(record)
    
    formatter = SafeFormatter(
        '[%(asctime)s] %(levelname)s in %(module)s - User: %(user_id)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Create module-level logger
logger = logging.getLogger(__name__)
