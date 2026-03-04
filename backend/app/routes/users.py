"""
User Management Routes
Endpoints for user CRUD, role management, and profile operations.
"""
from flask import Blueprint, request
from app.utils.errors import APIResponse, ValidationError, NotFoundError, ForbiddenError
from app.utils.auth import token_required, role_required
from app.utils.helpers import Paginator, QueryFilter
from app.services.auth import UserManagementService
from app.repositories import UserRepository, DoctorRepository, HospitalRepository
from app.schemas import UserListSchema, UserDetailSchema, UserUpdateSchema

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')


@users_bp.route('', methods=['GET'])
@token_required
@role_required('admin', 'reception')
def list_users():
    """Get all users with pagination and filters."""
    try:
        paginator = Paginator(request.args)
        role = request.args.get('role')
        is_active = request.args.get('is_active', type=lambda v: v.lower() == 'true' if v else None)
        
        query_filter = QueryFilter()
        if role:
            query_filter.add_filter('role', role)
        if is_active is not None:
            query_filter.add_filter('is_active', is_active)
        
        users, total, pages = UserRepository.paginate(
            page=paginator.page,
            per_page=paginator.per_page,
            filters=query_filter.to_dict() if query_filter else {}
        )
        
        schema = UserListSchema(many=True)
        return APIResponse.success(
            schema.dump(users),
            meta={
                'total': total,
                'page': paginator.page,
                'per_page': paginator.per_page,
                'pages': pages,
                'has_next': paginator.page < pages,
                'has_prev': paginator.page > 1
            }
        )
    except Exception as e:
        return APIResponse.error(str(e), 'LIST_USERS_ERROR')


@users_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user details."""
    try:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return APIResponse.not_found('User not found')
        
        # Check authorization: admin or self
        if request.user_id != user_id and request.user_role != 'admin':
            return APIResponse.forbidden('Cannot access other user details')
        
        schema = UserDetailSchema()
        return APIResponse.success(schema.dump(user))
    except Exception as e:
        return APIResponse.error(str(e), 'GET_USER_ERROR')


@users_bp.route('/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update user profile."""
    try:
        # Check authorization
        if request.user_id != user_id and request.user_role != 'admin':
            return APIResponse.forbidden('Cannot update other user')
        
        data = request.get_json()
        schema = UserUpdateSchema()
        validated = schema.load(data, partial=True)
        
        success, user_id = UserManagementService.update_user(user_id, **validated)
        if not success:
            return APIResponse.bad_request('Failed to update user')
        
        user = UserRepository.get_by_id(user_id)
        schema = UserDetailSchema()
        return APIResponse.success(schema.dump(user))
    except ValidationError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        return APIResponse.error(str(e), 'UPDATE_USER_ERROR')


@users_bp.route('/<user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def deactivate_user(user_id):
    """Deactivate user account."""
    try:
        success = UserManagementService.deactivate_user(user_id)
        if not success:
            return APIResponse.bad_request('Failed to deactivate user')
        
        return APIResponse.success({'message': 'User deactivated successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'DEACTIVATE_USER_ERROR')


@users_bp.route('/doctors', methods=['GET'])
@token_required
def list_doctors():
    """Get list of doctors in hospital."""
    try:
        paginator = Paginator(request.args)
        hospital_id = request.hospital_id
        specialization = request.args.get('specialization')
        available_only = request.args.get('available_only', type=lambda v: v.lower() == 'true' if v else False)
        
        query_filter = {}
        if specialization:
            query_filter['specialization'] = specialization
        if available_only:
            query_filter['is_available'] = True
        
        doctors, total, pages = DoctorRepository.filter(
            hospital_id=hospital_id,
            **query_filter
        ).paginate(page=paginator.page, per_page=paginator.per_page)
        
        from app.schemas import DoctorListSchema
        schema = DoctorListSchema(many=True)
        return APIResponse.success(
            schema.dump(doctors),
            meta={
                'total': total,
                'page': paginator.page,
                'per_page': paginator.per_page,
                'pages': pages
            }
        )
    except Exception as e:
        return APIResponse.error(str(e), 'LIST_DOCTORS_ERROR')


@users_bp.route('/nurses', methods=['GET'])
@token_required
@role_required('admin', 'reception')
def list_nurses():
    """Get list of nurses in hospital."""
    try:
        paginator = Paginator(request.args)
        hospital_id = request.hospital_id
        
        users, total, pages = UserRepository.paginate(
            page=paginator.page,
            per_page=paginator.per_page,
            filters={'role': 'nurse', 'hospital_id': hospital_id, 'is_active': True}
        )
        
        schema = UserListSchema(many=True)
        return APIResponse.success(
            schema.dump(users),
            meta={'total': total, 'page': paginator.page, 'per_page': paginator.per_page, 'pages': pages}
        )
    except Exception as e:
        return APIResponse.error(str(e), 'LIST_NURSES_ERROR')


@users_bp.route('/staff', methods=['GET'])
@token_required
@role_required('admin')
def list_staff():
    """Get list of all staff in hospital."""
    try:
        paginator = Paginator(request.args)
        hospital_id = request.hospital_id
        
        users, total, pages = UserRepository.paginate(
            page=paginator.page,
            per_page=paginator.per_page,
            filters={'hospital_id': hospital_id, 'is_active': True}
        )
        
        schema = UserListSchema(many=True)
        return APIResponse.success(
            schema.dump(users),
            meta={'total': total, 'page': paginator.page, 'per_page': paginator.per_page, 'pages': pages}
        )
    except Exception as e:
        return APIResponse.error(str(e), 'LIST_STAFF_ERROR')


@users_bp.route('/<user_id>/reset-password', methods=['POST'])
@token_required
@role_required('admin')
def reset_password(user_id):
    """Admin reset user password."""
    try:
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password or len(new_password) < 8:
            return APIResponse.bad_request('Password must be at least 8 characters')
        
        from app.utils.auth import PasswordHandler
        success = UserRepository.update(user_id, {
            'password_hash': PasswordHandler.hash_password(new_password)
        })
        
        if not success:
            return APIResponse.bad_request('Failed to reset password')
        
        return APIResponse.success({'message': 'Password reset successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'RESET_PASSWORD_ERROR')


@users_bp.route('/<user_id>/verify', methods=['POST'])
@token_required
@role_required('admin')
def verify_user(user_id):
    """Verify user account (activate)."""
    try:
        success = UserRepository.update(user_id, {'is_active': True})
        if not success:
            return APIResponse.bad_request('Failed to verify user')
        
        return APIResponse.success({'message': 'User verified successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'VERIFY_USER_ERROR')
