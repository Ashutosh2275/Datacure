"""
File upload routes for medical documents and records.
Handles secure file uploads for patient documents, prescriptions, reports, etc.
"""
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from app.utils import (
    APIResponse, token_required, role_required, get_logger
)
from app.utils.file_handler import FileUploadRequest, FileValidator, FileStorage
from app.extensions import db
from app.models import Patient, AuditLog, User

logger = get_logger(__name__)

upload_bp = Blueprint('uploads', __name__)


@upload_bp.route('/upload/medical-record', methods=['POST'])
@token_required
def upload_medical_record():
    """
    Upload medical record document for patient.

    Allowed roles: doctor, admin
    Allowed file types: pdf, dcm, jpg, jpeg, png, doc, docx
    Maximum file size: 50MB

    Expected form data:
    - file: Binary file data
    - patient_id: Patient UUID
    - record_type: Type of record (diagnosis, test_result, imaging, etc.)

    Returns:
        File upload confirmation with storage path
    """
    try:
        # Check authorization
        user_id = request.user_id
        hospital_id = request.hospital_id
        user_role = request.user_role

        if user_role not in ['doctor', 'admin']:
            return APIResponse.forbidden('Only doctors and admins can upload medical records')

        # Check if file present
        if 'file' not in request.files:
            return APIResponse.bad_request('No file provided')

        file_obj = request.files['file']
        patient_id = request.form.get('patient_id')
        record_type = request.form.get('record_type', 'document')

        # Validate patient exists and belongs to hospital
        patient = Patient.query.filter_by(
            id=patient_id,
            hospital_id=hospital_id
        ).first()

        if not patient:
            return APIResponse.not_found('Patient not found')

        # Process upload
        result = FileUploadRequest.process_upload(
            file_obj=file_obj,
            hospital_id=hospital_id,
            user_id=user_id,
            file_type=f'medical_record_{record_type}'
        )

        if not result['success']:
            return APIResponse.bad_request(result['error'])

        # Log audit trail
        try:
            audit_log = AuditLog(
                hospital_id=hospital_id,
                user_id=user_id,
                action='UPLOAD_MEDICAL_RECORD',
                resource_type='medical_record',
                resource_id=patient_id,
                changes={
                    'file_path': result['file_path'],
                    'original_filename': result['original_filename'],
                    'file_size': result['file_size'],
                    'record_type': record_type
                },
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to log audit trail: {str(e)}")

        return APIResponse.created({
            'file_path': result['file_path'],
            'filename': result['filename'],
            'original_filename': result['original_filename'],
            'file_size': result['file_size'],
            'record_type': record_type,
        }, 'Medical record uploaded successfully')

    except Exception as e:
        logger.error(f"Medical record upload error: {str(e)}")
        return APIResponse.internal_error(str(e))


@upload_bp.route('/upload/prescription-document', methods=['POST'])
@token_required
def upload_prescription_document():
    """
    Upload prescription document.

    Allowed roles: doctor, admin
    Allowed file types: pdf, jpg, jpeg, png
    Maximum file size: 10MB

    Expected form data:
    - file: Binary file data
    - prescription_id: Prescription UUID

    Returns:
        File upload confirmation
    """
    try:
        user_id = request.user_id
        hospital_id = request.hospital_id
        user_role = request.user_role

        if user_role not in ['doctor', 'admin']:
            return APIResponse.forbidden('Only doctors and admins can upload prescriptions')

        if 'file' not in request.files:
            return APIResponse.bad_request('No file provided')

        file_obj = request.files['file']
        prescription_id = request.form.get('prescription_id')

        # Validate extension is allowed for prescriptions
        if file_obj.filename:
            ext = file_obj.filename.rsplit('.', 1)[1].lower() if '.' in file_obj.filename else ''
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                return APIResponse.bad_request(
                    'Only PDF, JPG, PNG images allowed for prescriptions'
                )

        # Process upload
        result = FileUploadRequest.process_upload(
            file_obj=file_obj,
            hospital_id=hospital_id,
            user_id=user_id,
            file_type='prescription_document'
        )

        if not result['success']:
            return APIResponse.bad_request(result['error'])

        # Log audit trail
        try:
            audit_log = AuditLog(
                hospital_id=hospital_id,
                user_id=user_id,
                action='UPLOAD_PRESCRIPTION',
                resource_type='prescription',
                resource_id=prescription_id,
                changes={'file_path': result['file_path']},
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to log audit trail: {str(e)}")

        return APIResponse.created({
            'file_path': result['file_path'],
            'filename': result['filename'],
            'file_size': result['file_size'],
        }, 'Prescription document uploaded successfully')

    except Exception as e:
        logger.error(f"Prescription upload error: {str(e)}")
        return APIResponse.internal_error(str(e))


@upload_bp.route('/upload/report', methods=['POST'])
@token_required
@role_required('doctor', 'admin')
def upload_medical_report():
    """
    Upload medical test/lab report.

    Expected form data:
    - file: Binary file data
    - patient_id: Patient UUID
    - report_type: Type of report (lab, imaging, pathology, etc.)

    Returns:
        File upload confirmation
    """
    try:
        user_id = request.user_id
        hospital_id = request.hospital_id

        if 'file' not in request.files:
            return APIResponse.bad_request('No file provided')

        file_obj = request.files['file']
        patient_id = request.form.get('patient_id')
        report_type = request.form.get('report_type', 'report')

        # Validate patient
        patient = Patient.query.filter_by(
            id=patient_id,
            hospital_id=hospital_id
        ).first()

        if not patient:
            return APIResponse.not_found('Patient not found')

        # Process upload
        result = FileUploadRequest.process_upload(
            file_obj=file_obj,
            hospital_id=hospital_id,
            user_id=user_id,
            file_type=f'report_{report_type}'
        )

        if not result['success']:
            return APIResponse.bad_request(result['error'])

        # Log audit trail
        try:
            audit_log = AuditLog(
                hospital_id=hospital_id,
                user_id=user_id,
                action='UPLOAD_REPORT',
                resource_type='report',
                resource_id=patient_id,
                changes={
                    'file_path': result['file_path'],
                    'report_type': report_type
                },
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to log audit trail: {str(e)}")

        return APIResponse.created({
            'file_path': result['file_path'],
            'filename': result['filename'],
            'report_type': report_type,
        }, 'Report uploaded successfully')

    except Exception as e:
        logger.error(f"Report upload error: {str(e)}")
        return APIResponse.internal_error(str(e))


@upload_bp.route('/upload/validate', methods=['POST'])
@token_required
def validate_file():
    """
    Validate file without uploading (pre-flight check).

    Expected JSON:
    {
        "filename": "document.pdf",
        "file_size": 1024000,
        "file_type": "application/pdf"
    }

    Returns:
        Validation result with any errors
    """
    try:
        data = request.get_json()

        if not data or 'filename' not in data:
            return APIResponse.bad_request('filename required')

        filename = data.get('filename')
        file_size = data.get('file_size', 0)

        # Validate extension
        is_valid, error = FileValidator.validate_extension(filename)
        if not is_valid:
            return APIResponse.success({
                'valid': False,
                'error': error
            })

        # Get extension and validate size
        ext = filename.rsplit('.', 1)[1].lower()
        size_valid, size_error = FileValidator.validate_size(file_size, ext)
        if not size_valid:
            return APIResponse.success({
                'valid': False,
                'error': size_error
            })

        return APIResponse.success({
            'valid': True,
            'allowed_extension': ext in FileValidator.get_allowed_extensions(),
            'max_size_bytes': FileValidator.MAX_SIZES.get(ext),
        })

    except Exception as e:
        logger.error(f"File validation error: {str(e)}")
        return APIResponse.internal_error(str(e))


@upload_bp.route('/upload/allowed-types', methods=['GET'])
@token_required
def get_allowed_file_types():
    """
    Get list of allowed file types and limits.

    Returns:
        List of allowed extensions with max sizes
    """
    try:
        allowed_types = {}
        for ext, mime_type in FileValidator.ALLOWED_EXTENSIONS.items():
            allowed_types[ext] = {
                'mime_type': mime_type,
                'max_size_mb': FileValidator.MAX_SIZES.get(ext, 0) / (1024 * 1024),
            }

        return APIResponse.success({
            'allowed_types': allowed_types,
            'total_max_upload_mb': current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024 * 1024),
        })

    except Exception as e:
        logger.error(f"Get allowed types error: {str(e)}")
        return APIResponse.internal_error(str(e))
