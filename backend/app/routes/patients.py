"""
Patient Management Routes.
"""
from flask import Blueprint, request
from app.services import PatientService
from app.schemas import PatientCreateSchema, PatientResponseSchema, PatientListSchema
from app.utils import APIResponse, token_required, role_required, Paginator
from app.utils.auth import hospital_isolated
from marshmallow import ValidationError
from datetime import date

patients_bp = Blueprint('patients', __name__)
patient_service = PatientService()


@patients_bp.route('', methods=['POST'])
@role_required('admin', 'doctor')
@hospital_isolated
def create_patient():
    """
    Register new patient.
    
    Expected JSON:
    {
        "user_id": "user-uuid",
        "date_of_birth": "1990-05-15",
        "gender": "M",
        "blood_group": "O+",
        "weight": 75.5,
        "height": 175,
        "allergies": "Penicillin",
        "chronic_conditions": "Diabetes, Hypertension",
        "insurance_provider": "Apollo",
        "insurance_policy_number": "POL123456"
    }
    """
    try:
        schema = PatientCreateSchema()
        data = schema.load(request.json)
        
        success, response = patient_service.create_patient(
            user_id=data['user_id'],
            hospital_id=request.hospital_id,
            date_of_birth=data['date_of_birth'],
            gender=data['gender'],
            blood_group=data.get('blood_group'),
            weight=data.get('weight'),
            height=data.get('height'),
            allergies=data.get('allergies'),
            chronic_conditions=data.get('chronic_conditions'),
            insurance_provider=data.get('insurance_provider'),
            insurance_policy_number=data.get('insurance_policy_number'),
        )
        
        if success:
            return APIResponse.created(response, 'Patient registered successfully')
        else:
            return APIResponse.bad_request(response['message'])
    
    except ValidationError as err:
        return APIResponse.validation_error('Validation failed', err.messages)
    except Exception as e:
        return APIResponse.internal_error(str(e))


@patients_bp.route('', methods=['GET'])
@token_required
@hospital_isolated
def get_patients():
    """
   Get all patients in hospital with pagination.
    
    Query params:
    - page: Page number
    - per_page: Items per page
    """
    try:
        page, per_page = Paginator.get_pagination_params()
        
        patients, total = patient_service.get_hospital_patients(
            request.hospital_id,
            page,
            per_page
        )
        
        schema = PatientListSchema(many=True)
        response_data = schema.dump(patients)
        
        return APIResponse.paginated(response_data, page, per_page, total)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@patients_bp.route('/<patient_id>', methods=['GET'])
@token_required
@hospital_isolated
def get_patient(patient_id):
    """Get patient details."""
    try:
        patient = patient_service.get_patient(patient_id)
        
        if not patient:
            return APIResponse.not_found('Patient')
        
        schema = PatientResponseSchema()
        response_data = schema.dump(patient)
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@patients_bp.route('/<patient_id>', methods=['PUT'])
@token_required
@hospital_isolated
def update_patient(patient_id):
    """Update patient information."""
    try:
        data = request.json
        
        success, response = patient_service.update_patient(patient_id, **data)
        
        if success:
            return APIResponse.success(response)
        else:
            return APIResponse.not_found('Patient')
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@patients_bp.route('/<patient_id>/medical-records', methods=['GET'])
@token_required
@hospital_isolated
def get_medical_records(patient_id):
    """Get all medical records for patient."""
    try:
        records = patient_service.get_medical_records(patient_id)
        
        response_data = [
            {
                'id': r.id,
                'record_type': r.record_type,
                'description': r.description,
                'file_url': r.file_url,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@patients_bp.route('/<patient_id>/medical-records', methods=['POST'])
@role_required('doctor')
@hospital_isolated
def add_medical_record(patient_id):
    """
    Add medical record for patient.
    
    Expected JSON:
    {
        "doctor_id": "doctor-uuid",
        "record_type": "lab_report",
        "description": "Blood test results",
        "file_url": "s3://bucket/file.pdf",
        "diagnosis": "Normal",
        "notes": "No issues found"
    }
    """
    try:
        data = request.json
        
        success, response = patient_service.add_medical_record(
            patient_id=patient_id,
            doctor_id=data['doctor_id'],
            record_type=data['record_type'],
            description=data.get('description'),
            file_url=data.get('file_url'),
            diagnosis=data.get('diagnosis'),
            notes=data.get('notes'),
        )
        
        if success:
            return APIResponse.created(response)
        else:
            return APIResponse.bad_request(response['message'])
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@patients_bp.route('/statistics', methods=['GET'])
@role_required('admin', 'doctor')
@hospital_isolated
def get_statistics():
    """Get patient statistics for hospital."""
    try:
        stats = patient_service.get_patient_statistics(request.hospital_id)
        return APIResponse.success(stats)
    except Exception as e:
        return APIResponse.internal_error(str(e))


# ==================== DOCTOR ROUTES ====================

from app.services import DoctorService

doctors_bp = Blueprint('doctors', __name__)
doctor_service = DoctorService()


@doctors_bp.route('', methods=['GET'])
@token_required
@hospital_isolated
def get_doctors():
    """Get all doctors in hospital."""
    try:
        specialization = request.args.get('specialization')
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        
        if specialization:
            doctors = doctor_service.get_doctors_by_specialization(
                request.hospital_id,
                specialization
            )
        elif available_only:
            doctors = doctor_service.get_available_doctors(request.hospital_id)
        else:
            from app.models import Doctor
            doctors = Doctor.query.filter_by(hospital_id=request.hospital_id).all()
        
        response_data = [
            {
                'id': d.id,
                'name': f"{d.user.first_name} {d.user.last_name}",
                'specialization': d.specialization,
                'experience_years': d.experience_years,
                'consultation_fee': d.consultation_fee,
                'availability_status': d.availability_status,
            }
            for d in doctors
        ]
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@doctors_bp.route('/<doctor_id>/slots', methods=['GET'])
@token_required
@hospital_isolated
def get_doctor_slots(doctor_id):
    """Get available appointment slots for doctor."""
    try:
        from datetime import date, timedelta
        
        date_from = request.args.get('from', type=lambda x: date.fromisoformat(x))
        if not date_from:
            date_from = date.today()
        
        slots = doctor_service.get_available_slots(doctor_id, date_from)
        
        response_data = [
            {
                'id': s.id,
                'slot_date': str(s.slot_date),
                'start_time': str(s.start_time),
                'end_time': str(s.end_time),
                'is_booked': s.is_booked,
            }
            for s in slots[:14]  # Next 2 weeks
        ]
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


__all__ = ['patients_bp', 'doctors_bp', 'prescriptions_bp']
