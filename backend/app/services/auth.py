"""
Authentication and User Management Services.
"""
from typing import Optional, Tuple, Dict
from datetime import timedelta

from app.extensions import db
from app.utils import (
    JWTHandler,
    PasswordHandler,
    get_logger,
    InputValidator,
    IDGenerator,
)
from app.repositories import UserRepository
from app.models import User, Hospital, RoleEnum


logger = get_logger(__name__)


class AuthenticationService:
    """Handles user authentication and JWT token management."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def register(self, email: str, password: str, first_name: str, last_name: str,
                 role: str, hospital_id: str, phone: str = None) -> Tuple[bool, Dict]:
        """
        Register new user.
        
        Args:
            email: User email
            password: User password
            first_name: First name
            last_name: Last name
            role: User role
            hospital_id: Hospital ID
            phone: User phone
            
        Returns:
            (success, response_dict) tuple
        """
        # Validate inputs
        if not InputValidator.validate_email(email):
            return False, {'message': 'Invalid email format'}
        
        is_strong, msg = InputValidator.validate_password_strength(password)
        if not is_strong:
            return False, {'message': msg}
        
        # Check if user already exists
        if self.user_repo.get_by_email(email):
            return False, {'message': 'Email already registered'}
        
        # Check hospital exists
        hospital = Hospital.query.get(hospital_id)
        if not hospital:
            return False, {'message': 'Hospital not found'}
        
        try:
            # Create new user
            user = User(
                email=email,
                password_hash=PasswordHandler.hash_password(password),
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=RoleEnum(role),
                hospital_id=hospital_id,
                is_active=True,
            )
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"User registered: {email} with role {role}")
            
            return True, {
                'message': 'User registered successfully',
                'user_id': user.id,
                'email': user.email,
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            return False, {'message': 'Registration failed'}
    
    def login(self, email: str, password: str) -> Tuple[bool, Dict]:
        """
        Authenticate user and generate tokens.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            (success, response_dict) tuple
        """
        user = self.user_repo.get_by_email(email)
        
        if not user:
            logger.warning(f"Login attempt for non-existent user: {email}")
            return False, {'message': 'Invalid credentials'}
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            return False, {'message': 'User account is inactive'}
        
        if not PasswordHandler.verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt for: {email}")
            return False, {'message': 'Invalid credentials'}
        
        try:
            # Generate tokens
            access_token = JWTHandler.encode_token(
                user_id=user.id,
                role=user.role.value,
                hospital_id=user.hospital_id,
                token_type='access'
            )
            
            refresh_token = JWTHandler.encode_token(
                user_id=user.id,
                role=user.role.value,
                hospital_id=user.hospital_id,
                token_type='refresh'
            )
            
            logger.info(f"User logged in: {email}")
            
            return True, {
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.value,
                    'hospital_id': user.hospital_id,
                }
            }
        
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            return False, {'message': 'Login failed'}
    
    def refresh_tokens(self, refresh_token: str) -> Tuple[bool, Dict]:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            (success, response_dict) tuple
        """
        payload = JWTHandler.decode_token(refresh_token)
        
        if not payload or payload.get('token_type') != 'refresh':
            return False, {'message': 'Invalid refresh token'}
        
        try:
            user_id = payload.get('user_id')
            user = User.query.get(user_id)
            
            if not user:
                return False, {'message': 'User not found'}
            
            access_token = JWTHandler.encode_token(
                user_id=user.id,
                role=user.role.value,
                hospital_id=user.hospital_id,
                token_type='access'
            )
            
            return True, {
                'message': 'Token refreshed',
                'access_token': access_token,
                'token_type': 'Bearer',
            }
        
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return False, {'message': 'Token refresh failed'}
    
    def change_password(self, user_id: str, old_password: str,
                       new_password: str) -> Tuple[bool, Dict]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            (success, response_dict) tuple
        """
        user = User.query.get(user_id)
        
        if not user:
            return False, {'message': 'User not found'}
        
        if not PasswordHandler.verify_password(old_password, user.password_hash):
            return False, {'message': 'Current password is incorrect'}
        
        is_strong, msg = InputValidator.validate_password_strength(new_password)
        if not is_strong:
            return False, {'message': msg}
        
        try:
            user.password_hash = PasswordHandler.hash_password(new_password)
            db.session.commit()
            
            logger.info(f"Password changed for user: {user_id}")
            return True, {'message': 'Password changed successfully'}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password change error: {str(e)}")
            return False, {'message': 'Password change failed'}


class UserManagementService:
    """Handles user management operations."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_by_id(user_id)
    
    def get_users_by_hospital(self, hospital_id: str) -> list:
        """Get all users in hospital."""
        try:
            return User.query.filter_by(
                hospital_id=hospital_id,
                is_active=True
            ).all()
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            return []
    
    def get_doctors(self, hospital_id: str) -> list:
        """Get all doctors in hospital."""
        return self.user_repo.get_by_hospital_and_role(hospital_id, 'doctor')
    
    def get_nurses(self, hospital_id: str) -> list:
        """Get all nurses in hospital."""
        return self.user_repo.get_by_hospital_and_role(hospital_id, 'nurse')
    
    def get_staff(self, hospital_id: str) -> list:
        """Get all staff in hospital."""
        return self.user_repo.get_by_hospital_and_role(hospital_id, 'staff')
    
    def update_user(self, user_id: str, **kwargs) -> Tuple[bool, Dict]:
        """Update user details."""
        try:
            user = self.user_repo.update(user_id, **kwargs)
            if not user:
                return False, {'message': 'User not found'}
            
            return True, {
                'message': 'User updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return False, {'message': 'Update failed'}
    
    def deactivate_user(self, user_id: str) -> Tuple[bool, Dict]:
        """Deactivate user account."""
        try:
            user = self.user_repo.update(user_id, is_active=False)
            if not user:
                return False, {'message': 'User not found'}
            
            logger.info(f"User deactivated: {user_id}")
            return True, {'message': 'User deactivated successfully'}
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return False, {'message': 'Deactivation failed'}
    
    def delete_user(self, user_id: str) -> Tuple[bool, Dict]:
        """Soft delete user."""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, {'message': 'User not found'}
            
            user.soft_delete()
            db.session.commit()
            
            logger.info(f"User soft deleted: {user_id}")
            return True, {'message': 'User deleted successfully'}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            return False, {'message': 'Deletion failed'}
