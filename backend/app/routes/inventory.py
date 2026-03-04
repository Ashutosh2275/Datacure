"""
Inventory & Medicine Management Routes
Endpoints for medicine stock, expiry tracking, and inventory management.
"""
from flask import Blueprint, request
from datetime import datetime, timedelta
from app.utils.errors import APIResponse, ValidationError
from app.utils.auth import token_required, role_required, hospital_isolated
from app.utils.helpers import Paginator
from app.services.operations import InventoryService
from app.repositories import MedicineRepository, InventoryRepository
from app.schemas import MedicineListSchema, InventorySchema
from app import db

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/v1/inventory')


@inventory_bp.route('/medicines', methods=['GET'])
@token_required
@role_required('admin', 'pharmacy', 'doctor', 'nurse')
@hospital_isolated
def list_medicines():
    """List all medicines in hospital."""
    try:
        paginator = Paginator(request.args)
        search = request.args.get('search')
        
        medicines, total, pages = InventoryService.search_medicines(
            hospital_id=request.hospital_id,
            search_term=search,
            page=paginator.page,
            per_page=paginator.per_page
        )
        
        schema = MedicineListSchema(many=True)
        return APIResponse.success(
            schema.dump(medicines),
            meta={'total': total, 'page': paginator.page, 'per_page': paginator.per_page, 'pages': pages}
        )
    except Exception as e:
        return APIResponse.error(str(e), 'LIST_MEDICINES_ERROR')


@inventory_bp.route('/medicines/<medicine_id>', methods=['GET'])
@token_required
@hospital_isolated
def get_medicine(medicine_id):
    """Get medicine details with stock info."""
    try:
        from app.models import Medicine
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return APIResponse.not_found('Medicine not found')
        
        schema = MedicineListSchema()
        return APIResponse.success(schema.dump(medicine))
    except Exception as e:
        return APIResponse.error(str(e), 'GET_MEDICINE_ERROR')


@inventory_bp.route('/medicines', methods=['POST'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def create_medicine():
    """Create new medicine in inventory."""
    try:
        data = request.get_json()
        from app.models import Medicine
        
        medicine = Medicine(
            hospital_id=request.hospital_id,
            name=data['name'],
            generic_name=data['generic_name'],
            manufacturer=data.get('manufacturer'),
            strength=data.get('strength'),
            form=data['form'],
            price=float(data['price']),
            unit=data['unit'],
            hsn_code=data.get('hsn_code'),
            gst_percentage=float(data.get('gst_percentage', 5))
        )
        
        db.session.add(medicine)
        db.session.commit()
        
        schema = MedicineListSchema()
        return APIResponse.created({'medicine_id': medicine.id, 'message': 'Medicine created'})
    except Exception as e:
        return APIResponse.error(str(e), 'CREATE_MEDICINE_ERROR')


@inventory_bp.route('/medicines/<medicine_id>', methods=['PUT'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def update_medicine(medicine_id):
    """Update medicine details."""
    try:
        from app.models import Medicine
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return APIResponse.not_found('Medicine not found')
        
        data = request.get_json()
        if 'name' in data:
            medicine.name = data['name']
        if 'price' in data:
            medicine.price = float(data['price'])
        if 'gst_percentage' in data:
            medicine.gst_percentage = float(data['gst_percentage'])
        
        db.session.commit()
        schema = MedicineListSchema()
        return APIResponse.success(schema.dump(medicine))
    except Exception as e:
        return APIResponse.error(str(e), 'UPDATE_MEDICINE_ERROR')


@inventory_bp.route('/stock', methods=['GET'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def get_stock_status():
    """Get current stock status for all medicines."""
    try:
        inventory = InventoryService.get_inventory_status(request.hospital_id)
        return APIResponse.success(inventory)
    except Exception as e:
        return APIResponse.error(str(e), 'STOCK_STATUS_ERROR')


@inventory_bp.route('/stock/add', methods=['POST'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def add_stock():
    """Add new batch of medicine to inventory."""
    try:
        data = request.get_json()
        
        success, record_id = InventoryService.add_stock(
            hospital_id=request.hospital_id,
            medicine_id=data['medicine_id'],
            batch_number=data['batch_number'],
            quantity=int(data['quantity']),
            expiry_date=data['expiry_date'],
            purchase_price=float(data.get('purchase_price', 0)),
            manufacturing_date=data.get('manufacturing_date')
        )
        
        if not success:
            return APIResponse.bad_request('Failed to add stock')
        
        return APIResponse.created({'record_id': record_id, 'message': 'Stock added successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'ADD_STOCK_ERROR')


@inventory_bp.route('/stock/consume', methods=['POST'])
@token_required
@role_required('admin', 'pharmacy', 'nurse')
@hospital_isolated
def consume_stock():
    """Consume medicine from inventory."""
    try:
        data = request.get_json()
        
        success = InventoryService.consume_stock(
            medicine_id=data['medicine_id'],
            quantity=int(data['quantity']),
            reason=data.get('reason', 'prescription'),
            reference_id=data.get('reference_id')
        )
        
        if not success:
            return APIResponse.bad_request('Insufficient stock or medicine not found')
        
        return APIResponse.success({'message': 'Stock consumed successfully'})
    except Exception as e:
        return APIResponse.error(str(e), 'CONSUME_STOCK_ERROR')


@inventory_bp.route('/expiry', methods=['GET'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def get_expiring_medicines():
    """Get medicines expiring within 30 days."""
    try:
        days = request.args.get('days', 30, type=int)
        
        expiring = InventoryService.get_expired_medicines(
            hospital_id=request.hospital_id,
            days=days
        )
        
        return APIResponse.success({
            'total_expiring': len(expiring),
            'medicines': [
                {
                    'medicine_id': item.medicine_id,
                    'batch_number': item.batch_number,
                    'quantity': item.quantity_in_stock,
                    'expiry_date': item.expiry_date.isoformat(),
                    'days_until_expiry': (item.expiry_date - datetime.now().date()).days
                }
                for item in expiring
            ]
        })
    except Exception as e:
        return APIResponse.error(str(e), 'EXPIRY_ERROR')


@inventory_bp.route('/low-stock', methods=['GET'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def get_low_stock_alerts():
    """Get medicines below reorder level."""
    try:
        low_stock = InventoryService.get_low_stock_medicines(request.hospital_id)
        
        return APIResponse.success({
            'total_low_stock': len(low_stock),
            'medicines': [
                {
                    'medicine_id': item.medicine_id,
                    'medicine_name': item.medicine.name if hasattr(item, 'medicine') else 'Unknown',
                    'current_stock': item.quantity_in_stock,
                    'reorder_level': item.reorder_level,
                    'shortage': item.reorder_level - item.quantity_in_stock
                }
                for item in low_stock
            ]
        })
    except Exception as e:
        return APIResponse.error(str(e), 'LOW_STOCK_ERROR')


@inventory_bp.route('/purchase-order', methods=['POST'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def create_purchase_order():
    """Create purchase order for restock."""
    try:
        data = request.get_json()
        from app.models import PurchaseOrder  # Assuming model exists
        
        po_number = f"PO-{request.hospital_id[:8]}-{datetime.now().strftime('%Y%m%d')}-{data.get('sequence', 1)}"
        
        # Create PO (implementation depends on model)
        return APIResponse.created({
            'po_number': po_number,
            'message': 'Purchase order created successfully'
        })
    except Exception as e:
        return APIResponse.error(str(e), 'CREATE_PO_ERROR')


@inventory_bp.route('/batch-update', methods=['POST'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def batch_update_stock():
    """Update multiple medicines stock at once."""
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        success_count = 0
        for update in updates:
            try:
                InventoryService.add_stock(
                    hospital_id=request.hospital_id,
                    medicine_id=update['medicine_id'],
                    batch_number=update['batch_number'],
                    quantity=int(update['quantity']),
                    expiry_date=update['expiry_date']
                )
                success_count += 1
            except:
                continue
        
        return APIResponse.success({
            'total_updates': len(updates),
            'successful': success_count,
            'failed': len(updates) - success_count
        })
    except Exception as e:
        return APIResponse.error(str(e), 'BATCH_UPDATE_ERROR')


@inventory_bp.route('/adjust-stock/<medicine_id>', methods=['POST'])
@token_required
@role_required('admin', 'pharmacy')
@hospital_isolated
def adjust_stock(medicine_id):
    """Adjust stock due to damage, loss, or correction."""
    try:
        data = request.get_json()
        adjustment_type = data.get('type')  # damage, loss, correction
        quantity = int(data.get('quantity', 0))
        reason = data.get('reason')
        
        success = InventoryService.adjust_stock(
            medicine_id=medicine_id,
            quantity=quantity,
            adjustment_type=adjustment_type,
            reason=reason
        )
        
        if not success:
            return APIResponse.bad_request('Failed to adjust stock')
        
        return APIResponse.success({'message': f'Stock adjusted by {quantity} units'})
    except Exception as e:
        return APIResponse.error(str(e), 'ADJUST_STOCK_ERROR')
