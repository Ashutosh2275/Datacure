"""
AI/ML Prediction Routes.
"""
from flask import Blueprint, request
from app.services import AIService
from app.utils import APIResponse, token_required, role_required, admin_required, hospital_isolated

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()


@ai_bp.route('/predict/readmission', methods=['POST'])
@role_required('admin', 'doctor')
@hospital_isolated
def predict_readmission():
    """
    Predict 30-day readmission risk for patient.
    
    Expected JSON:
    {
        "patient_id": "patient-uuid"
    }
    """
    try:
        data = request.json
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return APIResponse.bad_request('Patient ID required')
        
        success, response = ai_service.predict_readmission_risk(
            patient_id=patient_id,
            hospital_id=request.hospital_id
        )
        
        if success:
            return APIResponse.success({
                'prediction_type': 'readmission_risk',
                'patient_id': patient_id,
                **response
            })
        else:
            return APIResponse.bad_request(response['message'])
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@ai_bp.route('/predict/no-show', methods=['POST'])
@role_required('admin', 'doctor', 'nurse')
@hospital_isolated
def predict_no_show():
    """
    Predict appointment no-show probability.
    
    Expected JSON:
    {
        "appointment_id": "appointment-uuid"
    }
    """
    try:
        data = request.json
        appointment_id = data.get('appointment_id')
        
        if not appointment_id:
            return APIResponse.bad_request('Appointment ID required')
        
        success, response = ai_service.predict_no_show(
            appointment_id=appointment_id,
            hospital_id=request.hospital_id
        )
        
        if success:
            return APIResponse.success({
                'prediction_type': 'no_show',
                'appointment_id': appointment_id,
                **response
            })
        else:
            return APIResponse.bad_request(response['message'])
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@ai_bp.route('/forecast/patient-flow', methods=['GET'])
@role_required('admin', 'doctor')
@hospital_isolated
def forecast_patient_flow():
    """
    Forecast patient flow for next 7-30 days.
    
    Query params:
    - days: Number of days to forecast (default: 7, max: 30)
    """
    try:
        days = request.args.get('days', 7, type=int)
        days = min(max(days, 1), 30)  # Clamp between 1-30
        
        success, response = ai_service.forecast_patient_flow(
            hospital_id=request.hospital_id,
            days=days
        )
        
        if success:
            return APIResponse.success({
                'forecast_type': 'patient_flow',
                **response
            })
        else:
            return APIResponse.internal_error(response['message'])
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@ai_bp.route('/forecast/medicine-demand', methods=['GET'])
@admin_required
@hospital_isolated
def forecast_medicine_demand():
    """
    Forecast medicine demand for next 30 days.
    
    Query params:
    - days: Number of days to forecast (default: 30)
    """
    try:
        days = request.args.get('days', 30, type=int)
        days = min(max(days, 1), 90)  # Clamp between 1-90
        
        success, response = ai_service.forecast_medicine_demand(
            hospital_id=request.hospital_id,
            days=days
        )
        
        if success:
            return APIResponse.success({
                'forecast_type': 'medicine_demand',
                **response
            })
        else:
            return APIResponse.internal_error(response['message'])
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@ai_bp.route('/risk-scores', methods=['GET'])
@admin_required
@hospital_isolated
def get_ai_risk_scores():
    """
    Get all AI risk scores for hospital.
    
    Query params:
    - risk_type: Filter by risk type (readmission, no_show, etc.)
    - min_score: Minimum risk score (0-1)
    - page: Page number
    - per_page: Items per page
    """
    try:
        from app.models import AIRiskScore
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        risk_type = request.args.get('risk_type')
        min_score = request.args.get('min_score', 0, type=float)
        
        query = AIRiskScore.query.filter_by(hospital_id=request.hospital_id)
        
        if risk_type:
            query = query.filter_by(risk_type=risk_type)
        
        if min_score > 0:
            query = query.filter(AIRiskScore.risk_score >= min_score)
        
        # Order by risk score descending
        query = query.order_by(AIRiskScore.risk_score.desc())
        
        total = query.count()
        scores = query.offset((page - 1) * per_page).limit(per_page).all()
        
        response_data = [
            {
                'id': s.id,
                'patient_id': s.patient_id,
                'risk_type': s.risk_type,
                'risk_score': s.risk_score,
                'risk_level': s.risk_level,
                'confidence_score': s.confidence_score,
                'recommendation': s.recommendation,
                'created_at': s.created_at.isoformat(),
            }
            for s in scores
        ]
        
        from app.utils import APIResponse as AR
        return AR.paginated(response_data, page, per_page, total)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@ai_bp.route('/risk-scores/<score_id>/acknowledge', methods=['POST'])
@admin_required
@hospital_isolated
def acknowledge_risk_score(score_id):
    """Mark risk score as reviewed/acted upon."""
    try:
        from app.models import AIRiskScore
        
        score = AIRiskScore.query.get(score_id)
        if not score:
            return APIResponse.not_found('Risk score')
        
        score.is_acted_upon = True
        from app.extensions import db
        db.session.commit()
        
        return APIResponse.success({'message': 'Risk score acknowledged'})
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


@ai_bp.route('/model-metrics', methods=['GET'])
@admin_required
@hospital_isolated
def get_model_metrics():
    """Get AI model performance metrics."""
    try:
        from app.models import ModelMetrics
        
        metrics = ModelMetrics.query.filter_by(
            hospital_id=request.hospital_id
        ).order_by(
            ModelMetrics.last_training_date.desc()
        ).all()
        
        response_data = [
            {
                'id': m.id,
                'model_name': m.model_name,
                'model_version': m.model_version,
                'accuracy': m.accuracy,
                'precision': m.precision,
                'recall': m.recall,
                'f1_score': m.f1_score,
                'auc_roc': m.auc_roc,
                'training_samples': m.training_samples,
                'last_training_date': m.last_training_date.isoformat() if m.last_training_date else None,
                'data_drift_detected': m.data_drift_detected,
                'drift_severity': m.drift_severity,
                'retraining_needed': m.retraining_needed,
            }
            for m in metrics
        ]
        
        return APIResponse.success(response_data)
    
    except Exception as e:
        return APIResponse.internal_error(str(e))


# ==================== PLACEHOLDER ROUTES FOR OTHER MODULES ====================

# Create placeholder blueprints that will be implemented
from flask import Blueprint

users_bp = Blueprint('users', __name__)
billing_bp = Blueprint('billing', __name__)
inventory_bp = Blueprint('inventory', __name__)
wards_bp = Blueprint('wards', __name__)
admin_bp = Blueprint('admin', __name__)
audit_bp = Blueprint('audit', __name__)

doctors_bp = Blueprint('doctors', __name__)

# Add the doctors_bp from patients.py to routes


@users_bp.route('/health', methods=['GET'])
def users_health():
    return APIResponse.success({'status': 'users service ok'})


@billing_bp.route('/health', methods=['GET'])
def billing_health():
    return APIResponse.success({'status': 'billing service ok'})


@inventory_bp.route('/health', methods=['GET'])
def inventory_health():
    return APIResponse.success({'status': 'inventory service ok'})


@wards_bp.route('/health', methods=['GET'])
def wards_health():
    return APIResponse.success({'status': 'wards service ok'})


@admin_bp.route('/health', methods=['GET'])
def admin_health():
    return APIResponse.success({'status': 'admin service ok'})


@audit_bp.route('/health', methods=['GET'])
def audit_health():
    return APIResponse.success({'status': 'audit service ok'})
