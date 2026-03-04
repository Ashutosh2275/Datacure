"""
Pagination, validation, and helper utilities.
"""
from flask import request
from typing import Tuple, List, Any, Optional
from datetime import datetime, date


class Paginator:
    """Handles pagination for list endpoints."""
    
    @staticmethod
    def get_pagination_params() -> Tuple[int, int]:
        """
        Extract pagination parameters from request.
        
        Returns:
            (page, per_page) tuple with defaults
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate values
        page = max(1, page)
        per_page = max(1, min(per_page, 100))  # Cap at 100 items per page
        
        return page, per_page
    
    @staticmethod
    def paginate_query(query, page: int, per_page: int):
        """
        Apply pagination to SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query object
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated query result with total count
        """
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return items, total


class QueryFilter:
    """Handles filtering and sorting for list endpoints."""
    
    @staticmethod
    def apply_filters(query, model, filters: dict):
        """
        Apply filters to SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query object
            model: SQLAlchemy model class
            filters: Dictionary of filter field:value pairs
            
        Returns:
            Filtered query object
        """
        for field, value in filters.items():
            if hasattr(model, field) and value is not None:
                if isinstance(value, str) and '%' in value:
                    # LIKE filter for string fields
                    query = query.filter(getattr(model, field).ilike(value))
                else:
                    # Exact match
                    query = query.filter(getattr(model, field) == value)
        
        return query
    
    @staticmethod
    def apply_sorting(query, model, sort_by: str, order: str = 'asc'):
        """
        Apply sorting to SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query object
            model: SQLAlchemy model class
            sort_by: Field to sort by
            order: 'asc' or 'desc'
            
        Returns:
            Sorted query object
        """
        if hasattr(model, sort_by):
            column = getattr(model, sort_by)
            if order.lower() == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        
        return query


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        import re
        pattern = r'^(\+91|0)?[6-9]\d{9}$'  # Indian phone format
        return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None
    
    @staticmethod
    def validate_date(date_str: str, format: str = '%Y-%m-%d') -> bool:
        """Validate date format."""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Returns:
            (is_strong, message) tuple
        """
        if len(password) < 8:
            return False, 'Password must be at least 8 characters long'
        
        import re
        if not re.search(r'[a-z]', password):
            return False, 'Password must contain lowercase letters'
        
        if not re.search(r'[A-Z]', password):
            return False, 'Password must contain uppercase letters'
        
        if not re.search(r'\d', password):
            return False, 'Password must contain digits'
        
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            return False, 'Password must contain special characters'
        
        return True, 'Password is strong'
    
    @staticmethod
    def validate_gst_number(gst: str) -> bool:
        """Validate Indian GST number format."""
        import re
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[0-9A-Z]{1}$'
        return re.match(pattern, gst.upper()) is not None


class DataTransformer:
    """Data transformation utilities."""
    
    @staticmethod
    def to_dict(obj, exclude_fields: List[str] = None) -> dict:
        """
        Convert SQLAlchemy model to dictionary.
        
        Args:
            obj: SQLAlchemy model instance
            exclude_fields: Fields to exclude
            
        Returns:
            Dictionary representation
        """
        if exclude_fields is None:
            exclude_fields = []
        
        result = {}
        for column in obj.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(obj, column.name)
                if value is None:
                    result[column.name] = None
                elif isinstance(value, (datetime, date)):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
        
        return result
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number."""
        digits_only = ''.join(filter(str.isdigit, phone))
        if len(digits_only) == 10:
            return f"+91-{digits_only[:5]}-{digits_only[5:]}"
        elif len(digits_only) == 12 and digits_only.startswith('91'):
            return f"+{digits_only[:2]}-{digits_only[2:7]}-{digits_only[7:]}"
        return phone
    
    @staticmethod
    def format_date(date_obj: Optional[date], format: str = '%d-%m-%Y') -> Optional[str]:
        """Format date object."""
        if date_obj is None:
            return None
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj).date()
        return date_obj.strftime(format)
    
    @staticmethod
    def format_currency(amount: float, decimals: int = 2) -> str:
        """Format amount as currency."""
        return f"₹{amount:,.{decimals}f}"


class IDGenerator:
    """Utility for generating unique IDs."""
    
    @staticmethod
    def generate_patient_id(hospital_code: str) -> str:
        """Generate unique patient ID."""
        import uuid
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_suffix = str(uuid.uuid4()).split('-')[0].upper()[:4]
        return f"PAT-{hospital_code}-{timestamp}-{unique_suffix}"
    
    @staticmethod
    def generate_invoice_number(hospital_code: str, year: Optional[int] = None) -> str:
        """Generate unique invoice number."""
        if year is None:
            year = datetime.utcnow().year
        
        import uuid
        sequential = str(uuid.uuid4().int)[:5]
        return f"INV-{hospital_code}-{year}-{sequential}"
    
    @staticmethod
    def generate_prescription_number(hospital_code: str) -> str:
        """Generate unique prescription number."""
        import uuid
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_suffix = str(uuid.uuid4()).split('-')[0].upper()[:4]
        return f"RX-{hospital_code}-{timestamp}-{unique_suffix}"
    
    @staticmethod
    def generate_order_number(hospital_code: str) -> str:
        """Generate unique purchase order number."""
        import uuid
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_suffix = str(uuid.uuid4()).split('-')[0].upper()[:6]
        return f"PO-{hospital_code}-{timestamp}-{unique_suffix}"
