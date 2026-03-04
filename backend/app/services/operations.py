"""
Billing, Inventory, and Ward Management Services.
"""
from typing import Optional, Tuple, Dict, List
from datetime import date
from app.extensions import db
from app.utils import get_logger, IDGenerator, DataTransformer
from app.repositories import BillingRepository, InventoryRepository, BedRepository
from app.models import (
    Billing, BillingItem, Medicine, MedicineInventory, SupplyOrder, Supplier,
    Ward, Bed, BillingStatusEnum, BedStatusEnum
)


logger = get_logger(__name__)


# ==================== BILLING SERVICE ====================

class BillingService:
    """Handles billing and invoicing."""
    
    def __init__(self):
        self.billing_repo = BillingRepository()
    
    def create_invoice(self, patient_id: str, hospital_id: str, items: List[Dict],
                      appointment_id: str = None, discount: float = 0,
                      gst_percentage: float = 18.0, notes: str = None) -> Tuple[bool, Dict]:
        """
        Create invoice for patient.
        
        Args:
            patient_id: Patient ID
            hospital_id: Hospital ID
            items: List of {'description', 'quantity', 'unit_price', 'service_type'}
            appointment_id: Optional appointment ID
            discount: Discount amount
            gst_percentage: GST percentage (default 18%)
            notes: Invoice notes
            
        Returns:
            (success, response_dict) tuple
        """
        try:
            # Calculate subtotal
            subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
            gst_amount = (subtotal - discount) * (gst_percentage / 100)
            total_amount = subtotal - discount + gst_amount
            
            # Generate invoice number
            invoice_number = IDGenerator.generate_invoice_number(hospital_id[:3].upper())
            
            billing = Billing(
                patient_id=patient_id,
                hospital_id=hospital_id,
                appointment_id=appointment_id,
                invoice_number=invoice_number,
                subtotal=subtotal,
                gst_percentage=gst_percentage,
                gst_amount=gst_amount,
                discount=discount,
                total_amount=total_amount,
                status=BillingStatusEnum.PENDING,
                notes=notes,
            )
            
            # Add line items
            for item in items:
                billing_item = BillingItem(
                    description=item['description'],
                    quantity=item.get('quantity', 1),
                    unit_price=item['unit_price'],
                    total_price=item.get('quantity', 1) * item['unit_price'],
                    service_type=item.get('service_type'),
                )
                billing.billing_items.append(billing_item)
            
            db.session.add(billing)
            db.session.commit()
            
            logger.info(f"Invoice created: {invoice_number}")
            
            return True, {
                'message': 'Invoice created',
                'billing_id': billing.id,
                'invoice_number': invoice_number,
                'total_amount': total_amount,
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating invoice: {str(e)}")
            return False, {'message': 'Invoice creation failed'}
    
    def get_invoice(self, billing_id: str) -> Optional[Billing]:
        """Get invoice by ID."""
        return self.billing_repo.get_by_id(billing_id)
    
    def get_patient_invoices(self, patient_id: str) -> List[Billing]:
        """Get all invoices for patient."""
        return self.billing_repo.get_by_patient(patient_id)
    
    def record_payment(self, billing_id: str, amount: float, payment_method: str,
                      transaction_id: str = None) -> Tuple[bool, Dict]:
        """
        Record payment for invoice.
        
        Args:
            billing_id: Billing ID
            amount: Payment amount
            payment_method: Payment method (cash, card, insurance, upi)
            transaction_id: Transaction ID for online payments
            
        Returns:
            (success, response_dict) tuple
        """
        billing = self.get_invoice(billing_id)
        if not billing:
            return False, {'message': 'Invoice not found'}
        
        try:
            if amount >= billing.total_amount:
                billing.status = BillingStatusEnum.PAID
            elif amount > 0:
                billing.status = BillingStatusEnum.PARTIAL
            
            billing.payment_method = payment_method
            billing.payment_date = db.func.now()
            billing.transaction_id = transaction_id
            
            db.session.commit()
            
            logger.info(f"Payment recorded for invoice: {billing_id}")
            
            return True, {
                'message': 'Payment recorded',
                'status': billing.status,
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error recording payment: {str(e)}")
            return False, {'message': 'Payment recording failed'}
    
    def get_revenue_report(self, hospital_id: str, start_date: date = None,
                          end_date: date = None) -> Dict:
        """Get revenue report for hospital."""
        try:
            query = Billing.query.filter_by(hospital_id=hospital_id)
            
            if start_date:
                query = query.filter(Billing.invoice_date >= start_date)
            if end_date:
                query = query.filter(Billing.invoice_date <= end_date)
            
            invoices = query.all()
            
            total_revenue = sum(inv.total_amount for inv in invoices if inv.status in ['paid', 'partial'])
            total_pending = sum(inv.total_amount for inv in invoices if inv.status == 'pending')
            total_invoices = len(invoices)
            
            return {
                'total_revenue': total_revenue,
                'pending_amount': total_pending,
                'total_invoices': total_invoices,
                'paid_invoices': sum(1 for inv in invoices if inv.status == 'paid'),
            }
        
        except Exception as e:
            logger.error(f"Error getting revenue report: {str(e)}")
            return {}


# ==================== INVENTORY SERVICE ====================

class InventoryService:
    """Handles medicine inventory management."""
    
    def __init__(self):
        self.inventory_repo = InventoryRepository()
    
    def add_medicine(self, name: str, generic_name: str = None, manufacturer: str = None,
                    medicine_type: str = None, strength: str = None, **kwargs) -> Tuple[bool, Dict]:
        """Add new medicine to master list."""
        try:
            medicine = Medicine(
                name=name,
                generic_name=generic_name,
                manufacturer=manufacturer,
                type=medicine_type,
                strength=strength,
                **kwargs
            )
            
            db.session.add(medicine)
            db.session.commit()
            
            logger.info(f"Medicine added: {name}")
            return True, {'message': 'Medicine added', 'medicine_id': medicine.id}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding medicine: {str(e)}")
            return False, {'message': 'Medicine addition failed'}
    
    def add_stock(self, hospital_id: str, medicine_id: str, batch_number: str,
                 quantity: int, unit_cost: float, expiry_date: date,
                 **kwargs) -> Tuple[bool, Dict]:
        """Add medicine stock to inventory."""
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return False, {'message': 'Medicine not found'}
        
        try:
            inventory = MedicineInventory(
                hospital_id=hospital_id,
                medicine_id=medicine_id,
                batch_number=batch_number,
                quantity=quantity,
                unit_cost=unit_cost,
                expiry_date=expiry_date,
                **kwargs
            )
            
            db.session.add(inventory)
            db.session.commit()
            
            logger.info(f"Stock added for medicine {medicine_id}: {quantity} units")
            return True, {'message': 'Stock added', 'inventory_id': inventory.id}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding stock: {str(e)}")
            return False, {'message': 'Stock addition failed'}
    
    def get_inventory_status(self, hospital_id: str) -> Dict:
        """Get inventory status summary."""
        try:
            expired = self.inventory_repo.get_expired_medicines(hospital_id)
            low_stock = self.inventory_repo.get_low_stock_medicines(hospital_id)
            
            total_inventory = MedicineInventory.query.filter_by(hospital_id=hospital_id).count()
            
            return {
                'total_medicines': total_inventory,
                'expired_count': len(expired),
                'low_stock_count': len(low_stock),
                'expired_medicines': [m.medicine.name for m in expired[:5]],
                'low_stock_medicines': [m.medicine.name for m in low_stock[:5]],
            }
        
        except Exception as e:
            logger.error(f"Error getting inventory status: {str(e)}")
            return {}
    
    def consume_stock(self, inventory_id: str, quantity: int) -> Tuple[bool, Dict]:
        """Deduct stock from inventory."""
        inventory = MedicineInventory.query.get(inventory_id)
        if not inventory:
            return False, {'message': 'Inventory not found'}
        
        if inventory.quantity < quantity:
            return False, {'message': 'Insufficient stock'}
        
        try:
            inventory.quantity -= quantity
            db.session.commit()
            logger.info(f"Stock consumed from {inventory_id}: {quantity} units")
            return True, {'message': 'Stock updated'}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating stock: {str(e)}")
            return False, {'message': 'Stock update failed'}


# ==================== WARD & BED SERVICE ====================

class WardService:
    """Handles ward and bed management."""
    
    def __init__(self):
        self.bed_repo = BedRepository()
    
    def create_ward(self, hospital_id: str, name: str, ward_type: str, total_beds: int,
                   floor_number: int = None, description: str = None) -> Tuple[bool, Dict]:
        """Create new ward."""
        try:
            ward = Ward(
                hospital_id=hospital_id,
                name=name,
                ward_type=ward_type,
                total_beds=total_beds,
                available_beds=total_beds,
                floor_number=floor_number,
                description=description,
            )
            
            # Create beds
            for i in range(1, total_beds + 1):
                bed = Bed(
                    ward_id=ward.id,
                    bed_number=f"{ward_type.upper()}-{i}",
                    status=BedStatusEnum.AVAILABLE,
                )
                ward.beds.append(bed)
            
            db.session.add(ward)
            db.session.commit()
            
            logger.info(f"Ward created: {name} with {total_beds} beds")
            return True, {'message': 'Ward created', 'ward_id': ward.id}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating ward: {str(e)}")
            return False, {'message': 'Ward creation failed'}
    
    def allocate_bed(self, bed_id: str, patient_id: str,
                    expected_discharge_date: date = None) -> Tuple[bool, Dict]:
        """Allocate bed to patient."""
        bed = Bed.query.get(bed_id)
        if not bed:
            return False, {'message': 'Bed not found'}
        
        if bed.status != BedStatusEnum.AVAILABLE:
            return False, {'message': 'Bed not available'}
        
        try:
            bed.patient_id = patient_id
            bed.status = BedStatusEnum.OCCUPIED
            bed.admission_date = db.func.now()
            bed.expected_discharge_date = expected_discharge_date
            
            # Update ward available beds count
            bed.ward.available_beds -= 1
            
            db.session.commit()
            
            logger.info(f"Bed allocated: {bed_id} to patient {patient_id}")
            return True, {'message': 'Bed allocated'}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error allocating bed: {str(e)}")
            return False, {'message': 'Allocation failed'}
    
    def discharge_patient(self, bed_id: str) -> Tuple[bool, Dict]:
        """Discharge patient and release bed."""
        bed = Bed.query.get(bed_id)
        if not bed:
            return False, {'message': 'Bed not found'}
        
        try:
            bed.status = BedStatusEnum.AVAILABLE
            bed.patient_id = None
            bed.admission_date = None
            bed.expected_discharge_date = None
            
            # Update ward available beds
            bed.ward.available_beds += 1
            
            db.session.commit()
            
            logger.info(f"Patient discharged from bed: {bed_id}")
            return True, {'message': 'Patient discharged'}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error discharging patient: {str(e)}")
            return False, {'message': 'Discharge failed'}
    
    def get_occupancy_status(self, hospital_id: str) -> Dict:
        """Get bed occupancy status."""
        try:
            wards = Ward.query.filter_by(hospital_id=hospital_id).all()
            
            total_beds = sum(w.total_beds for w in wards)
            occupied_beds = sum(w.total_beds - w.available_beds for w in wards)
            occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0
            
            return {
                'total_beds': total_beds,
                'occupied_beds': occupied_beds,
                'available_beds': total_beds - occupied_beds,
                'occupancy_rate': round(occupancy_rate, 2),
            }
        
        except Exception as e:
            logger.error(f"Error getting occupancy status: {str(e)}")
            return {}
