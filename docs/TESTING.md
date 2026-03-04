# DataCure Testing Guide

## Table of Contents
1. [Testing Structure](#testing-structure)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [API Testing](#api-testing)
5. [Load Testing](#load-testing)
6. [Running Tests](#running-tests)

---

## Testing Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures, setup, teardown
├── constants.py             # Test data constants
├── unit/
│   ├── __init__.py
│   ├── test_auth.py        # Authentication service tests
│   ├── test_patient.py     # Patient service tests
│   ├── test_appointment.py # Appointment service tests
│   ├── test_billing.py     # Billing service tests
│   ├── test_inventory.py   # Inventory service tests
│   └── test_ai.py          # AI service tests
├── integration/
│   ├── __init__.py
│   ├── test_auth_routes.py     # Auth endpoint tests
│   ├── test_patient_routes.py  # Patient endpoint tests
│   ├── test_appointment_routes.py
│   ├── test_billing_routes.py
│   └── test_ai_routes.py
├── api/
│   ├── __init__.py
│   └── test_api_contract.py # API contract validation
└── load/
    └── locustfile.py        # Load testing script
```

---

## Unit Testing

### Test Authentication Service
File: `tests/unit/test_auth.py`

```python
import pytest
from app.services.auth import AuthenticationService, UserManagementService
from app.models import User
from app.utils.errors import ValidationError, UnauthorizedError

class TestAuthenticationService:
    
    @pytest.fixture
    def auth_service(self, db):
        return AuthenticationService(db)
    
    def test_register_success(self, auth_service, hospital_id):
        """Test successful user registration."""
        data = {
            'email': 'newuser@hospital.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'doctor',
            'hospital_id': hospital_id
        }
        
        success, user_id = auth_service.register(**data)
        
        assert success is True
        assert user_id is not None
        assert User.query.filter_by(email='newuser@hospital.com').first() is not None
    
    def test_register_duplicate_email(self, auth_service, hospital_id, user_email):
        """Test registration fails for existing email."""
        data = {
            'email': user_email,  # Already exists
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'doctor',
            'hospital_id': hospital_id
        }
        
        with pytest.raises(ValidationError):
            auth_service.register(**data)
    
    def test_register_weak_password(self, auth_service, hospital_id):
        """Test registration fails with weak password."""
        data = {
            'email': 'weak@hospital.com',
            'password': '123',  # Too weak
            'confirm_password': '123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'doctor',
            'hospital_id': hospital_id
        }
        
        with pytest.raises(ValidationError):
            auth_service.register(**data)
    
    def test_login_success(self, auth_service, user_email, user_password):
        """Test successful login."""
        success, tokens = auth_service.login(user_email, user_password)
        
        assert success is True
        assert 'access_token' in tokens
        assert 'refresh_token' in tokens
        assert tokens['token_type'] == 'Bearer'
    
    def test_login_invalid_credentials(self, auth_service, user_email):
        """Test login fails with wrong password."""
        with pytest.raises(UnauthorizedError):
            auth_service.login(user_email, 'wrongpassword')
    
    def test_login_nonexistent_user(self, auth_service):
        """Test login fails for nonexistent user."""
        with pytest.raises(UnauthorizedError):
            auth_service.login('nonexistent@hospital.com', 'password123')
    
    def test_change_password_success(self, auth_service, user_id, user_password):
        """Test successful password change."""
        new_password = 'NewPassword123!'
        success = auth_service.change_password(user_id, user_password, new_password)
        
        assert success is True
        
        # Verify new password works
        user = User.query.get(user_id)
        assert user.verify_password(new_password) is True
    
    def test_change_password_wrong_old_password(self, auth_service, user_id):
        """Test password change fails with wrong old password."""
        with pytest.raises(UnauthorizedError):
            auth_service.change_password(user_id, 'wrongpassword', 'NewPassword123!')
```

### Test Patient Service
File: `tests/unit/test_patient.py`

```python
class TestPatientService:
    
    @pytest.fixture
    def patient_service(self, db):
        return PatientService(db)
    
    def test_create_patient_success(self, patient_service, user_id, hospital_id):
        """Test successful patient creation."""
        data = {
            'user_id': user_id,
            'date_of_birth': '1990-05-15',
            'gender': 'M',
            'blood_group': 'O+',
            'weight': 75.5,
            'height': 180,
            'allergies': 'Penicillin',
            'chronic_conditions': 'Diabetes'
        }
        
        success, patient_id = patient_service.create_patient(hospital_id, **data)
        
        assert success is True
        assert patient_id is not None
    
    def test_get_patient_statistics(self, patient_service, patient_id):
        """Test patient statistics generation."""
        stats = patient_service.get_patient_statistics(patient_id)
        
        assert 'total_appointments' in stats
        assert 'total_prescriptions' in stats
        assert 'total_billing_amount' in stats
        assert 'last_appointment_date' in stats
    
    def test_add_medical_record(self, patient_service, patient_id, file_path):
        """Test medical record addition."""
        success, record_id = patient_service.add_medical_record(
            patient_id=patient_id,
            record_type='laboratory',
            file_path=file_path,
            description='Blood test results'
        )
        
        assert success is True
        assert record_id is not None
```

### Running Unit Tests
```bash
# All unit tests
pytest tests/unit/ -v

# Specific test file
pytest tests/unit/test_auth.py -v

# Specific test
pytest tests/unit/test_auth.py::TestAuthenticationService::test_register_success -v

# With coverage
pytest tests/unit/ --cov=app --cov-report=html

# Show print statements
pytest tests/unit/ -v -s
```

---

## Integration Testing

### Test Auth Routes
File: `tests/integration/test_auth_routes.py`

```python
import pytest
from app import db
from app.models import User

class TestAuthRoutes:
    
    def test_register_endpoint(self, client, hospital_id):
        """Test /auth/register endpoint."""
        payload = {
            'email': 'newdoctor@hospital.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Dr. John',
            'last_name': 'Smith',
            'role': 'doctor',
            'hospital_id': hospital_id
        }
        
        response = client.post('/api/v1/auth/register', json=payload)
        
        assert response.status_code == 201
        assert response.json['success'] is True
        assert response.json['data']['email'] == 'newdoctor@hospital.com'
    
    def test_login_endpoint(self, client, user_email, user_password):
        """Test /auth/login endpoint."""
        payload = {
            'email': user_email,
            'password': user_password
        }
        
        response = client.post('/api/v1/auth/login', json=payload)
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'access_token' in response.json['data']
        assert 'refresh_token' in response.json['data']
    
    def test_refresh_token_endpoint(self, client, refresh_token):
        """Test /auth/refresh endpoint."""
        payload = {'refresh_token': refresh_token}
        
        response = client.post('/api/v1/auth/refresh', json=payload)
        
        assert response.status_code == 200
        assert 'access_token' in response.json['data']
    
    def test_change_password_endpoint(self, client, access_token, user_password):
        """Test /auth/change-password endpoint."""
        headers = {'Authorization': f'Bearer {access_token}'}
        payload = {
            'old_password': user_password,
            'new_password': 'NewPassword123!'
        }
        
        response = client.post(
            '/api/v1/auth/change-password',
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json['success'] is True
```

### Test Patient Routes
File: `tests/integration/test_patient_routes.py`

```python
class TestPatientRoutes:
    
    def test_create_patient_endpoint(self, client, access_token, hospital_id):
        """Test POST /patients endpoint."""
        headers = {'Authorization': f'Bearer {access_token}'}
        payload = {
            'user_id': 'user-uuid',
            'date_of_birth': '1985-05-10',
            'gender': 'F',
            'blood_group': 'A+',
            'weight': 65.0,
            'height': 165,
            'allergies': 'Nuts',
            'chronic_conditions': 'Asthma'
        }
        
        response = client.post(
            '/api/v1/patients',
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 201
        assert response.json['success'] is True
    
    def test_get_patients_list(self, client, access_token):
        """Test GET /patients endpoint."""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get(
            '/api/v1/patients?page=1&per_page=20',
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'data' in response.json
        assert 'meta' in response.json
    
    def test_get_patient_detail(self, client, access_token, patient_id):
        """Test GET /patients/{id} endpoint."""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get(
            f'/api/v1/patients/{patient_id}',
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json['data']['id'] == patient_id
```

### Running Integration Tests
```bash
# All integration tests
pytest tests/integration/ -v

# With database setup/teardown
pytest tests/integration/ -v --tb=short

# Integration + unit tests
pytest tests/ -v -k "not load"
```

---

## API Testing

### API Contract Tests
File: `tests/api/test_api_contract.py`

```python
class TestAPIContract:
    """Validate API response structures."""
    
    def test_success_response_structure(self, client, access_token):
        """Test standard success response format."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = client.get('/api/v1/patients', headers=headers)
        
        assert 'success' in response.json
        assert 'data' in response.json
        assert 'message' in response.json
    
    def test_error_response_structure(self, client):
        """Test standard error response format."""
        response = client.post('/api/v1/auth/login', json={})
        
        assert 'success' in response.json
        assert response.json['success'] is False
        assert 'message' in response.json
        assert 'error_code' in response.json
    
    def test_pagination_response_structure(self, client, access_token):
        """Test paginated response format."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = client.get('/api/v1/patients?page=1', headers=headers)
        
        assert 'meta' in response.json
        meta = response.json['meta']
        assert 'total' in meta
        assert 'page' in meta
        assert 'per_page' in meta
        assert 'pages' in meta
        assert 'has_next' in meta
        assert 'has_prev' in meta
```

---

## Load Testing

### Locust Load Testing
File: `tests/load/locustfile.py`

```python
from locust import HttpUser, task, between
import random

class DataCureUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        """Login before starting tasks."""
        response = self.client.post('/api/v1/auth/login', json={
            'email': 'testuser@hospital.com',
            'password': 'TestPass123!'
        })
        if response.status_code == 200:
            self.token = response.json()['data']['access_token']
            self.headers = {'Authorization': f'Bearer {self.token}'}
    
    @task(2)
    def get_patients(self):
        """Simulate getting patient list."""
        self.client.get('/api/v1/patients?page=1', headers=self.headers)
    
    @task(1)
    def get_appointments(self):
        """Simulate getting appointments."""
        self.client.get('/api/v1/appointments', headers=self.headers)
    
    @task(1)
    def predict_readmission(self):
        """Simulate readmission prediction."""
        self.client.post('/api/v1/ai/predict/readmission', json={
            'patient_id': 'patient-uuid'
        }, headers=self.headers)

class AdminUser(HttpUser):
    wait_time = between(2, 8)
    
    def on_start(self):
        """Login as admin."""
        response = self.client.post('/api/v1/auth/login', json={
            'email': 'admin@hospital.com',
            'password': 'AdminPass123!'
        })
        self.token = response.json()['data']['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    @task(3)
    def get_model_metrics(self):
        """Simulate checking AI metrics."""
        self.client.get('/api/v1/ai/model-metrics', headers=self.headers)
```

### Running Load Tests
```bash
# Start Locust GUI
locust -f tests/load/locustfile.py --host=http://localhost:5000

# Run headless (50 users, spawn rate 10/sec, 5 minute duration)
locust -f tests/load/locustfile.py \
    --headless \
    --users 50 \
    --spawn-rate 10 \
    --run-time 5m \
    --host=http://localhost:5000 \
    --csv=results

# With specific user class
locust -f tests/load/locustfile.py \
    --headless \
    -u 100 \
    -r 20 \
    DataCureUser \
    --host=http://localhost:5000
```

---

## Running Tests

### Pytest Configuration
File: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    api: API contract tests
    load: Load tests
    slow: Slow tests
```

### Test Fixtures
File: `tests/conftest.py`

```python
import pytest
from app import create_app, db
from app.models import User, Hospital, Patient

@pytest.fixture(scope='function')
def app():
    """Create app with test config."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()

@pytest.fixture
def hospital_id(app):
    """Create test hospital."""
    hospital = Hospital(
        name='Test Hospital',
        address='123 Test St',
        city='Test City',
        state='Test State',
        country='India'
    )
    db.session.add(hospital)
    db.session.commit()
    return hospital.id

@pytest.fixture
def user_email():
    return 'testuser@hospital.com'

@pytest.fixture
def user_password():
    return 'TestPass123!'

@pytest.fixture
def access_token(client, user_email, user_password):
    """Get valid JWT token."""
    response = client.post('/api/v1/auth/login', json={
        'email': user_email,
        'password': user_password
    })
    return response.json['data']['access_token']
```

### Run All Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html --cov-report=term

# Run by marker
pytest tests/ -m unit
pytest tests/ -m integration

# Run with debug output
pytest tests/ -vv -s

# Run single test
pytest tests/unit/test_auth.py::TestAuthenticationService::test_register_success -v
```

### Test Coverage Goals
```
Target Coverage: 80%+

app/models/          90%
app/services/        85%
app/utils/           90%
app/repositories/    85%
app/routes/          75%
app/schemas/         80%
```

Generate coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

## CI/CD Integration

### GitHub Actions Workflow
File: `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: datacure_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test123
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test123@localhost:5432/datacure_test
        run: |
          pytest tests/ -v --cov=app --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

**Last Updated**: February 2025
**Version**: 1.0
