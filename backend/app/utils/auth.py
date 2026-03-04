"""
Authentication utilities - JWT token handling, password hashing, permission checks.
Implements secure token management with JTI-based blacklisting and HTTPOnly cookies.
"""
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from typing import Dict, Optional, Tuple


class JWTHandler:
    """Handles JWT token creation, validation, and refresh with security."""

    @staticmethod
    def encode_token(user_id: str, role: str, hospital_id: str, token_type: str = 'access') -> Tuple[str, str]:
        """
        Encode JWT token with JTI (JWT ID) for token blacklisting.

        Args:
            user_id: User ID
            role: User role
            hospital_id: Hospital ID
            token_type: 'access' or 'refresh'

        Returns:
            (token, jti) - Encoded token and its unique ID
        """
        if token_type == 'access':
            expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 900)
        else:
            expires_in = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000)

        jti = str(uuid.uuid4())

        payload = {
            'user_id': user_id,
            'role': role,
            'hospital_id': hospital_id,
            'token_type': token_type,
            'jti': jti,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        }

        token = jwt.encode(
            payload,
            current_app.config.get('JWT_SECRET_KEY', 'dev-secret-key'),
            algorithm=current_app.config.get('JWT_ALGORITHM', 'HS256')
        )
        return token, jti

    @staticmethod
    def decode_token(token: str, verify: bool = True) -> Optional[Dict]:
        """
        Decode JWT token with optional signature verification.

        Args:
            token: JWT token string
            verify: Whether to verify signature

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config.get('JWT_SECRET_KEY', 'dev-secret-key'),
                algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')],
                options={'verify_signature': verify}
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def get_token_from_request() -> Optional[str]:
        """
        Extract JWT token from Authorization header or access_token cookie.

        Priority:
        1. Authorization header (Bearer scheme)
        2. access_token HTTPOnly cookie

        Returns:
            Token string or None
        """
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                scheme, token = auth_header.split()
                if scheme.lower() == 'bearer':
                    return token
            except (TypeError, ValueError):
                pass

        token = request.cookies.get('access_token')
        if token:
            return token

        return None

    @staticmethod
    def get_refresh_token_from_request() -> Optional[str]:
        """
        Extract refresh token from HTTPOnly cookie.

        Returns:
            Refresh token string or None
        """
        return request.cookies.get('refresh_token')


class PasswordHandler:
    """Handles password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
        """Validate password meets security requirements."""
        if len(password) < 8:
            return False, 'Password must be at least 8 characters long'

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

        if not has_upper:
            return False, 'Password must contain at least one uppercase letter'
        if not has_lower:
            return False, 'Password must contain at least one lowercase letter'
        if not has_digit:
            return False, 'Password must contain at least one digit'
        if not has_special:
            return False, 'Password must contain at least one special character'

        return True, None


class PermissionChecker:
    """Handles role-based access control."""

    ROLE_PERMISSIONS = {
        'admin': [
            'manage_users', 'manage_hospital', 'view_reports', 'manage_inventory',
            'manage_appointments', 'view_audit_logs', 'manage_doctors', 'manage_patients',
            'manage_billing', 'manage_ai_models',
        ],
        'doctor': [
            'view_appointments', 'create_prescription', 'view_patient_records',
            'upload_medical_records', 'view_patient_billing',
        ],
        'nurse': [
            'view_appointments', 'update_bed_status', 'view_patient_records',
            'manage_inventory', 'record_vitals',
        ],
        'patient': [
            'view_own_appointments', 'book_appointment', 'view_own_records',
            'view_own_prescriptions', 'view_own_billing', 'download_reports',
        ],
        'staff': [
            'manage_appointments', 'update_bed_status', 'manage_inventory', 'view_reports',
        ],
    }

    @staticmethod
    def has_permission(user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission."""
        permissions = PermissionChecker.ROLE_PERMISSIONS.get(user_role, [])
        return required_permission in permissions

    @staticmethod
    def has_any_role(user_role: str, required_roles: list) -> bool:
        """Check if user has any of the required roles."""
        return user_role in required_roles


def token_required(f):
    """
    Decorator to require valid JWT token with blacklist checking.

    Extracts token from Authorization header or access_token cookie.
    Validates token signature and expiry.
    Checks if token has been blacklisted.

    Sets on request object:
    - request.user_id
    - request.user_role
    - request.hospital_id
    - request.token_jti
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = JWTHandler.get_token_from_request()

        if not token:
            return jsonify({'message': 'Authorization token is missing'}), 401

        payload = JWTHandler.decode_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401

        # Check if token is blacklisted
        try:
            from app.models import TokenBlacklist
            jti = payload.get('jti')
            if jti and TokenBlacklist.is_token_blacklisted(jti):
                return jsonify({'message': 'Token has been revoked'}), 401
        except Exception as e:
            current_app.logger.warning(f"Token blacklist check failed: {str(e)}")

        # Store decoded token in request context
        request.user_id = payload.get('user_id')
        request.user_role = payload.get('role')
        request.hospital_id = payload.get('hospital_id')
        request.token_jti = payload.get('jti')

        return f(*args, **kwargs)

    return decorated


def role_required(*roles):
    """Decorator to require specific user roles."""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if request.user_role not in roles:
                return jsonify({
                    'message': f'Access denied. Required roles: {", ".join(roles)}'
                }), 403

            return f(*args, **kwargs)

        return decorated

    return decorator


def permission_required(permission: str):
    """Decorator to require specific permission."""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if not PermissionChecker.has_permission(request.user_role, permission):
                return jsonify({
                    'message': f'Permission denied: {permission}'
                }), 403

            return f(*args, **kwargs)

        return decorated

    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    return role_required('admin')(f)


def doctor_required(f):
    """Decorator to require doctor role."""
    return role_required('doctor')(f)


def patient_required(f):
    """Decorator to require patient role."""
    return role_required('patient')(f)


def hospital_isolated(f):
    """
    Decorator to enforce hospital data isolation for multi-tenancy.

    Validates that the requested hospital_id matches the user's assigned hospital.
    Prevents users from accessing data from other hospitals.

    Logs unauthorized access attempts for audit/security.

    This decorator should be applied to all routes that accept a hospital_id parameter
    or access hospital-specific data.

    Expected behavior:
    - User can only see/modify data from their assigned hospital
    - Cross-hospital access attempts are blocked with 403 Forbidden
    - Unauthorized attempts are logged for audit trail

    Usage:
        @app.route('/api/v1/patients')
        @token_required
        @hospital_isolated
        def list_patients():
            # route.hospital_id is guaranteed to match user's hospital
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # User context set by @token_required decorator
        user_hospital_id = getattr(request, 'hospital_id', None)
        user_id = getattr(request, 'user_id', None)

        if not user_hospital_id or not user_id:
            return jsonify({'message': 'Hospital context not available'}), 401

        # Get requested hospital from route parameter
        # Try multiple common parameter names
        requested_hospital_id = (
            kwargs.get('hospital_id') or
            request.args.get('hospital_id')
        )
        
        # Only try to read JSON body for non-GET requests
        if not requested_hospital_id and request.method not in ('GET', 'HEAD', 'OPTIONS', 'DELETE'):
            try:
                json_data = request.get_json(silent=True)
                if json_data and isinstance(json_data, dict):
                    requested_hospital_id = json_data.get('hospital_id')
            except Exception:
                pass
        
        if not requested_hospital_id:
            requested_hospital_id = getattr(request, 'hospital_id', None)

        # If no explicit hospital_id requested, use user's hospital (implicit access)
        if not requested_hospital_id:
            request.validated_hospital_id = user_hospital_id
            return f(*args, **kwargs)

        # Verify requested hospital matches user's hospital
        if requested_hospital_id != user_hospital_id:
            # Log unauthorized access attempt
            try:
                from app.models import AuditLog
                from app.extensions import db

                audit_log = AuditLog(
                    hospital_id=user_hospital_id,  # User's actual hospital
                    user_id=user_id,
                    action='UNAUTHORIZED_HOSPITAL_ACCESS_ATTEMPT',
                    resource_type='hospital',
                    resource_id=requested_hospital_id,
                    changes={
                        'attempted_hospital_id': requested_hospital_id,
                        'user_hospital_id': user_hospital_id,
                        'reason': 'Cross-hospital access attempt'
                    },
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    status='failed'
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as e:
                current_app.logger.warning(f"Failed to log unauthorized access: {str(e)}")

            # Block access
            return jsonify({
                'message': 'Access denied. You do not have permission to access this hospital\'s data.',
                'error_code': 'HOSPITAL_ISOLATION_VIOLATION'
            }), 403

        # Hospital ID matches - set validated context
        request.validated_hospital_id = user_hospital_id

        return f(*args, **kwargs)

    return decorated

