"""Add database indexes for performance optimization

Revision ID: 002_add_database_indexes
Revises: 001_initial_schema
Create Date: 2026-03-04 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_database_indexes'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create indexes for improved query performance."""
    
    # Users table indexes
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_phone', 'users', ['phone_number'])
    op.create_index('idx_users_role_active', 'users', ['role', 'is_active'])
    
    # Patients table indexes
    op.create_index('idx_patients_user_id', 'patients', ['user_id'])
    op.create_index('idx_patients_nhs_number', 'patients', ['nhs_number'], unique=True)
    op.create_index('idx_patients_hospital_id', 'patients', ['hospital_id'])
    
    # Doctors table indexes
    op.create_index('idx_doctors_user_id', 'doctors', ['user_id'])
    op.create_index('idx_doctors_specialization', 'doctors', ['specialization'])
    op.create_index('idx_doctors_hospital_id', 'doctors', ['hospital_id'])
    
    # Appointments table indexes
    op.create_index('idx_appointments_patient_id', 'appointments', ['patient_id'])
    op.create_index('idx_appointments_doctor_id', 'appointments', ['doctor_id'])
    op.create_index('idx_appointments_scheduled_date', 'appointments', ['scheduled_date'])
    op.create_index('idx_appointments_status', 'appointments', ['status'])
    op.create_index('idx_appointments_hospital_id', 'appointments', ['hospital_id'])
    
    # Prescriptions table indexes
    op.create_index('idx_prescriptions_patient_id', 'prescriptions', ['patient_id'])
    op.create_index('idx_prescriptions_doctor_id', 'prescriptions', ['doctor_id'])
    op.create_index('idx_prescriptions_status', 'prescriptions', ['status'])
    op.create_index('idx_prescriptions_hospital_id', 'prescriptions', ['hospital_id'])
    
    # Billing table indexes
    op.create_index('idx_billing_patient_id', 'billing', ['patient_id'])
    op.create_index('idx_billing_appointment_id', 'billing', ['appointment_id'])
    op.create_index('idx_billing_status', 'billing', ['status'])
    
    # Wards table indexes
    op.create_index('idx_wards_hospital_id', 'wards', ['hospital_id'])
    op.create_index('idx_wards_ward_type', 'wards', ['ward_type'])
    
    # Inventory table indexes
    op.create_index('idx_inventory_hospital_id', 'inventory', ['hospital_id'])
    op.create_index('idx_inventory_medication_name', 'inventory', ['medication_name'])


def downgrade() -> None:
    """Remove all created indexes."""
    
    # Remove all indexes
    op.drop_index('idx_inventory_medication_name', table_name='inventory')
    op.drop_index('idx_inventory_hospital_id', table_name='inventory')
    
    op.drop_index('idx_wards_ward_type', table_name='wards')
    op.drop_index('idx_wards_hospital_id', table_name='wards')
    
    op.drop_index('idx_billing_status', table_name='billing')
    op.drop_index('idx_billing_appointment_id', table_name='billing')
    op.drop_index('idx_billing_patient_id', table_name='billing')
    
    op.drop_index('idx_prescriptions_hospital_id', table_name='prescriptions')
    op.drop_index('idx_prescriptions_status', table_name='prescriptions')
    op.drop_index('idx_prescriptions_doctor_id', table_name='prescriptions')
    op.drop_index('idx_prescriptions_patient_id', table_name='prescriptions')
    
    op.drop_index('idx_appointments_hospital_id', table_name='appointments')
    op.drop_index('idx_appointments_status', table_name='appointments')
    op.drop_index('idx_appointments_scheduled_date', table_name='appointments')
    op.drop_index('idx_appointments_doctor_id', table_name='appointments')
    op.drop_index('idx_appointments_patient_id', table_name='appointments')
    
    op.drop_index('idx_doctors_hospital_id', table_name='doctors')
    op.drop_index('idx_doctors_specialization', table_name='doctors')
    op.drop_index('idx_doctors_user_id', table_name='doctors')
    
    op.drop_index('idx_patients_hospital_id', table_name='patients')
    op.drop_index('idx_patients_nhs_number', table_name='patients')
    op.drop_index('idx_patients_user_id', table_name='patients')
    
    op.drop_index('idx_users_role_active', table_name='users')
    op.drop_index('idx_users_phone', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
