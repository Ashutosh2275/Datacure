"""
Utility modules for DataCure application.
"""
from app.utils.auth import (
    JWTHandler,
    PasswordHandler,
    PermissionChecker,
    token_required,
    role_required,
    permission_required,
    admin_required,
    doctor_required,
    patient_required,
    hospital_isolated,
)
from app.utils.errors import (
    APIError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    APIResponse,
    api_error_handler,
)
from app.utils.logging_config import setup_logging, get_logger
from app.utils.helpers import (
    Paginator,
    QueryFilter,
    InputValidator,
    DataTransformer,
    IDGenerator,
)

__all__ = [
    'JWTHandler',
    'PasswordHandler',
    'PermissionChecker',
    'token_required',
    'role_required',
    'permission_required',
    'admin_required',
    'doctor_required',
    'patient_required',
    'hospital_isolated',
    'APIError',
    'ValidationError',
    'NotFoundError',
    'UnauthorizedError',
    'ForbiddenError',
    'ConflictError',
    'APIResponse',
    'api_error_handler',
    'setup_logging',
    'get_logger',
    'Paginator',
    'QueryFilter',
    'InputValidator',
    'DataTransformer',
    'IDGenerator',
]
