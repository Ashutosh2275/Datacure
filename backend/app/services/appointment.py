"""
Doctor, Appointment, and Prescription Services.
"""
from typing import Optional, Tuple, Dict, List
from datetime import datetime, date, time
from app.extensions import db
from app.utils import get_logger, IDGenerator
from app.repositories import DoctorRepository, AppointmentRepository
from app.models import (
    Doctor, User, DoctorSlot, Appointment, Prescription, PrescriptionItem,
    Medicine, AppointmentStatusEnum, PrescriptionStatusEnum
)


logger = get_logger(__name__)


# ==================== DOCTOR SERVICE ====================

class DoctorService:
    """Handles doctor management."""
    
    def __init__(self):
        self.doctor_repo = DoctorRepository()
    
    def create_doctor(self, user_id: str, hospital_id: str, license_number: str,
                      specialization: str, experience_years: int = 0,
                      consultation_fee: float = 0, **kwargs) -> Tuple[bool, Dict]:
        """Create doctor profile."""
        user = User.query.get(user_id)
        if not user:
            return False, {'message': 'User not found'}
        
        # Check license uniqueness
        if Doctor.query.filter_by(license_number=license_number).first():
            return False, {'message': 'License number already exists'}
        
        try:
            doctor = Doctor(
                user_id=user_id,
                hospital_id=hospital_id,
                license_number=license_number,
                specialization=specialization,
                experience_years=experience_years,
                consultation_fee=consultation_fee,
                **kwargs
            )
            
            db.session.add(doctor)
            db.session.commit()
            
            logger.info(f"Doctor created: {license_number}")
            return True, {'message': 'Doctor profile created', 'doctor_id': doctor.id}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating doctor: {str(e)}")
            return False, {'message': 'Creation failed'}
    
    def get_doctor(self, doctor_id: str) -> Optional[Doctor]:
        """Get doctor by ID."""
        return self.doctor_repo.get_by_id(doctor_id)
    
    def get_doctors_by_specialization(self, hospital_id: str,
                                      specialization: str) -> List[Doctor]:
        """Get doctors by specialization."""
        return self.doctor_repo.get_by_specialization(hospital_id, specialization)
    
    def get_available_doctors(self, hospital_id: str) -> List[Doctor]:
        """Get available doctors."""
        return self.doctor_repo.get_available_doctors(hospital_id)
    
    def update_doctor(self, doctor_id: str, **kwargs) -> Tuple[bool, Dict]:
        """Update doctor information."""
        try:
            doctor = self.doctor_repo.update(doctor_id, **kwargs)
            if not doctor:
                return False, {'message': 'Doctor not found'}
            return True, {'message': 'Doctor updated successfully'}
        except Exception as e:
            logger.error(f"Error updating doctor: {str(e)}")
            return False, {'message': 'Update failed'}
    
    def create_appointment_slot(self, doctor_id: str, slot_date: date,
                               start_time: time, end_time: time,
                               capacity: int = 1) -> Tuple[bool, Dict]:
        """Create appointment slot for doctor."""
        doctor = self.get_doctor(doctor_id)
        if not doctor:
            return False, {'message': 'Doctor not found'}
        
        try:
            slot = DoctorSlot(
                doctor_id=doctor_id,
                slot_date=slot_date,
                start_time=start_time,
                end_time=end_time,
                capacity=capacity,
            )
            
            db.session.add(slot)
            db.session.commit()
            
            logger.info(f"Slot created for doctor {doctor_id}")
            return True, {'message': 'Slot created', 'slot_id': slot.id}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating slot: {str(e)}")
            return False, {'message': 'Slot creation failed'}
    
    def get_available_slots(self, doctor_id: str, date_from: date = None) -> List[DoctorSlot]:
        """Get available slots for doctor."""
        try:
            query = DoctorSlot.query.filter_by(doctor_id=doctor_id, is_booked=False)
            if date_from:
                query = query.filter(DoctorSlot.slot_date >= date_from)
            return query.order_by(DoctorSlot.slot_date, DoctorSlot.start_time).all()
        except Exception as e:
            logger.error(f"Error getting slots: {str(e)}")
            return []


# ==================== APPOINTMENT SERVICE ====================

class AppointmentService:
    """Handles appointment management."""
    
    def __init__(self):
        self.appointment_repo = AppointmentRepository()
    
    def book_appointment(self, patient_id: str, doctor_id: str, hospital_id: str,
                        appointment_date: date, start_time: time, end_time: time,
                        appointment_type: str = 'consultation',
                        chief_complaint: str = None, is_emergency: bool = False,
                        is_telemedicine: bool = False) -> Tuple[bool, Dict]:
        """Book new appointment."""
        try:
            # Check patient exists
            from app.models import Patient
            if not Patient.query.get(patient_id):
                return False, {'message': 'Patient not found'}
            
            # Check doctor exists
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return False, {'message': 'Doctor not found'}
            
            # Check for conflicts
            conflict = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_([AppointmentStatusEnum.SCHEDULED, 
                                        AppointmentStatusEnum.CONFIRMED])
            ).first()
            
            if conflict:
                return False, {'message': 'Time slot not available'}
            
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                hospital_id=hospital_id,
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=end_time,
                appointment_type=appointment_type,
                chief_complaint=chief_complaint,
                is_emergency=is_emergency,
                is_telemedicine=is_telemedicine,
                status=AppointmentStatusEnum.SCHEDULED,
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            logger.info(f"Appointment booked: {appointment.id}")
            
            return True, {
                'message': 'Appointment booked successfully',
                'appointment_id': appointment.id,
                'appointment_date': str(appointment_date),
                'time': f"{start_time} - {end_time}",
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error booking appointment: {str(e)}")
            return False, {'message': 'Booking failed'}
    
    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID."""
        return self.appointment_repo.get_by_id(appointment_id)
    
    def get_patient_appointments(self, patient_id: str, limit: int = None) -> List[Appointment]:
        """Get appointments for patient."""
        return self.appointment_repo.get_by_patient(patient_id, limit)
    
    def get_doctor_appointments(self, doctor_id: str, appointment_date: date = None) -> List[Appointment]:
        """Get appointments for doctor."""
        return self.appointment_repo.get_by_doctor(doctor_id, appointment_date)
    
    def get_today_appointments(self, hospital_id: str) -> List[Appointment]:
        """Get today's appointments."""
        return self.appointment_repo.get_today_appointments(hospital_id)
    
    def reschedule_appointment(self, appointment_id: str, new_date: date,
                              new_start_time: time, new_end_time: time) -> Tuple[bool, Dict]:
        """Reschedule appointment."""
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False, {'message': 'Appointment not found'}
        
        try:
            appointment.appointment_date = new_date
            appointment.start_time = new_start_time
            appointment.end_time = new_end_time
            appointment.status = AppointmentStatusEnum.RESCHEDULED
            
            db.session.commit()
            logger.info(f"Appointment rescheduled: {appointment_id}")
            
            return True, {'message': 'Appointment rescheduled successfully'}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error rescheduling: {str(e)}")
            return False, {'message': 'Reschedule failed'}
    
    def cancel_appointment(self, appointment_id: str) -> Tuple[bool, Dict]:
        """Cancel appointment."""
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False, {'message': 'Appointment not found'}
        
        try:
            appointment.status = AppointmentStatusEnum.CANCELLED
            db.session.commit()
            logger.info(f"Appointment cancelled: {appointment_id}")
            return True, {'message': 'Appointment cancelled successfully'}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cancelling: {str(e)}")
            return False, {'message': 'Cancellation failed'}
    
    def complete_appointment(self, appointment_id: str) -> Tuple[bool, Dict]:
        """Mark appointment as completed."""
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False, {'message': 'Appointment not found'}
        
        try:
            appointment.status = AppointmentStatusEnum.COMPLETED
            db.session.commit()
            return True, {'message': 'Appointment completed'}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error completing appointment: {str(e)}")
            return False, {'message': 'Completion failed'}


# ==================== PRESCRIPTION SERVICE ====================

class PrescriptionService:
    """Handles prescription management."""
    
    def create_prescription(self, appointment_id: str, patient_id: str, doctor_id: str,
                           hospital_id: str, items: List[Dict],
                           notes: str = None) -> Tuple[bool, Dict]:
        """
        Create prescription with medicine items.
        
        Args:
            appointment_id: Appointment ID
            patient_id: Patient ID
            doctor_id: Doctor ID
            hospital_id: Hospital ID
            items: List of {'medicine_id', 'quantity', 'dosage', 'frequency', 'duration_days'}
            notes: Prescription notes
            
        Returns:
            (success, response_dict) tuple
        """
        try:
            # Generate prescription number
            prescription_number = IDGenerator.generate_prescription_number(hospital_id[:3].upper())
            
            prescription = Prescription(
                appointment_id=appointment_id,
                patient_id=patient_id,
                doctor_id=doctor_id,
                hospital_id=hospital_id,
                prescription_number=prescription_number,
                status=PrescriptionStatusEnum.ISSUED,
                notes=notes,
            )
            
            # Add medicine items
            for item in items:
                medicine = Medicine.query.get(item['medicine_id'])
                if not medicine:
                    return False, {'message': f"Medicine not found: {item['medicine_id']}"}
                
                prescription_item = PrescriptionItem(
                    prescription_id=prescription.id,
                    medicine_id=item['medicine_id'],
                    quantity=item.get('quantity'),
                    dosage=item.get('dosage'),
                    frequency=item.get('frequency'),
                    duration_days=item.get('duration_days'),
                    instructions=item.get('instructions'),
                )
                prescription.prescription_items.append(prescription_item)
            
            db.session.add(prescription)
            db.session.commit()
            
            logger.info(f"Prescription created: {prescription_number}")
            
            return True, {
                'message': 'Prescription created',
                'prescription_id': prescription.id,
                'prescription_number': prescription_number,
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating prescription: {str(e)}")
            return False, {'message': 'Prescription creation failed'}
    
    def get_prescription(self, prescription_id: str) -> Optional[Prescription]:
        """Get prescription by ID."""
        return Prescription.query.get(prescription_id)
    
    def get_patient_prescriptions(self, patient_id: str) -> List[Prescription]:
        """Get all prescriptions for patient."""
        try:
            return Prescription.query.filter_by(
                patient_id=patient_id,
                deleted_at=None
            ).order_by(Prescription.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting prescriptions: {str(e)}")
            return []
    
    def dispense_prescription(self, prescription_id: str) -> Tuple[bool, Dict]:
        """Mark prescription as dispensed."""
        prescription = self.get_prescription(prescription_id)
        if not prescription:
            return False, {'message': 'Prescription not found'}
        
        try:
            prescription.status = PrescriptionStatusEnum.DISPENSED
            prescription.dispensed_date = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Prescription dispensed: {prescription_id}")
            return True, {'message': 'Prescription dispensed'}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error dispensing prescription: {str(e)}")
            return False, {'message': 'Dispensing failed'}
