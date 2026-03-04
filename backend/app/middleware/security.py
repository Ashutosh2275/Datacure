"""
Security headers middleware for DataCure application.
Implements OWASP security best practices.
"""
from flask import request, g
from functools import wraps
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def add_security_headers(response):
    """
    Add security headers to all responses.
    """
    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection in older browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer Policy - only send referrer to same-origin
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy - restrict powerful browser features
    response.headers['Permissions-Policy'] = (
        'geolocation=(), '
        'microphone=(), '
        'camera=(), '
        'payment=(), '
        'usb=()'
    )
    
    # Content Security Policy - restrict content sources
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self' https://api.example.com; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "object-src 'none'"
    )
    
    # HSTS - enforce HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Remove server info
    response.headers.pop('Server', None)
    
    # Custom security header
    response.headers['X-Application-Name'] = 'DataCure'
    
    return response


def validate_content_type(required_types=None):
    """
    Validate request content type.
    
    Args:
        required_types: List of allowed content types (default: ['application/json'])
    """
    if required_types is None:
        required_types = ['application/json']
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip validation for GET, HEAD, OPTIONS requests
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return f(*args, **kwargs)
            
            # Check content type
            content_type = request.content_type
            if content_type is None:
                return {'success': False, 'message': 'Missing Content-Type header'}, 400
            
            # Extract content type without charset
            content_type = content_type.split(';')[0].strip()
            
            if content_type not in required_types:
                return {
                    'success': False,
                    'message': f'Invalid Content-Type. Expected {required_types}'
                }, 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_request_size(max_size_mb=10):
    """
    Validate request payload size.
    
    Args:
        max_size_mb: Maximum payload size in MB
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_length = request.content_length
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if content_length and content_length > max_size_bytes:
                return {
                    'success': False,
                    'message': f'Request payload exceeds {max_size_mb}MB limit'
                }, 413
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_request_response():
    """
    Log detailed request and response information.
    """
    @wraps(None)
    def before_request():
        g.start_time = datetime.utcnow()
        g.request_info = {
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @wraps(None)
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = (datetime.utcnow() - g.start_time).total_seconds()
            
            log_data = {
                **g.request_info,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'response_size': len(response.get_data(as_text=True))
            }
            
            # Log level based on status code
            if 200 <= response.status_code < 300:
                logger.info(f"Request: {log_data}")
            elif 300 <= response.status_code < 400:
                logger.info(f"Redirect: {log_data}")
            elif 400 <= response.status_code < 500:
                logger.warning(f"Client Error: {log_data}")
            else:
                logger.error(f"Server Error: {log_data}")
        
        return response
    
    return before_request, after_request


def sanitize_input(data, allowed_fields=None, max_string_length=1000):
    """
    Sanitize and validate input data.
    
    Args:
        data: Input dictionary
        allowed_fields: List of allowed field names
        max_string_length: Maximum length for string fields
    
    Returns:
        Sanitized data dictionary
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    
    for key, value in data.items():
        # Check allowed fields
        if allowed_fields and key not in allowed_fields:
            continue
        
        # Sanitize string values
        if isinstance(value, str):
            # Limit length
            if len(value) > max_string_length:
                value = value[:max_string_length]
            
            # Remove leading/trailing whitespace
            value = value.strip()
            
            # Remove null bytes
            value = value.replace('\x00', '')
        
        sanitized[key] = value
    
    return sanitized


def require_https(f):
    """
    Decorator to require HTTPS for an endpoint.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not request.environ.get('wsgi.url_scheme') == 'https':
            # Allow localhost for development
            if request.host.split(':')[0] not in ['localhost', '127.0.0.1']:
                return {
                    'success': False,
                    'message': 'HTTPS required'
                }, 403
        
        return f(*args, **kwargs)
    return decorated_function


def api_version_required(version):
    """
    Decorator to require specific API version.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_version = request.headers.get('API-Version', '1.0')
            
            if api_version != version:
                return {
                    'success': False,
                    'message': f'API version {version} required',
                    'current_version': api_version
                }, 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
