"""Initial schema creation for DataCure


Revision ID: 001_initial_schema
Revises:
Create Date: 2025-03-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for DataCure application."""

    # Create enums
    op.execute('''
        CREATE TYPE role_enum AS ENUM (
            'admin', 'doctor', 'nurse', 'patient', 'staff'
        )
    ''')

    op.execute('''
        CREATE TYPE appointment_status_enum AS ENUM (
            'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show', 'rescheduled'
        )
    ''')

    op.execute('''
        CREATE TYPE billing_status_enum AS ENUM (
            'pending', 'paid', 'partial', 'refunded', 'cancelled'
        )
    ''')

    op.execute('''
        CREATE TYPE prescription_status_enum AS ENUM (
            'issued', 'dispensed', 'completed', 'cancelled'
        )
    ''')

    op.execute('''
        CREATE TYPE ward_type_enum AS ENUM (
            'general', 'icu', 'pediatrics', 'maternity', 'surgery'
        )
    ''')

    op.execute('''
        CREATE TYPE bed_status_enum AS ENUM (
            'available', 'occupied', 'maintenance', 'reserved'
        )
    ''')

    # hospitals table
    op.create_table('hospitals',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('postal_code', sa.String(20), nullable=False),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('gst_number', sa.String(20), nullable=True),
        sa.Column('license_number', sa.String(50), nullable=True),
        sa.Column('total_beds', sa.Integer(), nullable=True),
        sa.Column('established_year', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('gst_number'),
        sa.UniqueConstraint('license_number')
    )
    op.create_index(op.f('ix_hospitals_is_active'), 'hospitals', ['is_active'])
    op.create_index(op.f('ix_hospitals_name'), 'hospitals', ['name'])

    # users table
    op.create_table('users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('role', sa.Enum('admin', 'doctor', 'nurse', 'patient', 'staff', name='role_enum'), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'])
    op.create_index(op.f('ix_users_hospital_id'), 'users', ['hospital_id'])
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'])
    op.create_index(op.f('ix_users_role'), 'users', ['role'])

    # patients table
    op.create_table('patients',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('patient_id_number', sa.String(50), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(10), nullable=False),
        sa.Column('blood_group', sa.String(10), nullable=True),
        sa.Column('weight', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('allergies', sa.Text(), nullable=True),
        sa.Column('chronic_conditions', sa.Text(), nullable=True),
        sa.Column('insurance_provider', sa.String(100), nullable=True),
        sa.Column('insurance_policy_number', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('patient_id_number', 'hospital_id')
    )
    op.create_index(op.f('ix_patients_hospital_id'), 'patients', ['hospital_id'])
    op.create_index(op.f('ix_patients_user_id'), 'patients', ['user_id'])

    # doctors table
    op.create_table('doctors',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('specialization', sa.String(100), nullable=False),
        sa.Column('license_number', sa.String(50), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('consultation_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('availability_start', sa.Time(), nullable=True),
        sa.Column('availability_end', sa.Time(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('license_number')
    )
    op.create_index(op.f('ix_doctors_hospital_id'), 'doctors', ['hospital_id'])
    op.create_index(op.f('ix_doctors_user_id'), 'doctors', ['user_id'])

    # medical_records table
    op.create_table('medical_records',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=False),
        sa.Column('treatment', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('record_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medical_records_hospital_id'), 'medical_records', ['hospital_id'])
    op.create_index(op.f('ix_medical_records_patient_id'), 'medical_records', ['patient_id'])

    # appointments table
    op.create_table('appointments',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=False),
        sa.Column('doctor_id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('appointment_date', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show', 'rescheduled', name='appointment_status_enum'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_doctor_id'), 'appointments', ['doctor_id'])
    op.create_index(op.f('ix_appointments_hospital_id'), 'appointments', ['hospital_id'])
    op.create_index(op.f('ix_appointments_patient_id'), 'appointments', ['patient_id'])

    # medicines table
    op.create_table('medicines',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medicines_hospital_id'), 'medicines', ['hospital_id'])

    # prescriptions table
    op.create_table('prescriptions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=False),
        sa.Column('doctor_id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('prescription_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('issued', 'dispensed', 'completed', 'cancelled', name='prescription_status_enum'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescriptions_doctor_id'), 'prescriptions', ['doctor_id'])
    op.create_index(op.f('ix_prescriptions_hospital_id'), 'prescriptions', ['hospital_id'])
    op.create_index(op.f('ix_prescriptions_patient_id'), 'prescriptions', ['patient_id'])

    # prescription_items table
    op.create_table('prescription_items',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('prescription_id', sa.String(36), nullable=False),
        sa.Column('medicine_id', sa.String(36), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('dosage', sa.String(100), nullable=False),
        sa.Column('frequency', sa.String(100), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescription_items_medicine_id'), 'prescription_items', ['medicine_id'])
    op.create_index(op.f('ix_prescription_items_prescription_id'), 'prescription_items', ['prescription_id'])

    # medicine_inventory table
    op.create_table('medicine_inventory',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('medicine_id', sa.String(36), nullable=False),
        sa.Column('batch_number', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batch_number', 'hospital_id')
    )
    op.create_index(op.f('ix_medicine_inventory_hospital_id'), 'medicine_inventory', ['hospital_id'])
    op.create_index(op.f('ix_medicine_inventory_medicine_id'), 'medicine_inventory', ['medicine_id'])

    # billing_invoices table
    op.create_table('billing_invoices',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('invoice_date', sa.DateTime(), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('gst_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('paid_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('balance_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', sa.Enum('pending', 'paid', 'partial', 'refunded', 'cancelled', name='billing_status_enum'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number', 'hospital_id')
    )
    op.create_index(op.f('ix_billing_invoices_hospital_id'), 'billing_invoices', ['hospital_id'])
    op.create_index(op.f('ix_billing_invoices_patient_id'), 'billing_invoices', ['patient_id'])

    # billing_payments table
    op.create_table('billing_payments',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('invoice_id', sa.String(36), nullable=False),
        sa.Column('payment_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('transaction_id', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['invoice_id'], ['billing_invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_billing_payments_invoice_id'), 'billing_payments', ['invoice_id'])

    # wards table
    op.create_table('wards',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('ward_type', sa.Enum('general', 'icu', 'pediatrics', 'maternity', 'surgery', name='ward_type_enum'), nullable=False),
        sa.Column('total_beds', sa.Integer(), nullable=False),
        sa.Column('available_beds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wards_hospital_id'), 'wards', ['hospital_id'])

    # beds table
    op.create_table('beds',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('ward_id', sa.String(36), nullable=False),
        sa.Column('bed_number', sa.String(20), nullable=False),
        sa.Column('status', sa.Enum('available', 'occupied', 'maintenance', 'reserved', name='bed_status_enum'), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['ward_id'], ['wards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_beds_patient_id'), 'beds', ['patient_id'])
    op.create_index(op.f('ix_beds_ward_id'), 'beds', ['ward_id'])

    # ai_risk_scores table
    op.create_table('ai_risk_scores',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('risk_type', sa.String(50), nullable=False),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('prediction_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_risk_scores_hospital_id'), 'ai_risk_scores', ['hospital_id'])
    op.create_index(op.f('ix_ai_risk_scores_patient_id'), 'ai_risk_scores', ['patient_id'])

    # ai_logs table
    op.create_table('ai_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('model_version', sa.String(20), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('prediction', sa.JSON(), nullable=True),
        sa.Column('accuracy', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_logs_hospital_id'), 'ai_logs', ['hospital_id'])

    # model_metrics table
    op.create_table('model_metrics',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('model_version', sa.String(20), nullable=True),
        sa.Column('accuracy', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('precision', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('recall', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('f1_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('training_date', sa.DateTime(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_metrics_hospital_id'), 'model_metrics', ['hospital_id'])

    # audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('hospital_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_hospital_id'), 'audit_logs', ['hospital_id'])
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'])


def downgrade() -> None:
    """Drop all tables created in upgrade."""
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('model_metrics')
    op.drop_table('ai_logs')
    op.drop_table('ai_risk_scores')
    op.drop_table('beds')
    op.drop_table('wards')
    op.drop_table('billing_payments')
    op.drop_table('billing_invoices')
    op.drop_table('medicine_inventory')
    op.drop_table('prescription_items')
    op.drop_table('prescriptions')
    op.drop_table('medicines')
    op.drop_table('appointments')
    op.drop_table('medical_records')
    op.drop_table('doctors')
    op.drop_table('patients')
    op.drop_table('users')
    op.drop_table('hospitals')

    # Drop enums
    op.execute('DROP TYPE bed_status_enum')
    op.execute('DROP TYPE ward_type_enum')
    op.execute('DROP TYPE prescription_status_enum')
    op.execute('DROP TYPE billing_status_enum')
    op.execute('DROP TYPE appointment_status_enum')
    op.execute('DROP TYPE role_enum')
