#!/usr/bin/env python
"""
Database initialization script for DataCure.
Creates database tables and seeds with test data.
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app, db
from app.models import Hospital, User, RoleEnum
from app.utils.auth import PasswordHandler

def init_database():
    """Initialize database with tables and test data."""
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
                name='Demo Hospital',
                email='hospital@example.com',
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
            db.session.commit()
            print(f"✓ Hospital created: {hospital.name}")
            
            # Create test admin user
            admin_password = PasswordHandler.hash_password('Admin@123')
            admin = User(
                email='admin@hospital.com',
                password_hash=admin_password,
                first_name='Admin',
                last_name='User',
                role=RoleEnum.ADMIN,
                hospital_id=hospital.id
            )
            db.session.add(admin)
            
            # Create test doctor user
            doctor_password = PasswordHandler.hash_password('Doctor@123')
            doctor = User(
                email='doctor@hospital.com',
                password_hash=doctor_password,
                first_name='Dr.',
                last_name='Smith',
                role=RoleEnum.DOCTOR,
                hospital_id=hospital.id
            )
            db.session.add(doctor)
            
            # Create test patient user
            patient_password = PasswordHandler.hash_password('Patient@123')
            patient = User(
                email='patient@hospital.com',
                password_hash=patient_password,
                first_name='John',
                last_name='Doe',
                role=RoleEnum.PATIENT,
                hospital_id=hospital.id
            )
            db.session.add(patient)
            
            db.session.commit()
            print("✓ Test users created:")
            print("  - Admin: admin@hospital.com / Admin@123")
            print("  - Doctor: doctor@hospital.com / Doctor@123")
            print("  - Patient: patient@hospital.com / Patient@123")
        else:
            print(f"\n✓ Database already has data: {hospital.name}")
        
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
