"""
Authentication and Authorization Routes.
Handles user registration, login, logout, token refresh, and password management.
"""
from flask import Blueprint, request, jsonify, make_response
from app.services import AuthenticationService, UserManagementService
from app.schemas import (
    LoginSchema, UserCreateSchema, UserResponseSchema, TokenResponseSchema
)
from app.utils import APIResponse, JWTHandler, token_required, admin_required
from app.models import TokenBlacklist
from app.extensions import db
from marshmallow import ValidationError
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
auth_service = AuthenticationService()
user_service = UserManagementService()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user.
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe",
        "role": "patient",
        "hospital_id": "hospital-uuid",
        "phone": "+91-9876543210"
    }
    """
    try:
        schema = UserCreateSchema()
        data = schema.load(request.json)
        
        # Verify passwords match
        if data['password'] != data['confirm_password']:
            return APIResponse.validation_error('Passwords do not match')
        
        success, response = auth_service.register(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            hospital_id=data['hospital_id'],
            phone=data.get('phone'),
        )
        
        if success:
            return APIResponse.created(response, 'User registered successfully')
        else:
            return APIResponse.bad_request(response['message'])
    
    except ValidationError as err:
        return APIResponse.validation_error('Validation failed', err.messages)
    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and get JWT tokens.
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    """
    try:
        schema = LoginSchema()
        data = schema.load(request.json)
        
        success, response = auth_service.login(
            email=data['email'],
            password=data['password'],
        )
        
        if success:
            return APIResponse.success(response, 'Login successful')
        else:
            return APIResponse.unauthorized()
    
    except ValidationError as err:
        return APIResponse.validation_error('Validation failed', err.messages)
    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token using refresh token.
    
    Expected JSON:
    {
        "refresh_token": "token-string"
    }
    """
    try:
        data = request.json
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return APIResponse.bad_request('Refresh token required')
        
        success, response = auth_service.refresh_tokens(refresh_token)
        
        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.unauthorized()
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """
    Change user password.
    
    Expected JSON:
    {
        "old_password": "CurrentPass123!",
        "new_password": "NewSecurePass456!"
    }
    """
    try:
        data = request.json
        
        if not data.get('old_password') or not data.get('new_password'):
            return APIResponse.bad_request('Old password and new password required')
        
        success, response = auth_service.change_password(
            user_id=request.user_id,
            old_password=data['old_password'],
            new_password=data['new_password'],
        )
        
        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.bad_request(response['message'])
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current logged-in user details."""
    try:
        user = user_service.get_user(request.user_id)
        
        if not user:
            return APIResponse.not_found('User')
        
        schema = UserResponseSchema()
        response_data = schema.dump(user)
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get all users in hospital (Admin only).
    
    Query params:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = user_service.get_users_by_hospital(request.hospital_id)
        
        # Paginate
        offset = (page - 1) * per_page
        paginated_users = users[offset:offset + per_page]
        
        schema = UserResponseSchema(many=True)
        response_data = schema.dump(paginated_users)
        
        return APIResponse.paginated(response_data, page, per_page, len(users))
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID."""
    try:
        # Users can only view themselves unless admin
        if request.user_role != 'admin' and request.user_id != user_id:
            return APIResponse.forbidden()
        
        user = user_service.get_user(user_id)
        
        if not user:
            return APIResponse.not_found('User')
        
        schema = UserResponseSchema()
        response_data = schema.dump(user)
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update user details."""
    try:
        # Users can only update themselves unless admin
        if request.user_role != 'admin' and request.user_id != user_id:
            return APIResponse.forbidden()
        
        data = request.json
        
        success, response = user_service.update_user(user_id, **data)
        
        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.not_found('User')
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/users/<user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate user account (Admin only)."""
    try:
        success, response = user_service.deactivate_user(user_id)

        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.not_found('User')

    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Logout user and revoke tokens.

    Blacklists both access and refresh tokens for security.
    Clears refresh_token HTTPOnly cookie.

    Returns:
        Success message with token revocation confirmation
    """
    try:
        user_id = request.user_id
        token_jti = request.token_jti

        if not token_jti:
            return APIResponse.bad_request('Invalid token')

        # Get refresh token from cookie if available
        refresh_token = JWTHandler.get_refresh_token_from_request()

        # Blacklist access token
        try:
            access_payload = JWTHandler.decode_token(
                JWTHandler.get_token_from_request(),
                verify=False
            )
            if access_payload:
                exp_time = datetime.utcfromtimestamp(access_payload.get('exp', 0))
                TokenBlacklist.blacklist_token(
                    user_id=user_id,
                    token_jti=token_jti,
                    token_type='access',
                    expires_at=exp_time,
                    reason='logout'
                )
        except Exception as e:
            pass

        # Blacklist refresh token if present
        if refresh_token:
            try:
                refresh_payload = JWTHandler.decode_token(refresh_token)
                if refresh_payload:
                    exp_time = datetime.utcfromtimestamp(refresh_payload.get('exp', 0))
                    TokenBlacklist.blacklist_token(
                        user_id=user_id,
                        token_jti=refresh_payload.get('jti', ''),
                        token_type='refresh',
                        expires_at=exp_time,
                        reason='logout'
                    )
            except Exception as e:
                pass

        # Create response
        response = make_response(jsonify({
            'success': True,
            'message': 'Logged out successfully',
            'data': {}
        }))

        # Clear HTTPOnly cookies
        response.set_cookie(
            'access_token',
            '',
            max_age=0,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        response.set_cookie(
            'refresh_token',
            '',
            max_age=0,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        return response, 200

    except Exception as e:
        return APIResponse.internal_error(str(e))


@auth_bp.route('/refresh-cookie', methods=['POST'])
def refresh_token_from_cookie():
    """
    Refresh access token using refresh token from HTTPOnly cookie.

    This endpoint is used when refresh_token is stored in HTTPOnly cookie.
    Does not require Authorization header.

    Returns:
        New access token in JSON response and/or cookie
    """
    try:
        # Get refresh token from HTTPOnly cookie
        refresh_token = JWTHandler.get_refresh_token_from_request()

        if not refresh_token:
            return APIResponse.bad_request('Refresh token not found in cookie')

        # Validate refresh token
        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            return APIResponse.unauthorized('Invalid or expired refresh token')

        # Verify token type
        if payload.get('token_type') != 'refresh':
            return APIResponse.unauthorized('Invalid token type')

        # Check if token is blacklisted
        try:
            jti = payload.get('jti')
            if jti and TokenBlacklist.is_token_blacklisted(jti):
                return APIResponse.unauthorized('Refresh token has been revoked')
        except Exception as e:
            pass

        # Generate new access token
        user_id = payload.get('user_id')
        role = payload.get('role')
        hospital_id = payload.get('hospital_id')

        new_access_token, new_jti = JWTHandler.encode_token(
            user_id=user_id,
            role=role,
            hospital_id=hospital_id,
            token_type='access'
        )

        # Return new token in response
        response_data = {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': 900,
        }

        response = make_response(jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            'data': response_data
        }))

        # Set access_token cookie
        response.set_cookie(
            'access_token',
            new_access_token,
            max_age=900,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        return response, 200

    except Exception as e:
        return APIResponse.internal_error(str(e))
