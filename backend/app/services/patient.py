"""
Patient Management Services.
"""
from typing import Optional, Tuple, Dict, List
from datetime import datetime, date
from app.extensions import db
from app.utils import get_logger, IDGenerator
from app.repositories import PatientRepository
from app.models import Patient, User, MedicalRecord, Appointment


logger = get_logger(__name__)


class PatientService:
    """Handles patient management operations."""
    
    def __init__(self):
        self.patient_repo = PatientRepository()
    
    def create_patient(self, user_id: str, hospital_id: str, date_of_birth: date,
                       gender: str, blood_group: str = None, weight: float = None,
                       height: float = None, **kwargs) -> Tuple[bool, Dict]:
        """
        Create new patient.
        
        Args:
            user_id: Associated user ID
            hospital_id: Hospital ID
            date_of_birth: Patient date of birth
            gender: Patient gender
            blood_group: Blood group
            weight: Weight in kg
            height: Height in cm
            **kwargs: Additional fields
            
        Returns:
            (success, response_dict) tuple
        """
        # Check user exists
        user = User.query.get(user_id)
        if not user:
            return False, {'message': 'User not found'}
        
        try:
            # Generate unique patient ID
            patient_id_number = IDGenerator.generate_patient_id(hospital_id[:3].upper())
            
            # Check ID uniqueness
            while self.patient_repo.get_by_patient_id_number(patient_id_number):
                patient_id_number = IDGenerator.generate_patient_id(hospital_id[:3].upper())
            
            patient = Patient(
                user_id=user_id,
                hospital_id=hospital_id,
                patient_id_number=patient_id_number,
                date_of_birth=date_of_birth,
                gender=gender,
                blood_group=blood_group,
                weight=weight,
                height=height,
                **kwargs
            )
            
            db.session.add(patient)
            db.session.commit()
            
            logger.info(f"Patient created: {patient_id_number}")
            
            return True, {
                'message': 'Patient registered successfully',
                'patient_id': patient.id,
                'patient_id_number': patient.patient_id_number,
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating patient: {str(e)}")
            return False, {'message': 'Patient registration failed'}
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID."""
        return self.patient_repo.get_by_id(patient_id)
    
    def get_patient_by_id_number(self, patient_id_number: str) -> Optional[Patient]:
        """Get patient by patient ID number."""
        return self.patient_repo.get_by_patient_id_number(patient_id_number)
    
    def get_hospital_patients(self, hospital_id: str, page: int = 1,
                             per_page: int = 20) -> Tuple[List[Patient], int]:
        """Get all patients in hospital with pagination."""
        offset = (page - 1) * per_page
        patients = self.patient_repo.get_by_hospital(hospital_id, per_page, offset)
        total = self.patient_repo.count_by_hospital(hospital_id)
        return patients, total
    
    def update_patient(self, patient_id: str, **kwargs) -> Tuple[bool, Dict]:
        """Update patient information."""
        try:
            patient = self.patient_repo.update(patient_id, **kwargs)
            if not patient:
                return False, {'message': 'Patient not found'}
            
            logger.info(f"Patient updated: {patient_id}")
            return True, {'message': 'Patient updated successfully'}
        
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            return False, {'message': 'Update failed'}
    
    def add_medical_record(self, patient_id: str, doctor_id: str, record_type: str,
                          description: str = None, file_path: str = None,
                          file_url: str = None, file_type: str = None,
                          file_size: int = None, **kwargs) -> Tuple[bool, Dict]:
        """
        Add medical record for patient.
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID creating record
            record_type: Type of record (lab_report, scan, xray, etc.)
            description: Record description
            file_path: Local file path
            file_url: Cloud storage URL (S3, Firebase)
            file_type: File MIME type
            file_size: File size in bytes
            **kwargs: Additional fields (diagnosis, notes)
            
        Returns:
            (success, response_dict) tuple
        """
        patient = self.get_patient(patient_id)
        if not patient:
            return False, {'message': 'Patient not found'}
        
        try:
            record = MedicalRecord(
                patient_id=patient_id,
                doctor_id=doctor_id,
                record_type=record_type,
                description=description,
                file_path=file_path,
                file_url=file_url,
                file_type=file_type,
                file_size=file_size,
                **kwargs
            )
            
            db.session.add(record)
            db.session.commit()
            
            logger.info(f"Medical record added for patient: {patient_id}")
            
            return True, {
                'message': 'Medical record added successfully',
                'record_id': record.id,
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding medical record: {str(e)}")
            return False, {'message': 'Record addition failed'}
    
    def get_medical_records(self, patient_id: str) -> List[MedicalRecord]:
        """Get all medical records for patient."""
        try:
            return MedicalRecord.query.filter_by(
                patient_id=patient_id,
                deleted_at=None
            ).order_by(MedicalRecord.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting medical records: {str(e)}")
            return []
    
    def delete_patient(self, patient_id: str) -> Tuple[bool, Dict]:
        """Soft delete patient."""
        try:
            patient = self.get_patient(patient_id)
            if not patient:
                return False, {'message': 'Patient not found'}
            
            patient.soft_delete()
            db.session.commit()
            
            logger.info(f"Patient soft deleted: {patient_id}")
            return True, {'message': 'Patient deleted successfully'}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting patient: {str(e)}")
            return False, {'message': 'Deletion failed'}
    
    def get_patient_statistics(self, hospital_id: str) -> Dict:
        """Get patient statistics for hospital."""
        try:
            total_patients = self.patient_repo.count_by_hospital(hospital_id)
            
            # Get appointment count
            appointments = Appointment.query.filter_by(hospital_id=hospital_id).count()
            
            # Get today's appointments
            today = date.today()
            today_appointments = Appointment.query.filter(
                Appointment.hospital_id == hospital_id,
                Appointment.appointment_date == today
            ).count()
            
            return {
                'total_patients': total_patients,
                'total_appointments': appointments,
                'today_appointments': today_appointments,
            }
        
        except Exception as e:
            logger.error(f"Error getting patient statistics: {str(e)}")
            return {}
