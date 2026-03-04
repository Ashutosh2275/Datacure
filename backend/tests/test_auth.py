"""
Unit tests for DataCure authentication endpoints.
"""
import unittest
import json
from app import create_app, db
from app.models import Hospital, User, RoleEnum
from app.utils.auth import PasswordHandler
from datetime import datetime


class AuthTestCase(unittest.TestCase):
    """Test cases for authentication endpoints."""
    
    def setUp(self):
        """Set up test client and database."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test hospital
            hospital = Hospital(
                name='Test Hospital',
                email='test@hospital.com',
                phone='+91-1234567890',
                address='Test Address',
                city='Test City',
                state='Test State',
                postal_code='123456',
                country='India',
                registration_number='REG123',
                gst_number='GST123'
            )
            db.session.add(hospital)
            db.session.commit()
            
            self.hospital_id = hospital.id
            
            # Create test user
            password_hash = PasswordHandler.hash_password('TestPass123!')
            user = User(
                email='user@hospital.com',
                password_hash=password_hash,
                first_name='Test',
                last_name='User',
                phone='+91-9876543210',
                role=RoleEnum.DOCTOR,
                hospital_id=self.hospital_id
            )
            db.session.add(user)
            db.session.commit()
            
            self.user_id = user.id
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_login_success(self):
        """Test successful login."""
        with self.app.app_context():
            response = self.client.post(
                '/api/v1/auth/login',
                data=json.dumps({
                    'email': 'user@hospital.com',
                    'password': 'TestPass123!'
                }),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('access_token', data['data'])
            self.assertIn('refresh_token', data['data'])
    
    def test_login_invalid_password(self):
        """Test login with invalid password."""
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'user@hospital.com',
                'password': 'WrongPassword123!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_login_invalid_email(self):
        """Test login with non-existent email."""
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'nonexistent@hospital.com',
                'password': 'TestPass123!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_register_success(self):
        """Test successful registration."""
        with self.app.app_context():
            response = self.client.post(
                '/api/v1/auth/register',
                data=json.dumps({
                    'email': 'newuser@hospital.com',
                    'password': 'NewPass123!',
                    'confirm_password': 'NewPass123!',
                    'first_name': 'New',
                    'last_name': 'User',
                    'phone': '+91-8765432109',
                    'role': 'patient',
                    'hospital_id': self.hospital_id
                }),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('user_id', data['data'])
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        with self.app.app_context():
            response = self.client.post(
                '/api/v1/auth/register',
                data=json.dumps({
                    'email': 'user@hospital.com',
                    'password': 'NewPass123!',
                    'confirm_password': 'NewPass123!',
                    'first_name': 'Another',
                    'last_name': 'User',
                    'phone': '+91-8765432109',
                    'role': 'patient',
                    'hospital_id': self.hospital_id
                }),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
    
    def test_password_mismatch(self):
        """Test password mismatch during registration."""
        with self.app.app_context():
            response = self.client.post(
                '/api/v1/auth/register',
                data=json.dumps({
                    'email': 'mismatch@hospital.com',
                    'password': 'Pass123!',
                    'confirm_password': 'DifferentPass123!',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'phone': '+91-8765432109',
                    'role': 'patient',
                    'hospital_id': self.hospital_id
                }),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 422)
            data = json.loads(response.data)
            self.assertFalse(data['success'])


class PatientModelTestCase(unittest.TestCase):
    """Test cases for Patient model."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_patient_creation(self):
        """Test patient record creation."""
        from app.models import Patient
        from datetime import date
        
        with self.app.app_context():
            # Create hospital and user first
            hospital = Hospital(
                name='Test Hospital',
                email='test@hospital.com',
                phone='+91-1234567890',
                address='Test Address',
                city='Test City',
                state='Test State',
                postal_code='123456',
                country='India',
                registration_number='REG123',
                gst_number='GST123'
            )
            db.session.add(hospital)
            db.session.commit()
            
            password_hash = PasswordHandler.hash_password('TestPass123!')
            user = User(
                email='patient@hospital.com',
                password_hash=password_hash,
                first_name='Patient',
                last_name='User',
                phone='+91-9876543210',
                role=RoleEnum.PATIENT,
                hospital_id=hospital.id
            )
            db.session.add(user)
            db.session.commit()
            
            # Create patient
            patient = Patient(
                user_id=user.id,
                hospital_id=hospital.id,
                patient_id_number='PAT001',
                date_of_birth=date(1990, 5, 15),
                gender='Male',
                blood_group='O+',
                weight=75.0,
                height=180.0
            )
            db.session.add(patient)
            db.session.commit()
            
            # Verify patient was created
            retrieved_patient = Patient.query.filter_by(patient_id_number='PAT001').first()
            self.assertIsNotNone(retrieved_patient)
            self.assertEqual(retrieved_patient.blood_group, 'O+')
            self.assertEqual(retrieved_patient.weight, 75.0)


if __name__ == '__main__':
    unittest.main()
