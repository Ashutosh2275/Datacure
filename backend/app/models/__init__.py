"""
Database models for DataCure - Hospital Intelligence Platform.
Implements clean architecture with proper relationships and constraints.
"""
import uuid
from datetime import datetime, timedelta
from enum import Enum
from app.extensions import db, TimestampMixin, SoftDeleteMixin


class RoleEnum(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    PATIENT = "patient"
    STAFF = "staff"


class AppointmentStatusEnum(str, Enum):
    """Appointment status enumeration."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class BillingStatusEnum(str, Enum):
    """Billing status enumeration."""
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PrescriptionStatusEnum(str, Enum):
    """Prescription status enumeration."""
    ISSUED = "issued"
    DISPENSED = "dispensed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WardTypeEnum(str, Enum):
    """Ward type enumeration."""
    GENERAL = "general"
    ICU = "icu"
    PEDIATRICS = "pediatrics"
    MATERNITY = "maternity"
    SURGERY = "surgery"


class BedStatusEnum(str, Enum):
    """Bed status enumeration."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


# ==================== USER & AUTHENTICATION ====================

class User(db.Model, TimestampMixin, SoftDeleteMixin):
    """User model for system authentication and access control."""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    role = db.Column(db.Enum(RoleEnum), nullable=False, index=True)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False, index=True)
    
    # Relationships
    doctor = db.relationship('Doctor', uselist=False, back_populates='user')
    patient = db.relationship('Patient', uselist=False, back_populates='user')
    audit_logs = db.relationship('AuditLog', uselist=True, back_populates='user')
    
    def __repr__(self):
        return f'<User {self.email}>'


class Hospital(db.Model, TimestampMixin):
    """Hospital model for multi-hospital SaaS support."""
    __tablename__ = 'hospitals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default='India')
    registration_number = db.Column(db.String(100), unique=True)
    gst_number = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    subscription_tier = db.Column(db.String(50), default='standard')  # basic, standard, premium
    
    # Relationships
    users = db.relationship('User', cascade='all, delete-orphan')
    patients = db.relationship('Patient', cascade='all, delete-orphan')
    doctors = db.relationship('Doctor', cascade='all, delete-orphan')
    wards = db.relationship('Ward', cascade='all, delete-orphan')
    inventory = db.relationship('MedicineInventory', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Hospital {self.name}>'


# ==================== PATIENT MANAGEMENT ====================

class Patient(db.Model, TimestampMixin, SoftDeleteMixin):
    """Patient model with comprehensive medical and demographic information."""
    __tablename__ = 'patients'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False, index=True)
    patient_id_number = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Unique ID
    
    # Personal Information
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(10))
    weight = db.Column(db.Float)  # in kg
    height = db.Column(db.Float)  # in cm
    
    # Medical Information
    allergies = db.Column(db.Text)
    chronic_conditions = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    
    # Insurance Information
    insurance_provider = db.Column(db.String(255))
    insurance_policy_number = db.Column(db.String(100))
    insurance_expiry = db.Column(db.Date)
    
    # Relationships
    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', cascade='all, delete-orphan')
    medical_records = db.relationship('MedicalRecord', cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', cascade='all, delete-orphan')
    billing_records = db.relationship('Billing', cascade='all, delete-orphan')
    ai_risk_scores = db.relationship('AIRiskScore', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.patient_id_number}>'


class MedicalRecord(db.Model, TimestampMixin, SoftDeleteMixin):
    """Medical records for patients with file uploads."""
    __tablename__ = 'medical_records'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    doctor_id = db.Column(db.String(36), db.ForeignKey('doctors.id'), nullable=False)
    
    record_type = db.Column(db.String(100), nullable=False)  # lab_report, scan, xray, etc.
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    file_url = db.Column(db.String(500))  # S3 or Firebase URL
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)  # in bytes
    
    diagnosis = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='medical_records')
    doctor = db.relationship('Doctor', back_populates='medical_records')
    
    def __repr__(self):
        return f'<MedicalRecord {self.record_type} for Patient {self.patient_id}>'


# ==================== DOCTOR MANAGEMENT ====================

class Doctor(db.Model, TimestampMixin, SoftDeleteMixin):
    """Doctor model with specialization and availability."""
    __tablename__ = 'doctors'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False, index=True)
    
    license_number = db.Column(db.String(100), unique=True, nullable=False)
    specialization = db.Column(db.String(100), nullable=False, index=True)
    qualification = db.Column(db.Text)
    experience_years = db.Column(db.Integer, default=0)
    
    consultation_fee = db.Column(db.Float, default=0)
    availability_status = db.Column(db.String(50), default='available')  # available, busy, on_leave
    
    # Relationships
    user = db.relationship('User', back_populates='doctor')
    appointments = db.relationship('Appointment', cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', cascade='all, delete-orphan')
    medical_records = db.relationship('MedicalRecord', cascade='all, delete-orphan')
    doctor_slots = db.relationship('DoctorSlot', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Doctor {self.user_id} - {self.specialization}>'


class DoctorSlot(db.Model, TimestampMixin):
    """Doctor's appointment slot availability."""
    __tablename__ = 'doctor_slots'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = db.Column(db.String(36), db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False, index=True)
    
    slot_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    capacity = db.Column(db.Integer, default=1)  # patients per slot
    
    # Relationships
    doctor = db.relationship('Doctor', back_populates='doctor_slots')
    appointments = db.relationship('Appointment', cascade='all, delete-orphan', back_populates='slot')
    
    def __repr__(self):
        return f'<DoctorSlot {self.doctor_id} on {self.slot_date}>'


# ==================== APPOINTMENT MANAGEMENT ====================

class Appointment(db.Model, TimestampMixin, SoftDeleteMixin):
    """Appointment model with scheduling and status tracking."""
    __tablename__ = 'appointments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    doctor_id = db.Column(db.String(36), db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False, index=True)
    slot_id = db.Column(db.String(36), db.ForeignKey('doctor_slots.id'), nullable=True)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False, index=True)
    
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    status = db.Column(db.Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.SCHEDULED, index=True)
    appointment_type = db.Column(db.String(50))  # consultation, follow-up, emergency, etc.
    chief_complaint = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    is_emergency = db.Column(db.Boolean, default=False, index=True)
    is_telemedicine = db.Column(db.Boolean, default=False)
    consultation_room = db.Column(db.String(100))
    
    reminder_sent = db.Column(db.Boolean, default=False)
    no_show_prediction_score = db.Column(db.Float)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    slot = db.relationship('DoctorSlot', back_populates='appointments')
    hospital = db.relationship('Hospital')
    prescription = db.relationship('Prescription', uselist=False, back_populates='appointment')
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.patient_id} with {self.doctor_id}>'


# ==================== PRESCRIPTION & MEDICINE ====================

class Prescription(db.Model, TimestampMixin, SoftDeleteMixin):
    """Prescription model for medicine management."""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    appointment_id = db.Column(db.String(36), db.ForeignKey('appointments.id', ondelete='CASCADE'), nullable=False, index=True)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    doctor_id = db.Column(db.String(36), db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False, index=True)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False)
    
    prescription_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    status = db.Column(db.Enum(PrescriptionStatusEnum), default=PrescriptionStatusEnum.ISSUED, index=True)
    
    notes = db.Column(db.Text)
    dispensed_date = db.Column(db.DateTime)
    expiry_date = db.Column(db.Date)
    
    # Relationships
    appointment = db.relationship('Appointment', back_populates='prescription')
    patient = db.relationship('Patient', back_populates='prescriptions')
    doctor = db.relationship('Doctor', back_populates='prescriptions')
    prescription_items = db.relationship('PrescriptionItem', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Prescription {self.prescription_number}>'


class PrescriptionItem(db.Model, TimestampMixin):
    """Individual medicine items in a prescription."""
    __tablename__ = 'prescription_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prescription_id = db.Column(db.String(36), db.ForeignKey('prescriptions.id', ondelete='CASCADE'), nullable=False)
    medicine_id = db.Column(db.String(36), db.ForeignKey('medicines.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    dosage = db.Column(db.String(100), nullable=False)  # e.g., "500mg"
    frequency = db.Column(db.String(100), nullable=False)  # e.g., "Twice daily after food"
    duration_days = db.Column(db.Integer)
    instructions = db.Column(db.Text)
    side_effects_noted = db.Column(db.Text)
    
    # Relationships
    prescription = db.relationship('Prescription', back_populates='prescription_items')
    medicine = db.relationship('Medicine', back_populates='prescription_items')
    
    def __repr__(self):
        return f'<PrescriptionItem {self.medicine_id} in Prescription {self.prescription_id}>'


class Medicine(db.Model, TimestampMixin, SoftDeleteMixin):
    """Medicine master list with properties."""
    __tablename__ = 'medicines'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, index=True)
    generic_name = db.Column(db.String(255))
    manufacturer = db.Column(db.String(255), index=True)
    
    type = db.Column(db.String(100))  # tablet, injection, syrup, etc.
    strength = db.Column(db.String(100))
    unit_of_measure = db.Column(db.String(50))  # tablet, ml, vial, etc.
    
    description = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    
    # Relationships
    prescription_items = db.relationship('PrescriptionItem', back_populates='medicine')
    inventory_items = db.relationship('MedicineInventory', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Medicine {self.name}>'


class MedicineInventory(db.Model, TimestampMixin):
    """Inventory tracking for medicines with batch and expiry."""
    __tablename__ = 'medicine_inventory'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id', ondelete='CASCADE'), nullable=False, index=True)
    medicine_id = db.Column(db.String(36), db.ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    
    batch_number = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, default=50)
    unit_cost = db.Column(db.Float, nullable=False)
    
    manufacturing_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    location = db.Column(db.String(100))  # shelf, refrigerator, etc.
    
    is_expired = db.Column(db.Boolean, default=False)
    is_recalled = db.Column(db.Boolean, default=False)
    
    # Relationships
    hospital = db.relationship('Hospital', back_populates='inventory')
    medicine = db.relationship('Medicine', back_populates='inventory_items')
    supply_orders = db.relationship('SupplyOrder', back_populates='medicine_inventory')
    
    def __repr__(self):
        return f'<MedicineInventory {self.medicine_id} - Qty: {self.quantity}>'


class SupplyOrder(db.Model, TimestampMixin):
    """Purchase orders for medicine supply from suppliers."""
    __tablename__ = 'supply_orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medicine_inventory_id = db.Column(db.String(36), db.ForeignKey('medicine_inventory.id'), nullable=False)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False)
    supplier_id = db.Column(db.String(36), db.ForeignKey('suppliers.id'), nullable=False)
    
    order_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    quantity_ordered = db.Column(db.Integer, nullable=False)
    quantity_received = db.Column(db.Integer, default=0)
    
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered
    
    # Relationships
    medicine_inventory = db.relationship('MedicineInventory', back_populates='supply_orders')
    supplier = db.relationship('Supplier', back_populates='supply_orders')
    
    def __repr__(self):
        return f'<SupplyOrder {self.order_number}>'


class Supplier(db.Model, TimestampMixin, SoftDeleteMixin):
    """Supplier information for inventory management."""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    contact_person = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    
    gst_number = db.Column(db.String(50))
    payment_terms = db.Column(db.String(100))
    
    # Relationships
    supply_orders = db.relationship('SupplyOrder', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'


# ==================== BILLING & FINANCE ====================

class Billing(db.Model, TimestampMixin, SoftDeleteMixin):
    """Billing and invoice model with payment tracking."""
    __tablename__ = 'billing'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False)
    appointment_id = db.Column(db.String(36), db.ForeignKey('appointments.id'), nullable=True)
    
    invoice_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    invoice_date = db.Column(db.Date, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    
    subtotal = db.Column(db.Float, nullable=False)
    gst_percentage = db.Column(db.Float, default=18.0)
    gst_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    
    status = db.Column(db.Enum(BillingStatusEnum), default=BillingStatusEnum.PENDING, index=True)
    
    payment_method = db.Column(db.String(50))  # cash, card, insurance, upi
    payment_date = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(255), unique=True)
    
    notes = db.Column(db.Text)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='billing_records')
    hospital = db.relationship('Hospital')
    appointment = db.relationship('Appointment')
    billing_items = db.relationship('BillingItem', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Billing {self.invoice_number}>'


class BillingItem(db.Model, TimestampMixin):
    """Individual line items in a billing invoice."""
    __tablename__ = 'billing_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    billing_id = db.Column(db.String(36), db.ForeignKey('billing.id', ondelete='CASCADE'), nullable=False)
    
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    service_type = db.Column(db.String(100))  # consultation, lab_test, medicine, room_charge, etc.
    
    # Relationships
    billing = db.relationship('Billing', back_populates='billing_items')
    
    def __repr__(self):
        return f'<BillingItem {self.description}>'


# ==================== BED & WARD MANAGEMENT ====================

class Ward(db.Model, TimestampMixin, SoftDeleteMixin):
    """Hospital ward model with capacity and type."""
    __tablename__ = 'wards'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id', ondelete='CASCADE'), nullable=False, index=True)
    
    name = db.Column(db.String(255), nullable=False, index=True)
    ward_type = db.Column(db.Enum(WardTypeEnum), nullable=False, index=True)
    floor_number = db.Column(db.Integer)
    
    total_beds = db.Column(db.Integer, nullable=False)
    available_beds = db.Column(db.Integer, nullable=False)
    
    description = db.Column(db.Text)
    
    # Relationships
    beds = db.relationship('Bed', cascade='all, delete-orphan')
    hospital = db.relationship('Hospital', back_populates='wards')
    
    def __repr__(self):
        return f'<Ward {self.name}>'


class Bed(db.Model, TimestampMixin):
    """Individual bed in a ward."""
    __tablename__ = 'beds'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ward_id = db.Column(db.String(36), db.ForeignKey('wards.id', ondelete='CASCADE'), nullable=False, index=True)
    
    bed_number = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(BedStatusEnum), default=BedStatusEnum.AVAILABLE, index=True)
    
    bed_type = db.Column(db.String(100))  # standard, deluxe, icu, etc.
    daily_rate = db.Column(db.Float, default=0)
    
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=True)
    admission_date = db.Column(db.DateTime)
    expected_discharge_date = db.Column(db.Date)
    
    last_maintenance = db.Column(db.DateTime)
    
    # Relationships
    ward = db.relationship('Ward', back_populates='beds')
    patient = db.relationship('Patient')
    
    def __repr__(self):
        return f'<Bed {self.bed_number} in Ward {self.ward_id}>'


# ==================== AI & ANALYTICS ====================

class AIRiskScore(db.Model, TimestampMixin):
    """AI-generated risk scores for patients."""
    __tablename__ = 'ai_risk_scores'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False)
    
    risk_type = db.Column(db.String(100), nullable=False, index=True)  # readmission, no_show, etc.
    risk_score = db.Column(db.Float, nullable=False)  # 0-1
    risk_level = db.Column(db.String(50))  # low, medium, high
    
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float)
    
    contributing_factors = db.Column(db.JSON)  # List of important factors
    model_version = db.Column(db.String(50))
    
    recommendation = db.Column(db.Text)
    is_acted_upon = db.Column(db.Boolean, default=False)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='ai_risk_scores')
    hospital = db.relationship('Hospital')
    
    def __repr__(self):
        return f'<AIRiskScore {self.risk_type} - {self.patient_id}>'


class AILog(db.Model, TimestampMixin):
    """Logs for AI model predictions and monitoring."""
    __tablename__ = 'ai_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False, index=True)
    
    model_name = db.Column(db.String(255), nullable=False, index=True)
    model_version = db.Column(db.String(50))
    
    prediction_type = db.Column(db.String(100))  # flow, readmission, etc.
    input_features = db.Column(db.JSON)
    output_prediction = db.Column(db.Float)
    
    confidence_score = db.Column(db.Float)
    inference_time_ms = db.Column(db.Float)
    
    model_status = db.Column(db.String(50))  # success, error, timeout
    error_message = db.Column(db.Text)
    
    hospital = db.relationship('Hospital')
    
    def __repr__(self):
        return f'<AILog {self.model_name} v{self.model_version}>'


class ModelMetrics(db.Model, TimestampMixin):
    """Performance metrics for deployed AI models."""
    __tablename__ = 'model_metrics'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False, index=True)
    
    model_name = db.Column(db.String(255), nullable=False, index=True)
    model_version = db.Column(db.String(50), nullable=False)
    
    # Classification metrics
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    auc_roc = db.Column(db.Float)
    
    # Training info
    training_samples = db.Column(db.Integer)
    last_training_date = db.Column(db.DateTime)
    
    # Data drift detection
    data_drift_detected = db.Column(db.Boolean, default=False)
    drift_severity = db.Column(db.String(50))  # low, medium, high
    
    retraining_needed = db.Column(db.Boolean, default=False)
    
    hospital = db.relationship('Hospital')
    
    def __repr__(self):
        return f'<ModelMetrics {self.model_name} v{self.model_version}>'


# ==================== AUDIT & LOGGING ====================

class AuditLog(db.Model, TimestampMixin):
    """Comprehensive audit logs for compliance and security."""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False, index=True)
    
    action = db.Column(db.String(255), nullable=False, index=True)
    resource_type = db.Column(db.String(100), nullable=False)  # User, Patient, Appointment, etc.
    resource_id = db.Column(db.String(36), nullable=False, index=True)
    
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    status = db.Column(db.String(50), default='success')  # success, failed, error
    
    details = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', back_populates='audit_logs')
    hospital = db.relationship('Hospital')

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.resource_type}>'


# ==================== AUTHENTICATION & SECURITY ====================

class TokenBlacklist(db.Model):
    """Blacklisted JWT tokens for logout functionality."""
    __tablename__ = 'token_blacklist'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token_jti = db.Column(db.String(255), unique=True, nullable=False, index=True)  # JWT ID claim
    token_type = db.Column(db.String(20), default='access')  # access or refresh
    blacklisted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)  # When token naturally expires
    reason = db.Column(db.String(255))  # logout, password_change, security, etc.

    # Relationships
    user = db.relationship('User')

    def __repr__(self):
        return f'<TokenBlacklist {self.user_id} {self.token_type}>'

    @classmethod
    def is_token_blacklisted(cls, token_jti: str) -> bool:
        """Check if token JTI is blacklisted."""
        return cls.query.filter_by(token_jti=token_jti).first() is not None

    @classmethod
    def blacklist_token(cls, user_id: str, token_jti: str, token_type: str = 'access',
                       expires_at: datetime = None, reason: str = None):
        """Add token to blacklist."""
        blacklist_entry = cls(
            user_id=user_id,
            token_jti=token_jti,
            token_type=token_type,
            expires_at=expires_at or datetime.utcnow(),
            reason=reason
        )
        db.session.add(blacklist_entry)
        db.session.commit()


class PasswordResetToken(db.Model, TimestampMixin):
    """Password reset tokens for account recovery."""
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)  # Token expiry (typically 1 hour)
    used_at = db.Column(db.DateTime, nullable=True)  # When token was used
    ip_address = db.Column(db.String(50))  # IP address of reset request
    user_agent = db.Column(db.String(500))  # Browser/client info

    # Relationships
    user = db.relationship('User')

    def __repr__(self):
        return f'<PasswordResetToken {self.user_id}>'

    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not yet used)."""
        return (
            self.expires_at > datetime.utcnow() and
            self.used_at is None
        )

    @classmethod
    def create_reset_token(cls, user_id: str, token: str, ip_address: str = None,
                          user_agent: str = None, validity_hours: int = 1):
        """Create a new password reset token."""
        reset_token = cls(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=validity_hours),
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(reset_token)
        db.session.commit()
        return reset_token

    @classmethod
    def get_valid_token(cls, token: str):
        """Get a valid reset token by its value."""
        reset_token = cls.query.filter_by(token=token).first()
        if reset_token and reset_token.is_valid():
            return reset_token
        return None