#!/usr/bin/env python
"""
Database initialization script for DataCure.
Creates database tables and seeds with comprehensive test data.
"""
import sys
import os
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app, db
from app.models import (
    Hospital, User, RoleEnum, Patient, Doctor, Appointment,
    AppointmentStatusEnum, Prescription, PrescriptionStatusEnum,
    PrescriptionItem, Ward, WardTypeEnum, BedStatusEnum,
    Billing, BillingStatusEnum, MedicineInventory
)
from app.utils.auth import PasswordHandler

def create_database_indexes(app):
    """Create all database indexes for performance optimization."""
    from sqlalchemy import Index, text, inspect
    
    with app.app_context():
        try:
            # Get database dialect to handle SQLite vs PostgreSQL
            engine = db.engine
            inspector = inspect(engine)
            
            # Define all indexes to create
            indexes_config = {
                'users': [
                    ('idx_users_email', ['email']),
                    ('idx_users_phone', ['phone_number']),
                    ('idx_users_role_active', ['role', 'is_active']),
                ],
                'patients': [
                    ('idx_patients_user_id', ['user_id']),
                    ('idx_patients_nhs_number', ['nhs_number']),
                    ('idx_patients_hospital_id', ['hospital_id']),
                ],
                'doctors': [
                    ('idx_doctors_user_id', ['user_id']),
                    ('idx_doctors_specialization', ['specialization']),
                    ('idx_doctors_hospital_id', ['hospital_id']),
                ],
                'appointments': [
                    ('idx_appointments_patient_id', ['patient_id']),
                    ('idx_appointments_doctor_id', ['doctor_id']),
                    ('idx_appointments_scheduled_date', ['scheduled_date']),
                    ('idx_appointments_status', ['status']),
                    ('idx_appointments_hospital_id', ['hospital_id']),
                ],
                'prescriptions': [
                    ('idx_prescriptions_patient_id', ['patient_id']),
                    ('idx_prescriptions_doctor_id', ['doctor_id']),
                    ('idx_prescriptions_status', ['status']),
                    ('idx_prescriptions_hospital_id', ['hospital_id']),
                ],
                'billing': [
                    ('idx_billing_patient_id', ['patient_id']),
                    ('idx_billing_appointment_id', ['appointment_id']),
                    ('idx_billing_status', ['status']),
                ],
                'wards': [
                    ('idx_wards_hospital_id', ['hospital_id']),
                    ('idx_wards_ward_type', ['ward_type']),
                ],
                'medicine_inventory': [
                    ('idx_inventory_hospital_id', ['hospital_id']),
                    ('idx_inventory_medication_name', ['medication_name']),
                ],
            }
            
            indexes_created = 0
            
            # Create indexes for each table
            for table_name, indexes in indexes_config.items():
                # Check if table exists
                if table_name not in inspector.get_table_names():
                    continue
                    
                existing_indexes = {idx['name'] for idx in inspector.get_indexes(table_name)}
                
                for index_name, columns in indexes:
                    # Skip if index already exists
                    if index_name in existing_indexes:
                        continue
                    
                    try:
                        # Create index using proper SQL dialect
                        if engine.dialect.name == 'postgresql':
                            sql = f"CREATE INDEX {index_name} ON {table_name} ({', '.join(columns)});"
                        else:  # SQLite
                            sql = f"CREATE INDEX {index_name} ON {table_name} ({', '.join(columns)});"
                        
                        db.session.execute(text(sql))
                        indexes_created += 1
                    except Exception as e:
                        # Index might already exist or column might not exist
                        pass
            
            db.session.commit()
            if indexes_created > 0:
                print(f"✓ Created {indexes_created} database indexes")
            else:
                print("✓ All database indexes already exist")
                
        except Exception as e:
            print(f"⚠ Note: Index creation skipped ({str(e)})")
            # Don't fail initialization if indexes can't be created

def init_database():
    """Initialize database with tables and comprehensive test data."""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Check if hospital already exists
        hospital = Hospital.query.first()
        if not hospital:
            print("\nSeeding database with test data...")
            
            # Create default hospital
            hospital = Hospital(
                name='DataCure Demo Hospital',
                email='hospital@datacure.com',
                phone='+91-9876543210',
                address='123 Medical Avenue, Tech Park',
                city='Bangalore',
                state='Karnataka',
                postal_code='560001',
                country='India',
                registration_number='REG123456',
                gst_number='27AAPCT1234G1Z0',
                subscription_tier='premium'
            )
            db.session.add(hospital)
            db.session.flush()
            hospital_id = hospital.id
            print(f"✓ Hospital created: {hospital.name}")
            
            # Create test admin user
            admin_password = PasswordHandler.hash_password('Admin@123')
            admin_user = User(
                email='admin@hospital.com',
                password_hash=admin_password,
                first_name='Admin',
                last_name='User',
                phone='+91-1111111111',
                role=RoleEnum.ADMIN,
                hospital_id=hospital_id,
                is_active=True
            )
            db.session.add(admin_user)
            
            # Create test doctor user
            doctor_password = PasswordHandler.hash_password('Doctor@123')
            doctor_user = User(
                email='doctor@hospital.com',
                password_hash=doctor_password,
                first_name='Dr.',
                last_name='Smith',
                phone='+91-2222222222',
                role=RoleEnum.DOCTOR,
                hospital_id=hospital_id,
                is_active=True
            )
            db.session.add(doctor_user)
            
            # Create test patient user
            patient_password = PasswordHandler.hash_password('Patient@123')
            patient_user = User(
                email='patient@hospital.com',
                password_hash=patient_password,
                first_name='John',
                last_name='Doe',
                phone='+91-3333333333',
                role=RoleEnum.PATIENT,
                hospital_id=hospital_id,
                is_active=True
            )
            db.session.add(patient_user)
            
            # Create additional users for testing
            nurse_password = PasswordHandler.hash_password('Nurse@123')
            nurse_user = User(
                email='nurse@hospital.com',
                password_hash=nurse_password,
                first_name='Nurse',
                last_name='Johnson',
                phone='+91-4444444444',
                role=RoleEnum.NURSE,
                hospital_id=hospital_id,
                is_active=True
            )
            db.session.add(nurse_user)
            
            staff_password = PasswordHandler.hash_password('Staff@123')
            staff_user = User(
                email='staff@hospital.com',
                password_hash=staff_password,
                first_name='Staff',
                last_name='Member',
                phone='+91-5555555555',
                role=RoleEnum.STAFF,
                hospital_id=hospital_id,
                is_active=True
            )
            db.session.add(staff_user)
            
            db.session.commit()
            print("✓ Test users created:")
            print("  - Admin: admin@hospital.com / Admin@123")
            print("  - Doctor: doctor@hospital.com / Doctor@123")
            print("  - Patient: patient@hospital.com / Patient@123")
            print("  - Nurse: nurse@hospital.com / Nurse@123")
            print("  - Staff: staff@hospital.com / Staff@123")
            
            # Create doctor profile
            doctor = Doctor(
                user_id=doctor_user.id,
                hospital_id=hospital_id,
                license_number='MED123456',
                specialization='General Medicine',
                qualification='MBBS, MD',
                experience_years=8,
                consultation_fee=500.0,
                availability_status='available'
            )
            db.session.add(doctor)
            db.session.flush()
            doctor_id = doctor.id
            print(f"✓ Doctor profile created for {doctor_user.first_name} {doctor_user.last_name}")
            
            # Create patient profile
            patient = Patient(
                user_id=patient_user.id,
                hospital_id=hospital_id,
                patient_id_number='PAT001',
                date_of_birth=date(1990, 5, 15),
                gender='Male',
                blood_group='O+',
                weight=75.0,
                height=175.0,
                allergies='Penicillin',
                chronic_conditions='Hypertension',
                emergency_contact_name='Jane Doe',
                emergency_contact_phone='+91-9999999999',
                insurance_provider='Apollo Health Insurance',
                insurance_policy_number='AHI123456',
                insurance_expiry=date(2025, 12, 31)
            )
            db.session.add(patient)
            db.session.flush()
            patient_id = patient.id
            print(f"✓ Patient profile created for {patient_user.first_name} {patient_user.last_name}")
            
            # Create sample wards
            ward_general = Ward(
                hospital_id=hospital_id,
                name='General Ward',
                ward_type=WardTypeEnum.GENERAL,
                floor='1',
                total_beds=20,
                available_beds=15,
                head_nurse='Sarah Williams'
            )
            db.session.add(ward_general)
            
            ward_icu = Ward(
                hospital_id=hospital_id,
                name='ICU Ward',
                ward_type=WardTypeEnum.ICU,
                floor='2',
                total_beds=10,
                available_beds=7,
                head_nurse='Michael Brown'
            )
            db.session.add(ward_icu)
            print("✓ Wards created: General Ward, ICU Ward")
            db.session.commit()
            
            # Create sample medicines
            medicine1 = MedicineInventory(
                hospital_id=hospital_id,
                medicine_name='Paracetamol',
                generic_name='Acetaminophen',
                dosage='500mg',
                quantity_in_stock=500,
                reorder_level=100,
                unit_price=10.0,
                manufacturer='ABC Pharma',
                batch_number='BATCH001',
                expiry_date=date(2025, 12, 31),
                storage_location='Cabinet A1'
            )
            db.session.add(medicine1)
            
            medicine2 = MedicineInventory(
                hospital_id=hospital_id,
                medicine_name='Amoxicillin',
                generic_name='Amoxicillin Trihydrate',
                dosage='250mg',
                quantity_in_stock=300,
                reorder_level=50,
                unit_price=15.0,
                manufacturer='XYZ Pharma',
                batch_number='BATCH002',
                expiry_date=date(2025, 11, 30),
                storage_location='Cabinet B2'
            )
            db.session.add(medicine2)
            print("✓ Medicines added to inventory")
            db.session.commit()
            
            # Create sample appointments
            today = date.today()
            appointment1 = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                hospital_id=hospital_id,
                appointment_date=today + timedelta(days=2),
                start_time=datetime.strptime('10:00', '%H:%M').time(),
                end_time=datetime.strptime('10:30', '%H:%M').time(),
                status=AppointmentStatusEnum.SCHEDULED,
                appointment_type='consultation',
                chief_complaint='Regular check-up',
                consultation_room='Room 201'
            )
            db.session.add(appointment1)
            
            appointment2 = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                hospital_id=hospital_id,
                appointment_date=today + timedelta(days=5),
                start_time=datetime.strptime('14:00', '%H:%M').time(),
                end_time=datetime.strptime('14:30', '%H:%M').time(),
                status=AppointmentStatusEnum.SCHEDULED,
                appointment_type='follow-up',
                chief_complaint='Follow-up for hypertension',
                consultation_room='Room 202'
            )
            db.session.add(appointment2)
            print("✓ Sample appointments created")
            db.session.commit()
            
            # Create sample prescription
            prescription = Prescription(
                appointment_id=appointment1.id,
                patient_id=patient_id,
                doctor_id=doctor_id,
                hospital_id=hospital_id,
                prescription_number='RX001',
                status=PrescriptionStatusEnum.ISSUED,
                notes='Take after food. Continue for 7 days.',
                expiry_date=today + timedelta(days=30)
            )
            db.session.add(prescription)
            db.session.flush()
            
            # Add prescription items
            item1 = PrescriptionItem(
                prescription_id=prescription.id,
                medicine_id=medicine1.id,
                dosage='500mg',
                frequency='Twice a day',
                duration='7 days',
                quantity=14
            )
            db.session.add(item1)
            
            item2 = PrescriptionItem(
                prescription_id=prescription.id,
                medicine_id=medicine2.id,
                dosage='250mg',
                frequency='Once a day',
                duration='7 days',
                quantity=7
            )
            db.session.add(item2)
            print("✓ Sample prescription created with items")
            db.session.commit()
            
            # Create sample billing records
            billing1 = Billing(
                patient_id=patient_id,
                hospital_id=hospital_id,
                invoice_number='INV001',
                invoice_date=today,
                amount_due=2500.0,
                amount_paid=2500.0,
                status=BillingStatusEnum.PAID,
                payment_date=today,
                description='Consultation and Medicine'
            )
            db.session.add(billing1)
            
            billing2 = Billing(
                patient_id=patient_id,
                hospital_id=hospital_id,
                invoice_number='INV002',
                invoice_date=today,
                amount_due=5000.0,
                amount_paid=2500.0,
                status=BillingStatusEnum.PARTIAL,
                description='Lab Tests and Consultation'
            )
            db.session.add(billing2)
            print("✓ Sample billing records created")
            
            db.session.commit()
            print("\n✓ Comprehensive test data created successfully!")
            
            # Create database indexes for performance optimization
            print("\nCreating database indexes for performance...")
            create_database_indexes(app)
        else:
            print(f"\n✓ Database already has data: {hospital.name}")
            print("Skipping test data creation to avoid duplicates.")
            # Still create indexes if they don't exist
            print("Ensuring all database indexes exist...")
            create_database_indexes(app)
        
        print("\n✓ Database initialization complete!")
        return True

if __name__ == '__main__':
    try:
        init_database()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
