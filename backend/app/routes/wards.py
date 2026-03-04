"""
Ward & Bed Management Routes
Endpoints for ward creation, bed allocation, occupancy management.
"""
from flask import Blueprint, request
from datetime import datetime
from app.utils.errors import APIResponse, ValidationError, ConflictError
from app.utils.auth import token_required, role_required, hospital_isolated
from app.utils.helpers import Paginator
from app.services.operations import WardService
from app.repositories import WardRepository, BedRepository
from app.schemas import WardListSchema, BedDetailSchema
from app.extensions import db

wards_bp = Blueprint('wards', __name__)


@wards_bp.route('', methods=['GET'])
@token_required
@hospital_isolated
def list_wards():
    """List all wards in hospital."""
    try:
        page, per_page = Paginator.get_pagination_params()
        ward_type = request.args.get('ward_type')  # icu, general, pediatric

        from app.models import Ward
        query = Ward.query.filter_by(hospital_id=request.hospital_id)
        if ward_type:
            query = query.filter_by(ward_type=ward_type)

        wards, total = Paginator.paginate_query(query, page, per_page)
        pages = max(1, (total + per_page - 1) // per_page)

        schema = WardListSchema(many=True)
        return APIResponse.success(
            schema.dump(wards),
            meta={'total': total, 'page': page, 'per_page': per_page, 'pages': pages}
        )
    except Exception as e:
        return APIResponse.error(str(e), 'LIST_WARDS_ERROR')


@wards_bp.route('/<ward_id>', methods=['GET'])
@token_required
@hospital_isolated
def get_ward(ward_id):
    """Get ward details."""
    try:
        from app.models import Ward
        ward = Ward.query.get(ward_id)
        if not ward:
            return APIResponse.not_found('Ward not found')
        
        schema = WardListSchema()
        return APIResponse.success(schema.dump(ward))
    except Exception as e:
        return APIResponse.error(str(e), 'GET_WARD_ERROR')


@wards_bp.route('', methods=['POST'])
@token_required
@role_required('admin')
@hospital_isolated
def create_ward():
    """Create new ward with beds."""
    try:
        data = request.get_json()
        from app.models import Ward, Bed
        
        ward = Ward(
            hospital_id=request.hospital_id,
            name=data['name'],
            ward_type=data.get('ward_type', 'general'),
            floor_number=data.get('floor_number'),
            total_beds=int(data['total_beds']),
            available_beds=int(data['total_beds'])
        )
        
        db.session.add(ward)
        db.session.flush()  # Get ward ID without committing
        
        # Create beds for this ward
        for i in range(int(data['total_beds'])):
            bed = Bed(
                ward_id=ward.id,
                hospital_id=request.hospital_id,
                bed_number=f"{data['name']}-{i+1}",
                bed_type=data.get('bed_type', 'general'),
                status='available'
            )
            db.session.add(bed)
        
        db.session.commit()
        schema = WardListSchema()
        return APIResponse.created({'ward_id': ward.id, 'message': 'Ward created successfully'})
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(str(e), 'CREATE_WARD_ERROR')


@wards_bp.route('/<ward_id>', methods=['PUT'])
@token_required
@role_required('admin')
@hospital_isolated
def update_ward(ward_id):
    """Update ward information."""
    try:
        from app.models import Ward
        ward = Ward.query.get(ward_id)
        if not ward:
            return APIResponse.not_found('Ward not found')
        
        data = request.get_json()
        if 'name' in data:
            ward.name = data['name']
        if 'floor_number' in data:
            ward.floor_number = data['floor_number']
        
        db.session.commit()
        schema = WardListSchema()
        return APIResponse.success(schema.dump(ward))
    except Exception as e:
        return APIResponse.error(str(e), 'UPDATE_WARD_ERROR')


@wards_bp.route('/<ward_id>/beds', methods=['GET'])
@token_required
@hospital_isolated
def get_ward_beds(ward_id):
    """Get all beds in ward with status."""
    try:
        beds, total, pages = BedRepository.filter(
            ward_id=ward_id
        ).paginate(page=1, per_page=100)
        
        schema = BedDetailSchema(many=True)
        return APIResponse.success(schema.dump(beds))
    except Exception as e:
        return APIResponse.error(str(e), 'GET_BEDS_ERROR')


@wards_bp.route('/<ward_id>/occupancy', methods=['GET'])
@token_required
@hospital_isolated
def get_occupancy_stats(ward_id):
    """Get occupancy statistics for ward."""
    try:
        stats = WardService.get_occupancy_status(ward_id)
        
        return APIResponse.success({
            'ward_id': ward_id,
            'total_beds': stats.get('total', 0),
            'occupied_beds': stats.get('occupied', 0),
            'available_beds': stats.get('available', 0),
            'occupancy_percentage': (stats.get('occupied', 0) / max(stats.get('total', 1), 1)) * 100,
            'average_stay_days': stats.get('avg_stay', 0)
        })
    except Exception as e:
        return APIResponse.error(str(e), 'OCCUPANCY_ERROR')


@wards_bp.route('/<ward_id>/admit', methods=['POST'])
@token_required
@role_required('admin', 'nurse', 'doctor')
@hospital_isolated
def admit_patient(ward_id):
    """Admit patient to ward, allocate bed."""
    try:
        data = request.get_json()
        
        success, admission_id = WardService.allocate_bed(
            ward_id=ward_id,
            patient_id=data['patient_id'],
            doctor_id=data.get('doctor_id'),
            reason=data.get('reason'),
            estimated_days=data.get('estimated_days')
        )
        
        if not success:
            return APIResponse.bad_request('No available beds in ward')
        
        return APIResponse.created({'admission_id': admission_id, 'message': 'Patient admitted successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'ADMIT_ERROR')


@wards_bp.route('/<ward_id>/discharge', methods=['POST'])
@token_required
@role_required('admin', 'nurse', 'doctor')
@hospital_isolated
def discharge_patient(ward_id):
    """Discharge patient from ward."""
    try:
        data = request.get_json()
        patient_id = data['patient_id']
        
        success = WardService.discharge_patient(
            ward_id=ward_id,
            patient_id=patient_id,
            discharge_reason=data.get('discharge_reason'),
            notes=data.get('notes')
        )
        
        if not success:
            return APIResponse.bad_request('Failed to discharge patient')
        
        return APIResponse.success({'message': 'Patient discharged successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'DISCHARGE_ERROR')


@wards_bp.route('/<ward_id>/summary', methods=['GET'])
@token_required
@hospital_isolated
def get_ward_summary(ward_id):
    """Get ward summary including current patients."""
    try:
        from app.models import Ward, Bed, Patient
        
        ward = Ward.query.get(ward_id)
        if not ward:
            return APIResponse.not_found('Ward not found')
        
        beds = Bed.query.filter_by(ward_id=ward_id).all()
        occupied = [b for b in beds if b.status == 'occupied']
        
        return APIResponse.success({
            'ward_id': ward_id,
            'ward_name': ward.name,
            'ward_type': ward.ward_type,
            'total_beds': len(beds),
            'occupied_beds': len(occupied),
            'available_beds': len(beds) - len(occupied),
            'occupancy_percentage': (len(occupied) / max(len(beds), 1)) * 100,
            'current_patients': [
                {
                    'patient_id': b.patient_id,
                    'bed_number': b.bed_number,
                    'admission_date': b.admission_date.isoformat() if b.admission_date else None
                }
                for b in occupied if b.patient_id
            ]
        })
    except Exception as e:
        return APIResponse.error(str(e), 'SUMMARY_ERROR')


@wards_bp.route('/transfer-patient', methods=['POST'])
@token_required
@role_required('admin', 'nurse', 'doctor')
@hospital_isolated
def transfer_patient():
    """Transfer patient between wards."""
    try:
        data = request.get_json()
        
        success = WardService.transfer_patient(
            patient_id=data['patient_id'],
            from_ward_id=data['from_ward_id'],
            to_ward_id=data['to_ward_id'],
            reason=data.get('reason')
        )
        
        if not success:
            return APIResponse.bad_request('Failed to transfer patient')
        
        return APIResponse.success({'message': 'Patient transferred successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'TRANSFER_ERROR')


@wards_bp.route('/<ward_id>/bed-allocation', methods=['GET'])
@token_required
@hospital_isolated
def get_bed_allocation(ward_id):
    """Get detailed bed allocation information."""
    try:
        beds = BedRepository.filter(ward_id=ward_id).all()
        
        allocation = []
        for bed in beds:
            allocation.append({
                'bed_id': bed.id,
                'bed_number': bed.bed_number,
                'bed_type': bed.bed_type,
                'status': bed.status,
                'patient_id': bed.patient_id,
                'admission_date': bed.admission_date.isoformat() if bed.admission_date else None,
                'patient_name': f"{bed.patient.user.first_name} {bed.patient.user.last_name}" if bed.patient else None
            })
        
        return APIResponse.success({
            'ward_id': ward_id,
            'beds': allocation,
            'total': len(beds),
            'occupied': sum(1 for b in beds if b.status == 'occupied'),
            'available': sum(1 for b in beds if b.status == 'available')
        })
    except Exception as e:
        return APIResponse.error(str(e), 'BED_ALLOCATION_ERROR')
