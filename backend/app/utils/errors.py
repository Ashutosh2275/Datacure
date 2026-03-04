"""
Error handling and response formatting utilities.
"""
from flask import jsonify
from typing import Any, Dict, Optional, Tuple


class APIError(Exception):
    """Custom exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Custom error code for client handling
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
    
    def to_dict(self) -> Dict:
        """Convert error to dictionary."""
        error_dict = {
            'success': False,
            'message': self.message,
            'status_code': self.status_code,
        }
        if self.error_code:
            error_dict['error_code'] = self.error_code
        return error_dict


class ValidationError(APIError):
    """Validation error."""
    def __init__(self, message: str, error_code: str = 'VALIDATION_ERROR'):
        super().__init__(message, status_code=422, error_code=error_code)


class NotFoundError(APIError):
    """Resource not found error."""
    def __init__(self, resource: str):
        message = f'{resource} not found'
        super().__init__(message, status_code=404, error_code='NOT_FOUND')


class UnauthorizedError(APIError):
    """Unauthorized access error."""
    def __init__(self, message: str = 'Unauthorized'):
        super().__init__(message, status_code=401, error_code='UNAUTHORIZED')


class ForbiddenError(APIError):
    """Forbidden access error."""
    def __init__(self, message: str = 'Access denied'):
        super().__init__(message, status_code=403, error_code='FORBIDDEN')


class ConflictError(APIError):
    """Resource conflict error."""
    def __init__(self, message: str):
        super().__init__(message, status_code=409, error_code='CONFLICT')


# ==================== RESPONSE FORMATTING ====================

class APIResponse:
    """Structured API response formatter."""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = 'Success',
        status_code: int = 200,
        meta: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """
        Format successful response.
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata
            
        Returns:
            (response_dict, status_code) tuple
        """
        response = {
            'success': True,
            'message': message,
            'data': data,
        }
        if meta:
            response['meta'] = meta
        
        return response, status_code
    
    @staticmethod
    def error(
        message: str,
        status_code: int = 400,
        error_code: str = None,
        details: Any = None
    ) -> Tuple[Dict, int]:
        """
        Format error response.
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Custom error code
            details: Additional error details
            
        Returns:
            (response_dict, status_code) tuple
        """
        response = {
            'success': False,
            'message': message,
        }
        if error_code:
            response['error_code'] = error_code
        if details:
            response['details'] = details
        
        return response, status_code
    
    @staticmethod
    def paginated(
        data: list,
        page: int,
        per_page: int,
        total: int,
        message: str = 'Success'
    ) -> Tuple[Dict, int]:
        """
        Format paginated response.
        
        Args:
            data: List of items
            page: Current page number
            per_page: Items per page
            total: Total number of items
            message: Success message
            
        Returns:
            (response_dict, 200) tuple
        """
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        
        response = {
            'success': True,
            'message': message,
            'data': data,
            'meta': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1,
            }
        }
        
        return response, 200
    
    @staticmethod
    def created(data: Any = None, message: str = 'Created successfully') -> Tuple[Dict, int]:
        """Format 201 Created response."""
        return APIResponse.success(data, message, status_code=201)
    
    @staticmethod
    def no_content() -> Tuple[Dict, int]:
        """Format 204 No Content response."""
        return {}, 204
    
    @staticmethod
    def bad_request(message: str) -> Tuple[Dict, int]:
        """Format 400 Bad Request response."""
        return APIResponse.error(message, 400)
    
    @staticmethod
    def unauthorized() -> Tuple[Dict, int]:
        """Format 401 Unauthorized response."""
        return APIResponse.error('Unauthorized', 401)
    
    @staticmethod
    def forbidden() -> Tuple[Dict, int]:
        """Format 403 Forbidden response."""
        return APIResponse.error('Access denied', 403)
    
    @staticmethod
    def not_found(resource: str = 'Resource') -> Tuple[Dict, int]:
        """Format 404 Not Found response."""
        return APIResponse.error(f'{resource} not found', 404)
    
    @staticmethod
    def conflict(message: str) -> Tuple[Dict, int]:
        """Format 409 Conflict response."""
        return APIResponse.error(message, 409)
    
    @staticmethod
    def validation_error(message: str, details: Any = None) -> Tuple[Dict, int]:
        """Format 422 Validation Error response."""
        return APIResponse.error(message, 422, error_code='VALIDATION_ERROR', details=details)
    
    @staticmethod
    def internal_error(message: str = 'Internal server error') -> Tuple[Dict, int]:
        """Format 500 Internal Server Error response."""
        return APIResponse.error(message, 500)


def api_error_handler(error: APIError):
    """
    Handle APIError exceptions.
    
    Args:
        error: APIError instance
        
    Returns:
        Flask response tuple
    """
    return jsonify(error.to_dict()), error.status_code
