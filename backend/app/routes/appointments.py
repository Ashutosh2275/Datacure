"""
Appointment Management Routes.
"""
from flask import Blueprint, request
from app.services import AppointmentService
from app.utils import APIResponse, token_required, role_required, Paginator
from app.utils.auth import hospital_isolated
from datetime import date

appointments_bp = Blueprint('appointments', __name__)
appointment_service = AppointmentService()


@appointments_bp.route('', methods=['POST'])
@role_required('patient', 'admin', 'doctor')
@hospital_isolated
def book_appointment():
    """
    Book new appointment.
    
    Expected JSON:
    {
        "patient_id": "patient-uuid",
        "doctor_id": "doctor-uuid",
        "appointment_date": "2025-03-15",
        "start_time": "10:00",
        "end_time": "10:30",
        "appointment_type": "consultation",
        "chief_complaint": "Fever and cough",
        "is_emergency": false
    }
    """
    try:
        data = request.json
        
        from datetime import datetime, time
        
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        success, response = appointment_service.book_appointment(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            hospital_id=request.hospital_id,
            appointment_date=date.fromisoformat(data['appointment_date']),
            start_time=start_time,
            end_time=end_time,
            appointment_type=data.get('appointment_type', 'consultation'),
            chief_complaint=data.get('chief_complaint'),
            is_emergency=data.get('is_emergency', False),
            is_telemedicine=data.get('is_telemedicine', False),
        )
        
        if success:
            return APIResponse.created(response, 'Appointment booked successfully')
        else:
            return APIResponse.bad_request(response['message'])
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@appointments_bp.route('', methods=['GET'])
@token_required
@hospital_isolated
def get_appointments():
    """
    Get appointments.
    
    Query params:
    - patient_id: Filter by patient
    - doctor_id: Filter by doctor
    - status: Filter by status
    - date: Filter by date
    """
    try:
        page, per_page = Paginator.get_pagination_params()
        
        patient_id = request.args.get('patient_id')
        doctor_id = request.args.get('doctor_id')
        status_filter = request.args.get('status')
        date_filter = request.args.get('date')
        
        from app.models import Appointment
        from sqlalchemy import and_
        
        query = Appointment.query.filter_by(hospital_id=request.hospital_id)
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        if status_filter:
            query = query.filter_by(status=status_filter)
        if date_filter:
            query = query.filter(Appointment.appointment_date == date.fromisoformat(date_filter))
        
        total = query.count()
        appointments = query.offset((page - 1) * per_page).limit(per_page).all()
        
        response_data = [
            {
                'id': a.id,
                'patient_id': a.patient_id,
                'doctor_id': a.doctor_id,
                'appointment_date': str(a.appointment_date),
                'start_time': str(a.start_time),
                'end_time': str(a.end_time),
                'status': a.status,
                'appointment_type': a.appointment_type,
                'is_emergency': a.is_emergency,
                'no_show_prediction_score': a.no_show_prediction_score,
            }
            for a in appointments
        ]
        
        return APIResponse.paginated(response_data, page, per_page, total)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@appointments_bp.route('/<appointment_id>', methods=['GET'])
@token_required
@hospital_isolated
def get_appointment(appointment_id):
    """Get appointment details."""
    try:
        appointment = appointment_service.get_appointment(appointment_id)
        
        if not appointment:
            return APIResponse.not_found('Appointment')
        
        response_data = {
            'id': appointment.id,
            'patient_id': appointment.patient_id,
            'doctor_id': appointment.doctor_id,
            'appointment_date': str(appointment.appointment_date),
            'start_time': str(appointment.start_time),
            'end_time': str(appointment.end_time),
            'status': appointment.status,
            'chief_complaint': appointment.chief_complaint,
            'notes': appointment.notes,
            'is_emergency': appointment.is_emergency,
            'is_telemedicine': appointment.is_telemedicine,
        }
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@appointments_bp.route('/<appointment_id>/reschedule', methods=['PUT'])
@role_required('admin', 'doctor', 'patient')
@hospital_isolated
def reschedule_appointment(appointment_id):
    """
    Reschedule appointment.
    
    Expected JSON:
    {
        "appointment_date": "2025-03-20",
        "start_time": "14:00",
        "end_time": "14:30"
    }
    """
    try:
        from datetime import datetime, time
        
        data = request.json
        
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        success, response = appointment_service.reschedule_appointment(
            appointment_id=appointment_id,
            new_date=date.fromisoformat(data['appointment_date']),
            new_start_time=start_time,
            new_end_time=end_time,
        )
        
        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.not_found('Appointment')
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@appointments_bp.route('/<appointment_id>/cancel', methods=['POST'])
@role_required('admin', 'doctor', 'patient')
@hospital_isolated
def cancel_appointment(appointment_id):
    """Cancel appointment."""
    try:
        success, response = appointment_service.cancel_appointment(appointment_id)
        
        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.not_found('Appointment')
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@appointments_bp.route('/<appointment_id>/complete', methods=['POST'])
@role_required('admin', 'doctor')
@hospital_isolated
def complete_appointment(appointment_id):
    """Mark appointment as completed."""
    try:
        success, response = appointment_service.complete_appointment(appointment_id)
        
        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.not_found('Appointment')
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@appointments_bp.route('/today', methods=['GET'])
@role_required('admin', 'doctor', 'nurse')
@hospital_isolated
def get_today_appointments():
    """Get today's appointments."""
    try:
        appointments = appointment_service.get_today_appointments(request.hospital_id)
        
        response_data = [
            {
                'id': a.id,
                'patient_id': a.patient_id,
                'doctor_id': a.doctor_id,
                'start_time': str(a.start_time),
                'end_time': str(a.end_time),
                'status': a.status,
                'is_emergency': a.is_emergency,
            }
            for a in appointments
        ]
        
        return APIResponse.success({
            'total': len(response_data),
            'appointments': response_data,
        })
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


# ==================== PRESCRIPTION ROUTES ====================

from app.services import PrescriptionService

prescriptions_bp = Blueprint('prescriptions', __name__)
prescription_service = PrescriptionService()


@prescriptions_bp.route('', methods=['POST'])
@role_required('doctor')
@hospital_isolated
def create_prescription():
    """
    Create prescription with medicines.
    
    Expected JSON:
    {
        "appointment_id": "appt-uuid",
        "patient_id": "patient-uuid",
        "doctor_id": "doctor-uuid",
        "items": [
            {
                "medicine_id": "med-uuid",
                "quantity": 10,
                "dosage": "500mg",
                "frequency": "Twice daily",
                "duration_days": 7
            }
        ],
        "notes": "After meals"
    }
    """
    try:
        data = request.json
        
        success, response = prescription_service.create_prescription(
            appointment_id=data['appointment_id'],
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            hospital_id=request.hospital_id,
            items=data['items'],
            notes=data.get('notes'),
        )
        
        if success:
            return APIResponse.created(response)
        else:
            return APIResponse.bad_request(response['message'])
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@prescriptions_bp.route('/<patient_id>', methods=['GET'])
@token_required
@hospital_isolated
def get_patient_prescriptions(patient_id):
    """Get all prescriptions for patient."""
    try:
        prescriptions = prescription_service.get_patient_prescriptions(patient_id)
        
        response_data = [
            {
                'id': p.id,
                'prescription_number': p.prescription_number,
                'status': p.status,
                'created_at': p.created_at.isoformat(),
                'items': [
                    {
                        'medicine_name': pi.medicine.name,
                        'quantity': pi.quantity,
                        'dosage': pi.dosage,
                        'frequency': pi.frequency,
                    }
                    for pi in p.prescription_items
                ]
            }
            for p in prescriptions
        ]
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@prescriptions_bp.route('/<prescription_id>/dispense', methods=['POST'])
@role_required('admin', 'nurse')
@hospital_isolated
def dispense_prescription(prescription_id):
    """Mark prescription as dispensed."""
    try:
        success, response = prescription_service.dispense_prescription(prescription_id)
        
        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.not_found('Prescription')
    
    except Exception as e:
        return APIResponse.internal_error(str(e))
