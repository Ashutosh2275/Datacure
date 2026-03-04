"""
Rate limiting middleware for DataCure API.
Implements per-endpoint rate limiting using in-memory storage.
For production, use Redis-based solution.
"""
from flask import request, g
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple rate limiter using in-memory storage.
    For production, integrate with Redis.
    """
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_limited(self, identifier, max_requests=100, window_seconds=60):
        """
        Check if request should be rate limited.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Maximum requests in window
            window_seconds: Time window in seconds
        
        Returns:
            (is_limited, remaining_requests, reset_timestamp)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        current_count = len(self.requests[identifier])
        is_limited = current_count >= max_requests
        remaining = max(0, max_requests - current_count)
        reset_time = int((self.requests[identifier][0] + timedelta(seconds=window_seconds)).timestamp()) if self.requests[identifier] else int(now.timestamp()) + window_seconds
        
        # Record this request
        if not is_limited:
            self.requests[identifier].append(now)
        
        return is_limited, remaining, reset_time
    
    def cleanup_old_entries(self, older_than_hours=1):
        """
        Clean up old request records to free memory.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > cutoff_time
            ]
            if not self.requests[identifier]:
                del self.requests[identifier]


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_client_identifier():
    """
    Get unique identifier for client.
    Uses X-Forwarded-For header for proxied requests, falls back to remote_addr.
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def rate_limit(max_requests=100, window_seconds=60, key_func=None):
    """
    Rate limiting decorator.
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        key_func: Function to generate rate limit key (default: IP address)
    
    Example:
        @rate_limit(max_requests=10, window_seconds=60)
        def my_endpoint():
            return {'status': 'ok'}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                identifier = key_func()
            else:
                identifier = get_client_identifier()
            
            # Check rate limit
            is_limited, remaining, reset_time = _rate_limiter.is_limited(
                identifier,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
            
            # Add rate limit headers
            g.rate_limit_limit = max_requests
            g.rate_limit_remaining = remaining
            g.rate_limit_reset = reset_time
            
            if is_limited:
                logger.warning(f"Rate limit exceeded for {identifier} on {request.path}")
                return {
                    'success': False,
                    'message': 'API rate limit exceeded',
                    'error_code': 'RATE_LIMITED',
                    'details': {
                        'retry_after': window_seconds
                    }
                }, 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def auth_rate_limit(max_requests=10, window_seconds=60):
    """
    Rate limiter specifically for authentication endpoints.
    Uses email address as key.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Try to get email from request
            email = None
            try:
                data = request.get_json() or {}
                email = data.get('email', '')
            except:
                pass
            
            if not email:
                email = get_client_identifier()
            
            identifier = f"auth:{email}"
            
            # Check rate limit
            is_limited, remaining, reset_time = _rate_limiter.is_limited(
                identifier,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
            
            # Add rate limit headers
            g.rate_limit_limit = max_requests
            g.rate_limit_remaining = remaining
            g.rate_limit_reset = reset_time
            
            if is_limited:
                logger.warning(f"Auth rate limit exceeded for {email}")
                return {
                    'success': False,
                    'message': 'Too many authentication attempts',
                    'error_code': 'RATE_LIMITED',
                    'details': {
                        'retry_after': window_seconds
                    }
                }, 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def upload_rate_limit(max_requests=10, window_seconds=60):
    """
    Rate limiter specifically for file uploads.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = f"upload:{get_client_identifier()}"
            
            # Check rate limit
            is_limited, remaining, reset_time = _rate_limiter.is_limited(
                identifier,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
            
            # Add rate limit headers
            g.rate_limit_limit = max_requests
            g.rate_limit_remaining = remaining
            g.rate_limit_reset = reset_time
            
            if is_limited:
                logger.warning(f"Upload rate limit exceeded for {get_client_identifier()}")
                return {
                    'success': False,
                    'message': 'File upload rate limit exceeded',
                    'error_code': 'RATE_LIMITED',
                    'details': {
                        'retry_after': window_seconds
                    }
                }, 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def user_rate_limit(max_requests=100, window_seconds=60):
    """
    Rate limiter based on authenticated user.
    Uses user ID as key.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user ID from request context (set by auth middleware)
            user_id = getattr(g, 'user_id', None)
            
            if user_id:
                identifier = f"user:{user_id}"
            else:
                identifier = get_client_identifier()
            
            # Check rate limit
            is_limited, remaining, reset_time = _rate_limiter.is_limited(
                identifier,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
            
            # Add rate limit headers
            g.rate_limit_limit = max_requests
            g.rate_limit_remaining = remaining
            g.rate_limit_reset = reset_time
            
            if is_limited:
                logger.warning(f"User rate limit exceeded for {identifier}")
                return {
                    'success': False,
                    'message': 'User API rate limit exceeded',
                    'error_code': 'RATE_LIMITED',
                    'details': {
                        'retry_after': window_seconds
                    }
                }, 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def apply_rate_limit_headers(response):
    """
    Add rate limit headers to response.
    """
    if hasattr(g, 'rate_limit_limit'):
        response.headers['X-RateLimit-Limit'] = str(g.rate_limit_limit)
        response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
        response.headers['X-RateLimit-Reset'] = str(g.rate_limit_reset)
    
    return response


def cleanup_rate_limiter():
    """
    Cleanup old rate limiter entries.
    Should be called periodically (e.g., via APScheduler).
    """
    _rate_limiter.cleanup_old_entries(older_than_hours=1)
    logger.info("Rate limiter cleanup completed")
