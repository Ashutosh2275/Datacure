"""
Repository pattern for data access layer.
Provides abstraction over SQLAlchemy ORM queries.
"""
from typing import List, Optional, Any, Dict, Tuple
from app.extensions import db
from app.utils import get_logger

logger = get_logger(__name__)


class BaseRepository:
    """Base repository with common CRUD operations."""
    
    def __init__(self, model):
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def create(self, **kwargs) -> Any:
        """Create new entity."""
        try:
            entity = self.model(**kwargs)
            db.session.add(entity)
            db.session.commit()
            logger.info(f"Created {self.model.__name__}: {entity.id}")
            return entity
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Get entity by ID."""
        try:
            return self.model.query.get(entity_id)
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID: {str(e)}")
            return None
    
    def get_all(self, limit: int = None, offset: int = 0) -> List[Any]:
        """Get all entities."""
        try:
            query = self.model.query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            return []
    
    def update(self, entity_id: str, **kwargs) -> Optional[Any]:
        """Update entity."""
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                logger.warning(f"{self.model.__name__} not found: {entity_id}")
                return None
            
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            db.session.commit()
            logger.info(f"Updated {self.model.__name__}: {entity_id}")
            return entity
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise
    
    def delete(self, entity_id: str) -> bool:
        """Delete entity."""
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                return False
            
            db.session.delete(entity)
            db.session.commit()
            logger.info(f"Deleted {self.model.__name__}: {entity_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {str(e)}")
            raise
    
    def count(self, **filters) -> int:
        """Count entities matching filters."""
        try:
            query = self.model.query
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.filter(getattr(self.model, key) == value)
            return query.count()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            return 0


class UserRepository(BaseRepository):
    """Repository for User model."""
    
    def __init__(self):
        from app.models import User
        super().__init__(User)
    
    def get_by_email(self, email: str) -> Optional[Any]:
        """Get user by email."""
        try:
            return self.model.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    def get_by_hospital_and_role(self, hospital_id: str, role: str) -> List[Any]:
        """Get users by hospital and role."""
        try:
            return self.model.query.filter_by(
                hospital_id=hospital_id,
                role=role,
                is_active=True
            ).all()
        except Exception as e:
            logger.error(f"Error getting users by hospital and role: {str(e)}")
            return []


class PatientRepository(BaseRepository):
    """Repository for Patient model."""
    
    def __init__(self):
        from app.models import Patient
        super().__init__(Patient)
    
    def get_by_patient_id_number(self, patient_id_number: str) -> Optional[Any]:
        """Get patient by patient ID number."""
        try:
            return self.model.query.filter_by(patient_id_number=patient_id_number).first()
        except Exception as e:
            logger.error(f"Error getting patient by ID number: {str(e)}")
            return None
    
    def get_by_hospital(self, hospital_id: str, limit: int = None, offset: int = 0) -> List[Any]:
        """Get patients by hospital."""
        try:
            query = self.model.query.filter_by(hospital_id=hospital_id).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting patients by hospital: {str(e)}")
            return []
    
    def count_by_hospital(self, hospital_id: str) -> int:
        """Count patients in hospital."""
        try:
            return self.model.query.filter_by(hospital_id=hospital_id).count()
        except Exception as e:
            logger.error(f"Error counting patients: {str(e)}")
            return 0


class DoctorRepository(BaseRepository):
    """Repository for Doctor model."""
    
    def __init__(self):
        from app.models import Doctor
        super().__init__(Doctor)
    
    def get_by_specialization(self, hospital_id: str, specialization: str) -> List[Any]:
        """Get doctors by specialization."""
        try:
            return self.model.query.filter_by(
                hospital_id=hospital_id,
                specialization=specialization
            ).all()
        except Exception as e:
            logger.error(f"Error getting doctors by specialization: {str(e)}")
            return []
    
    def get_available_doctors(self, hospital_id: str) -> List[Any]:
        """Get available doctors."""
        try:
            return self.model.query.filter_by(
                hospital_id=hospital_id,
                availability_status='available'
            ).all()
        except Exception as e:
            logger.error(f"Error getting available doctors: {str(e)}")
            return []


class AppointmentRepository(BaseRepository):
    """Repository for Appointment model."""
    
    def __init__(self):
        from app.models import Appointment
        super().__init__(Appointment)
    
    def get_by_patient(self, patient_id: str, limit: int = None) -> List[Any]:
        """Get appointments for patient."""
        try:
            query = self.model.query.filter_by(patient_id=patient_id).order_by(
                self.model.appointment_date.desc()
            )
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting appointments for patient: {str(e)}")
            return []
    
    def get_by_doctor(self, doctor_id: str, date = None) -> List[Any]:
        """Get appointments for doctor."""
        try:
            query = self.model.query.filter_by(doctor_id=doctor_id)
            if date:
                query = query.filter(self.model.appointment_date == date)
            return query.order_by(self.model.start_time).all()
        except Exception as e:
            logger.error(f"Error getting appointments for doctor: {str(e)}")
            return []
    
    def get_today_appointments(self, hospital_id: str, date = None) -> List[Any]:
        """Get today's appointments."""
        from datetime import date as date_class
        if date is None:
            date = date_class.today()
        
        try:
            return self.model.query.filter(
                self.model.hospital_id == hospital_id,
                self.model.appointment_date == date
            ).order_by(self.model.start_time).all()
        except Exception as e:
            logger.error(f"Error getting today's appointments: {str(e)}")
            return []


class BillingRepository(BaseRepository):
    """Repository for Billing model."""
    
    def __init__(self):
        from app.models import Billing
        super().__init__(Billing)
    
    def get_by_patient(self, patient_id: str) -> List[Any]:
        """Get billing records for patient."""
        try:
            return self.model.query.filter_by(patient_id=patient_id).order_by(
                self.model.invoice_date.desc()
            ).all()
        except Exception as e:
            logger.error(f"Error getting billing records: {str(e)}")
            return []
    
    def get_pending_payments(self, hospital_id: str) -> List[Any]:
        """Get pending payment invoices."""
        try:
            return self.model.query.filter_by(
                hospital_id=hospital_id,
                status='pending'
            ).all()
        except Exception as e:
            logger.error(f"Error getting pending payments: {str(e)}")
            return []


class InventoryRepository(BaseRepository):
    """Repository for inventory models."""
    
    def __init__(self):
        from app.models import MedicineInventory
        super().__init__(MedicineInventory)
    
    def get_expired_medicines(self, hospital_id: str) -> List[Any]:
        """Get expired medicines."""
        from datetime import date
        try:
            return self.model.query.filter(
                self.model.hospital_id == hospital_id,
                self.model.expiry_date < date.today()
            ).all()
        except Exception as e:
            logger.error(f"Error getting expired medicines: {str(e)}")
            return []
    
    def get_low_stock_medicines(self, hospital_id: str) -> List[Any]:
        """Get medicines with low stock."""
        try:
            return self.model.query.filter(
                self.model.hospital_id == hospital_id,
                self.model.quantity <= self.model.reorder_level
            ).all()
        except Exception as e:
            logger.error(f"Error getting low stock medicines: {str(e)}")
            return []


class HospitalRepository(BaseRepository):
    """Repository for hospital management."""
    
    def __init__(self):
        from app.models import Hospital
        super().__init__(Hospital)
    
    def get_by_name(self, name: str) -> Optional[Any]:
        """Get hospital by name."""
        try:
            return self.model.query.filter_by(name=name).first()
        except Exception as e:
            logger.error(f"Error getting hospital by name: {str(e)}")
            return None
    
    def get_active_hospitals(self) -> List[Any]:
        """Get all active hospitals."""
        try:
            return self.model.query.filter_by(is_active=True).all()
        except Exception as e:
            logger.error(f"Error getting active hospitals: {str(e)}")
            return []


class BedRepository(BaseRepository):
    """Repository for Bed model."""
    
    def __init__(self):
        from app.models import Bed
        super().__init__(Bed)
    
    def get_available_beds(self, ward_id: str) -> List[Any]:
        """Get available beds in ward."""
        try:
            return self.model.query.filter_by(
                ward_id=ward_id,
                status='available'
            ).all()
        except Exception as e:
            logger.error(f"Error getting available beds: {str(e)}")
            return []
    
    def get_occupied_beds(self, ward_id: str) -> List[Any]:
        """Get occupied beds in ward."""
        try:
            return self.model.query.filter_by(
                ward_id=ward_id,
                status='occupied'
            ).all()
        except Exception as e:
            logger.error(f"Error getting occupied beds: {str(e)}")
            return []


class MedicineRepository(BaseRepository):
    """Repository for medicine/inventory management."""
    
    def __init__(self):
        from app.models import MedicineInventory
        super().__init__(MedicineInventory)
    
    def get_by_name(self, name: str, hospital_id: str) -> Optional[Any]:
        """Get medicine by name."""
        try:
            return self.model.query.filter_by(name=name, hospital_id=hospital_id).first()
        except Exception as e:
            logger.error(f"Error getting medicine by name: {str(e)}")
            return None


class WardRepository(BaseRepository):
    """Repository for ward management."""
    
    def __init__(self):
        from app.models import Ward
        super().__init__(Ward)
    
    def get_by_name(self, name: str, hospital_id: str) -> Optional[Any]:
        """Get ward by name."""
        try:
            return self.model.query.filter_by(name=name, hospital_id=hospital_id).first()
        except Exception as e:
            logger.error(f"Error getting ward by name: {str(e)}")
            return None
    
    def get_available_beds_count(self, ward_id: str) -> int:
        """Get count of available beds in ward."""
        try:
            from app.models import Bed
            return Bed.query.filter_by(ward_id=ward_id, status='available').count()
        except Exception as e:
            logger.error(f"Error getting available beds count: {str(e)}")
            return 0


class AuditLogRepository(BaseRepository):
    """Repository for audit logging."""
    
    def __init__(self):
        from app.models import AuditLog
        super().__init__(AuditLog)
    
    def get_user_logs(self, user_id: str, limit: int = 100) -> List[Any]:
        """Get audit logs for a user."""
        try:
            return self.model.query.filter_by(user_id=user_id).order_by(
                self.model.created_at.desc()
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting user logs: {str(e)}")
            return []
    
    def get_resource_logs(self, resource_type: str, resource_id: str, limit: int = 100) -> List[Any]:
        """Get audit logs for a resource."""
        try:
            return self.model.query.filter_by(
                resource_type=resource_type,
                resource_id=resource_id
            ).order_by(self.model.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting resource logs: {str(e)}")
            return []

