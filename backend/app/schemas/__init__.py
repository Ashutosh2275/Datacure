"""
Marshmallow schemas for request/response serialization.
Provides validation and transformation of API data.
"""
from marshmallow import Schema, fields, validate, pre_dump, post_load
from datetime import datetime


# ==================== USER & AUTHENTICATION SCHEMAS ====================

class UserBaseSchema(Schema):
    """Base schema for user data."""
    email = fields.Email(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.Str(allow_none=True)
    role = fields.Str(validate=validate.OneOf(['admin', 'doctor', 'nurse', 'patient', 'staff']))


class UserCreateSchema(UserBaseSchema):
    """Schema for creating new users."""
    password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True)


class UserResponseSchema(UserBaseSchema):
    """Schema for user responses."""
    id = fields.Str(dump_only=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    hospital_id = fields.Str()


class UserUpdateSchema(Schema):
    """Schema for updating user data."""
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)


class LoginSchema(Schema):
    """Schema for login request."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class TokenResponseSchema(Schema):
    """Schema for token response."""
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    expires_in = fields.Int()
    token_type = fields.Str(dump_default='Bearer')


# ==================== HOSPITAL SCHEMAS ====================

class HospitalBaseSchema(Schema):
    """Base schema for hospital data."""
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str(required=True)
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    postal_code = fields.Str(required=True)


class HospitalCreateSchema(HospitalBaseSchema):
    """Schema for creating hospitals."""
    gst_number = fields.Str(allow_none=True)
    registration_number = fields.Str(allow_none=True)


class HospitalResponseSchema(HospitalBaseSchema):
    """Schema for hospital responses."""
    id = fields.Str(dump_only=True)
    gst_number = fields.Str()
    registration_number = fields.Str()
    is_active = fields.Bool()
    subscription_tier = fields.Str()
    created_at = fields.DateTime(dump_only=True)


# ==================== PATIENT SCHEMAS ====================

class PatientBaseSchema(Schema):
    """Base schema for patient data."""
    date_of_birth = fields.Date(required=True)
    gender = fields.Str(required=True)
    blood_group = fields.Str(allow_none=True)
    weight = fields.Float(allow_none=True)
    height = fields.Float(allow_none=True)


class PatientCreateSchema(PatientBaseSchema):
    """Schema for creating patients."""
    user_id = fields.Str(required=True)
    allergies = fields.Str(allow_none=True)
    chronic_conditions = fields.Str(allow_none=True)
    insurance_provider = fields.Str(allow_none=True)
    insurance_policy_number = fields.Str(allow_none=True)


class PatientResponseSchema(PatientBaseSchema):
    """Schema for patient responses."""
    id = fields.Str(dump_only=True)
    patient_id_number = fields.Str()
    user = fields.Nested(UserResponseSchema, dump_only=True)
    allergies = fields.Str()
    chronic_conditions = fields.Str()
    insurance_provider = fields.Str()
    insurance_policy_number = fields.Str()
    insurance_expiry = fields.Date()
    emergency_contact_name = fields.Str()
    emergency_contact_phone = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class PatientListSchema(Schema):
    """Schema for patient list."""
    id = fields.Str()
    patient_id_number = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    gender = fields.Str()
    date_of_birth = fields.Date()
    blood_group = fields.Str()


# ==================== DOCTOR SCHEMAS ====================

class DoctorBaseSchema(Schema):
    """Base schema for doctor data."""
    license_number = fields.Str(required=True)
    specialization = fields.Str(required=True)
    experience_years = fields.Int()
    consultation_fee = fields.Float()


class DoctorCreateSchema(DoctorBaseSchema):
    """Schema for creating doctors."""
    user_id = fields.Str(required=True)
    qualification = fields.Str(allow_none=True)


class DoctorResponseSchema(DoctorBaseSchema):
    """Schema for doctor responses."""
    id = fields.Str(dump_only=True)
    user = fields.Nested(UserResponseSchema, dump_only=True)
    qualification = fields.Str()
    availability_status = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class DoctorSlotSchema(Schema):
    """Schema for doctor appointment slots."""
    id = fields.Str(dump_only=True)
    doctor_id = fields.Str(required=True)
    slot_date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    is_booked = fields.Bool(dump_only=True)
    capacity = fields.Int()


# ==================== APPOINTMENT SCHEMAS ====================

class AppointmentBaseSchema(Schema):
    """Base schema for appointment data."""
    appointment_date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)


class AppointmentCreateSchema(AppointmentBaseSchema):
    """Schema for creating appointments."""
    patient_id = fields.Str(required=True)
    doctor_id = fields.Str(required=True)
    appointment_type = fields.Str()
    chief_complaint = fields.Str()
    is_emergency = fields.Bool(allow_none=True, dump_default=False)


class AppointmentResponseSchema(AppointmentBaseSchema):
    """Schema for appointment responses."""
    id = fields.Str(dump_only=True)
    patient_id = fields.Str()
    doctor_id = fields.Str()
    status = fields.Str()
    appointment_type = fields.Str()
    chief_complaint = fields.Str()
    is_emergency = fields.Bool()
    is_telemedicine = fields.Bool()
    consultation_room = fields.Str()
    no_show_prediction_score = fields.Float()
    created_at = fields.DateTime(dump_only=True)


class AppointmentListSchema(Schema):
    """Schema for appointment list view."""
    id = fields.Str()
    patient_name = fields.Str()
    doctor_name = fields.Str()
    appointment_date = fields.Date()
    start_time = fields.Time()
    status = fields.Str()
    is_emergency = fields.Bool()


# ==================== PRESCRIPTION SCHEMAS ====================

class PrescriptionItemSchema(Schema):
    """Schema for prescription items."""
    id = fields.Str(dump_only=True)
    medicine_id = fields.Str(required=True)
    quantity = fields.Int(required=True)
    dosage = fields.Str(required=True)
    frequency = fields.Str(required=True)
    duration_days = fields.Int()
    instructions = fields.Str()


class PrescriptionCreateSchema(Schema):
    """Schema for creating prescriptions."""
    appointment_id = fields.Str(required=True)
    patient_id = fields.Str(required=True)
    items = fields.List(fields.Nested(PrescriptionItemSchema), required=True)
    notes = fields.Str()


class PrescriptionResponseSchema(Schema):
    """Schema for prescription responses."""
    id = fields.Str(dump_only=True)
    prescription_number = fields.Str()
    appointment_id = fields.Str()
    patient_id = fields.Str()
    doctor_id = fields.Str()
    status = fields.Str()
    dispensed_date = fields.DateTime()
    expiry_date = fields.Date()
    items = fields.List(fields.Nested(PrescriptionItemSchema), dump_only=True)
    notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class MedicineSchema(Schema):
    """Schema for medicine data."""
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    generic_name = fields.Str()
    manufacturer = fields.Str()
    type = fields.Str()
    strength = fields.Str()
    description = fields.Str()


# ==================== BILLING SCHEMAS ====================

class BillingItemSchema(Schema):
    """Schema for billing line items."""
    id = fields.Str(dump_only=True)
    description = fields.Str(required=True)
    quantity = fields.Int(dump_default=1)
    unit_price = fields.Float(required=True)
    service_type = fields.Str()


class BillingCreateSchema(Schema):
    """Schema for creating billing records."""
    patient_id = fields.Str(required=True)
    appointment_id = fields.Str(allow_none=True)
    items = fields.List(fields.Nested(BillingItemSchema), required=True)
    discount = fields.Float(dump_default=0)
    notes = fields.Str()


class BillingResponseSchema(Schema):
    """Schema for billing responses."""
    id = fields.Str(dump_only=True)
    invoice_number = fields.Str()
    patient_id = fields.Str()
    invoice_date = fields.Date()
    due_date = fields.Date()
    subtotal = fields.Float()
    gst_percentage = fields.Float()
    gst_amount = fields.Float()
    discount = fields.Float()
    total_amount = fields.Float()
    status = fields.Str()
    payment_method = fields.Str()
    payment_date = fields.DateTime()
    items = fields.List(fields.Nested(BillingItemSchema), dump_only=True)
    created_at = fields.DateTime(dump_only=True)


# ==================== BED & WARD SCHEMAS ====================

class WardBaseSchema(Schema):
    """Base schema for ward data."""
    name = fields.Str(required=True)
    ward_type = fields.Str(required=True)
    floor_number = fields.Int()
    total_beds = fields.Int(required=True)
    available_beds = fields.Int(dump_only=True)


class WardCreateSchema(WardBaseSchema):
    """Schema for creating wards."""
    description = fields.Str(allow_none=True)


class WardResponseSchema(WardBaseSchema):
    """Schema for ward responses."""
    id = fields.Str(dump_only=True)
    description = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class BedBaseSchema(Schema):
    """Base schema for bed data."""
    bed_number = fields.Str(required=True)
    bed_type = fields.Str()
    daily_rate = fields.Float()


class BedUpdateSchema(Schema):
    """Schema for updating bed status."""
    status = fields.Str(validate=validate.OneOf(['available', 'occupied', 'maintenance', 'reserved']))
    patient_id = fields.Str(allow_none=True)
    expected_discharge_date = fields.Date(allow_none=True)


class BedResponseSchema(BedBaseSchema):
    """Schema for bed responses."""
    id = fields.Str(dump_only=True)
    ward_id = fields.Str()
    status = fields.Str()
    patient_id = fields.Str()
    admission_date = fields.DateTime()
    expected_discharge_date = fields.Date()


# ==================== INVENTORY SCHEMAS ====================

class MedicineInventorySchema(Schema):
    """Schema for medicine inventory."""
    id = fields.Str(dump_only=True)
    medicine_id = fields.Str(required=True)
    batch_number = fields.Str(required=True)
    quantity = fields.Int(required=True)
    reorder_level = fields.Int()
    unit_cost = fields.Float(required=True)
    expiry_date = fields.Date(required=True)
    location = fields.Str()
    is_expired = fields.Bool(dump_only=True)


class SupplyOrderSchema(Schema):
    """Schema for supply orders."""
    id = fields.Str(dump_only=True)
    order_number = fields.Str()
    supplier_id = fields.Str(required=True)
    medicine_inventory_id = fields.Str(required=True)
    quantity_ordered = fields.Int(required=True)
    quantity_received = fields.Int()
    unit_cost = fields.Float(required=True)
    total_cost = fields.Float()
    order_date = fields.DateTime(dump_only=True)
    expected_delivery_date = fields.Date()
    actual_delivery_date = fields.Date()
    status = fields.Str()


# ==================== AI SCHEMAS ====================

class AIRiskScoreSchema(Schema):
    """Schema for AI risk scores."""
    id = fields.Str(dump_only=True)
    patient_id = fields.Str()
    risk_type = fields.Str()
    risk_score = fields.Float()
    risk_level = fields.Str()
    confidence_score = fields.Float()
    contributing_factors = fields.Dict()
    recommendation = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class AILogSchema(Schema):
    """Schema for AI logs."""
    id = fields.Str(dump_only=True)
    model_name = fields.Str()
    model_version = fields.Str()
    prediction_type = fields.Str()
    confidence_score = fields.Float()
    inference_time_ms = fields.Float()
    model_status = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class PredictionRequestSchema(Schema):
    """Schema for prediction requests."""
    patient_id = fields.Str(required=True)
    prediction_type = fields.Str(required=True)
    additional_data = fields.Dict(allow_none=True)


class PredictionResponseSchema(Schema):
    """Schema for prediction responses."""
    prediction_type = fields.Str()
    prediction_score = fields.Float()
    risk_level = fields.Str()
    confidence_score = fields.Float()
    explanation = fields.Dict()
    recommendations = fields.List(fields.Str())
    timestamp = fields.DateTime()


# ==================== AUDIT LOG SCHEMAS ====================

class AuditLogResponseSchema(Schema):
    """Schema for audit log responses."""
    id = fields.Str(dump_only=True)
    action = fields.Str()
    resource_type = fields.Str()
    resource_id = fields.Str()
    user_email = fields.Str()
    old_value = fields.Dict()
    new_value = fields.Dict()
    ip_address = fields.Str()
    status = fields.Str()
    details = fields.Str()
    created_at = fields.DateTime(dump_only=True)


# ==================== PAGINATION SCHEMAS ====================

class PaginationMetaSchema(Schema):
    """Schema for pagination metadata."""
    total = fields.Int()
    page = fields.Int()
    pages = fields.Int()
    per_page = fields.Int()
    has_next = fields.Bool()
    has_prev = fields.Bool()


class PaginatedResponseSchema(Schema):
    """Generic schema for paginated responses."""
    data = fields.List(fields.Dict())
    meta = fields.Nested(PaginationMetaSchema)


# ==================== LIST AND DETAIL SCHEMAS ====================

class UserListSchema(Schema):
    """Schema for listing users."""
    id = fields.Str()
    username = fields.Str()
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    role = fields.Str()
    hospital_id = fields.Str()
    created_at = fields.DateTime()


class UserDetailSchema(Schema):
    """Schema for user details."""
    id = fields.Str()
    username = fields.Str()
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    role = fields.Str()
    hospital_id = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class UserUpdateSchema(Schema):
    """Schema for updating user."""
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    password = fields.Str(allow_none=True)


class DoctorListSchema(Schema):
    """Schema for listing doctors."""
    id = fields.Str()
    user_id = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    specialization = fields.Str()
    license_number = fields.Str()
    hospital_id = fields.Str()


class PatientListSchema(Schema):
    """Schema for listing patients."""
    id = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    date_of_birth = fields.Date()
    gender = fields.Str()
    phone_number = fields.Str()
    hospital_id = fields.Str()


class WardListSchema(Schema):
    """Schema for listing wards."""
    id = fields.Str()
    name = fields.Str()
    hospital_id = fields.Str()
    total_beds = fields.Int()
    available_beds = fields.Int()


class BedDetailSchema(Schema):
    """Schema for bed details."""
    id = fields.Str()
    ward_id = fields.Str()
    bed_number = fields.Str()
    status = fields.Str()
    patient_id = fields.Str(allow_none=True)


class MedicineListSchema(Schema):
    """Schema for listing medicines."""
    id = fields.Str()
    name = fields.Str()
    manufacturer = fields.Str()
    quantity = fields.Int()
    hospital_id = fields.Str()


class InventorySchema(Schema):
    """Schema for inventory items."""
    id = fields.Str()
    name = fields.Str()
    quantity = fields.Int()
    unit = fields.Str()
    hospital_id = fields.Str()


class BillingListSchema(Schema):
    """Schema for listing bills."""
    id = fields.Str()
    patient_id = fields.Str()
    total_amount = fields.Float()
    status = fields.Str()
    created_at = fields.DateTime()


class BillingDetailSchema(Schema):
    """Schema for billing details."""
    id = fields.Str()
    patient_id = fields.Str()
    appointment_id = fields.Str()
    items = fields.List(fields.Nested(BillingItemSchema))
    total_amount = fields.Float()
    status = fields.Str()
    created_at = fields.DateTime()


class BillingCreateSchema(Schema):
    """Schema for creating billing."""
    patient_id = fields.Str(required=True)
    appointment_id = fields.Str(allow_none=True)
    items = fields.List(fields.Nested(BillingItemSchema), required=True)
    discount = fields.Float(dump_default=0)
    notes = fields.Str()