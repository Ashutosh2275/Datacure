"""
Billing & Invoice Management Routes
Endpoints for invoice creation, payment tracking, and financial reports.
"""
from flask import Blueprint, request, send_file
from datetime import datetime
from app.utils.errors import APIResponse, ValidationError, NotFoundError
from app.utils.auth import token_required, role_required, hospital_isolated
from app.utils.helpers import Paginator, QueryFilter
from app.services.operations import BillingService
from app.repositories import BillingRepository, PatientRepository
from app.schemas import BillingListSchema, BillingDetailSchema, BillingCreateSchema
from app.extensions import db

billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/invoices', methods=['GET'])
@token_required
@role_required('admin', 'reception', 'doctor')
@hospital_isolated
def list_invoices():
    """Get invoices with pagination and filters."""
    try:
        page, per_page = Paginator.get_pagination_params()
        patient_id = request.args.get('patient_id')
        status = request.args.get('status')  # pending, partial, paid, cancelled

        from app.models import Billing
        query = Billing.query.filter_by(hospital_id=request.hospital_id)
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(Billing.invoice_date.desc())

        invoices, total = Paginator.paginate_query(query, page, per_page)
        pages = max(1, (total + per_page - 1) // per_page)

        schema = BillingListSchema(many=True)
        return APIResponse.success(
            schema.dump(invoices),
            meta={'total': total, 'page': page, 'per_page': per_page, 'pages': pages}
        )
    except Exception as e:
        return APIResponse.error(str(e), 'LIST_INVOICES_ERROR')


@billing_bp.route('/invoices/<invoice_id>', methods=['GET'])
@token_required
@hospital_isolated
def get_invoice(invoice_id):
    """Get invoice detail."""
    try:
        from app.models import Billing
        invoice = Billing.query.get(invoice_id)
        if not invoice:
            return APIResponse.not_found('Invoice not found')
        
        schema = BillingDetailSchema()
        return APIResponse.success(schema.dump(invoice))
    except Exception as e:
        return APIResponse.error(str(e), 'GET_INVOICE_ERROR')


@billing_bp.route('/invoices', methods=['POST'])
@token_required
@role_required('admin', 'reception', 'doctor')
@hospital_isolated
def create_invoice():
    """Create new invoice."""
    try:
        data = request.get_json()
        schema = BillingCreateSchema()
        validated = schema.load(data)
        
        success, invoice_id = BillingService.create_invoice(
            hospital_id=request.hospital_id,
            patient_id=validated['patient_id'],
            appointment_id=validated.get('appointment_id'),
            items=validated.get('items', []),
            gst_percentage=validated.get('gst_percentage', 5),
            due_date=validated.get('due_date')
        )
        
        if not success:
            return APIResponse.bad_request('Failed to create invoice')
        
        return APIResponse.created({'invoice_id': invoice_id, 'message': 'Invoice created successfully'})
    except ValidationError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        return APIResponse.error(str(e), 'CREATE_INVOICE_ERROR')


@billing_bp.route('/invoices/<invoice_id>', methods=['PUT'])
@token_required
@role_required('admin', 'reception')
@hospital_isolated
def update_invoice(invoice_id):
    """Update invoice details."""
    try:
        data = request.get_json()
        from app.models import Billing
        
        invoice = Billing.query.get(invoice_id)
        if not invoice:
            return APIResponse.not_found('Invoice not found')
        
        # Update allowed fields
        if 'due_date' in data:
            invoice.due_date = datetime.fromisoformat(data['due_date'])
        if 'notes' in data:
            invoice.notes = data['notes']
        
        db.session.commit()
        schema = BillingDetailSchema()
        return APIResponse.success(schema.dump(invoice))
    except Exception as e:
        return APIResponse.error(str(e), 'UPDATE_INVOICE_ERROR')


@billing_bp.route('/invoices/<invoice_id>/pay', methods=['POST'])
@token_required
@role_required('admin', 'reception')
@hospital_isolated
def record_payment(invoice_id):
    """Record payment for invoice."""
    try:
        data = request.get_json()
        amount = data.get('amount')
        payment_method = data.get('payment_method')  # cash, cheque, card, net_banking
        reference_number = data.get('reference_number')
        
        success = BillingService.record_payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number
        )
        
        if not success:
            return APIResponse.bad_request('Failed to record payment')
        
        return APIResponse.success({'message': 'Payment recorded successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'RECORD_PAYMENT_ERROR')


@billing_bp.route('/invoices/<invoice_id>/pdf', methods=['GET'])
@token_required
@role_required('admin', 'reception', 'doctor')
@hospital_isolated
def generate_invoice_pdf(invoice_id):
    """Generate PDF for invoice."""
    try:
        from app.models import Billing
        invoice = Billing.query.get(invoice_id)
        if not invoice:
            return APIResponse.not_found('Invoice not found')
        
        # PDF generation would be implemented here
        # For now, return success message
        return APIResponse.success({'message': 'PDF generation feature coming soon'})
    except Exception as e:
        return APIResponse.error(str(e), 'GENERATE_PDF_ERROR')


@billing_bp.route('/reports/revenue', methods=['GET'])
@token_required
@role_required('admin')
@hospital_isolated
def revenue_report():
    """Get revenue report."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        report = BillingService.get_revenue_report(
            hospital_id=request.hospital_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return APIResponse.success(report)
    except Exception as e:
        return APIResponse.error(str(e), 'REVENUE_REPORT_ERROR')


@billing_bp.route('/reports/unpaid', methods=['GET'])
@token_required
@role_required('admin', 'reception')
@hospital_isolated
def unpaid_invoices_report():
    """Get unpaid invoices report."""
    try:
        unpaid = BillingService.get_pending_payments(request.hospital_id)
        
        return APIResponse.success({
            'total_unpaid': len(unpaid),
            'total_amount': sum(inv.balance_due for inv in unpaid),
            'invoices': [
                {
                    'invoice_id': inv.id,
                    'invoice_number': inv.invoice_number,
                    'patient_id': inv.patient_id,
                    'balance_due': float(inv.balance_due),
                    'due_date': inv.due_date.isoformat() if inv.due_date else None
                }
                for inv in unpaid
            ]
        })
    except Exception as e:
        return APIResponse.error(str(e), 'UNPAID_REPORT_ERROR')


@billing_bp.route('/reports/breakdown', methods=['GET'])
@token_required
@role_required('admin')
@hospital_isolated
def payment_method_breakdown():
    """Get payment breakdown by method."""
    try:
        period = request.args.get('period', 'month')
        
        breakdown = BillingService.get_payment_breakdown(
            hospital_id=request.hospital_id,
            period=period
        )
        
        return APIResponse.success(breakdown)
    except Exception as e:
        return APIResponse.error(str(e), 'BREAKDOWN_ERROR')


@billing_bp.route('/invoice-duplicate/<invoice_id>', methods=['POST'])
@token_required
@role_required('admin', 'reception')
@hospital_isolated
def duplicate_invoice(invoice_id):
    """Duplicate an existing invoice."""
    try:
        from app.models import Billing
        original = Billing.query.get(invoice_id)
        if not original:
            return APIResponse.not_found('Invoice not found')
        
        success, new_invoice_id = BillingService.duplicate_invoice(invoice_id)
        if not success:
            return APIResponse.bad_request('Failed to duplicate invoice')
        
        return APIResponse.created({'new_invoice_id': new_invoice_id})
    except Exception as e:
        return APIResponse.error(str(e), 'DUPLICATE_ERROR')
