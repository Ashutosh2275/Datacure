# DataCure Developer Guide

Complete guide for developing features, understanding architecture, and contributing to DataCure.

## Table of Contents
1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Database Models](#database-models)
4. [API Architecture](#api-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Authentication & Authorization](#authentication--authorization)
7. [Testing](#testing)
8. [Coding Standards](#coding-standards)
9. [Common Tasks](#common-tasks)
10. [Debugging](#debugging)

---

## Development Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Git

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd DataCure

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r ai-requirements.txt  # For AI features

# Setup database
python init_db.py
alembic upgrade head

# Install frontend dependencies
cd ../frontend
npm install

# Copy environment file
cp ../.env.example ../.env
```

### Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source ../.venv/bin/activate
python run.py
```

Backend runs on `http://localhost:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:3000`

### Test Credentials
```
Admin:   admin@hospital.com / Admin@123
Doctor:  doctor@hospital.com / Doctor@123
Patient: patient@hospital.com / Patient@123
Nurse:   nurse@hospital.com / Nurse@123
Staff:   staff@hospital.com / Staff@123
```

---

## Project Structure

```
DataCure/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory
│   │   ├── config.py            # Configuration
│   │   ├── extensions.py        # Flask extensions
│   │   ├── models/              # Database models
│   │   │   └── __init__.py      # All SQLAlchemy models
│   │   ├── routes/              # API blueprints
│   │   │   ├── auth.py
│   │   │   ├── patients.py
│   │   │   ├── doctors.py
│   │   │   ├── appointments.py
│   │   │   ├── prescriptions.py
│   │   │   ├── billing.py
│   │   │   ├── inventory.py
│   │   │   ├── wards.py
│   │   │   ├── users.py
│   │   │   └── ai.py
│   │   ├── schemas/             # Request validators
│   │   ├── services/            # Business logic
│   │   ├── utils/               # Utility functions
│   │   │   ├── auth.py
│   │   │   ├── errors.py
│   │   │   ├── helpers.py
│   │   │   ├── logging_config.py
│   │   │   └── file_upload.py
│   │   ├── middleware/          # Middleware
│   │   │   ├── security.py
│   │   │   └── rate_limiting.py
│   │   ├── ai/                  # AI/ML models
│   │   └── repositories/        # Data access layer
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test files
│   ├── run.py                   # Development server
│   ├── init_db.py              # Database initialization
│   ├── backup_db.py            # Database backup tool
│   ├── requirements.txt         # Python dependencies
│   └── ai-requirements.txt      # AI dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── store/               # State management
│   │   ├── utils/               # Utility functions
│   │   ├── App.jsx              # Main app
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── public/                  # Static assets
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── docs/                        # Documentation
│   ├── API.md
│   ├── API_COMPLETE.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPER_GUIDE.md (this file)
└── docker/                      # Docker configuration
```

---

## Database Models

### Key Models

**User** - System users
```python
class User(db.Model):
    id: str (UUID)
    email: str (unique)
    password_hash: str
    first_name: str
    last_name: str
    role: RoleEnum (admin, doctor, nurse, patient, staff)
    hospital_id: str (FK)
    is_active: bool
```

**Patient** - Patient records
```python
class Patient(db.Model):
    id: str (UUID)
    user_id: str (FK to User)
    patient_id_number: str (unique)
    date_of_birth: date
    gender: str
    blood_group: str
    weight: float
    height: float
    allergies: text
    chronic_conditions: text
    emergency_contact_name: str
    emergency_contact_phone: str
```

**Doctor** - Doctor profiles
```python
class Doctor(db.Model):
    id: str (UUID)
    user_id: str (FK to User)
    license_number: str (unique)
    specialization: str
    qualification: text
    experience_years: int
    consultation_fee: float
```

**Appointment** - Appointment bookings
```python
class Appointment(db.Model):
    id: str (UUID)
    patient_id: str (FK)
    doctor_id: str (FK)
    appointment_date: date
    start_time: time
    end_time: time
    status: AppointmentStatusEnum
    chief_complaint: text
    is_emergency: bool
    no_show_prediction_score: float
```

### Adding New Models

1. **Define in `/backend/app/models/__init__.py`:**
```python
class NewEntity(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'new_entities'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Add columns...
    hospital_id = db.Column(db.String(36), db.ForeignKey('hospitals.id'), nullable=False)
```

2. **Create migration:**
```bash
cd backend
alembic revision --autogenerate -m "Add new_entities table"
alembic upgrade head
```

3. **Create API route** in `/backend/app/routes/`

---

## API Architecture

### Blueprint Structure

Each resource has its own blueprint in `/backend/app/routes/`:

```python
from flask import Blueprint, request, g
from app.models import Patient
from app.utils.errors import BadRequest, NotFound
from app.middleware import rate_limit

patients_bp = Blueprint('patients', __name__, url_prefix='/api/v1/patients')

@patients_bp.route('', methods=['GET'])
@rate_limit(max_requests=100)
def list_patients():
    """List all patients with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get hospital from auth context
    hospital_id = g.hospital_id
    
    # Paginate query
    paginated = Patient.query.filter_by(hospital_id=hospital_id).paginate(
        page=page,
        per_page=per_page
    )
    
    return {
        'success': True,
        'message': 'Success',
        'data': [patient.to_dict() for patient in paginated.items],
        'meta': {
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    }, 200
```

### Response Format

All endpoints return this format:

```json
{
  "success": true,
  "message": "Human-readable message",
  "data": {},
  "meta": {}
}
```

### Error Responses

```python
from app.utils.errors import BadRequest, NotFound, Unauthorized

# In route handler
if not patient:
    raise NotFound('Patient not found')

if not authorized:
    raise Unauthorized('Not authorized for this operation')

if invalid_input:
    raise BadRequest('Field X is invalid')
```

---

## Frontend Architecture

### Component Structure

```
src/
├── components/
│   ├── Common.jsx           # Reusable UI components
│   ├── ProtectedRoute.jsx   # Auth-protected routes
│   └── ...
├── pages/
│   ├── LoginPage.jsx
│   ├── DashboardPage.jsx
│   ├── PatientsPage.jsx
│   └── ...
├── services/
│   ├── api.js              # Axios instance
│   ├── patientService.js
│   ├── appointmentService.js
│   └── ...
├── store/
│   ├── authStore.js        # Zustand auth state
│   └── appStore.js
└── utils/
    ├── helpers.js
    └── constants.js
```

### Creating a New Page

```jsx
import { useState, useEffect } from 'react'
import { Card, Loading, Error, Alert } from '../components/Common'
import patientService from '../services/patientService'

export default function PatientsPage() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadPatients = async () => {
      try {
        const response = await patientService.listPatients()
        setPatients(response.data.data || [])
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load patients')
      } finally {
        setLoading(false)
      }
    }
    loadPatients()
  }, [])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div>
      {/* Page content */}
    </div>
  )
}
```

### API Service Structure

```javascript
// src/services/patientService.js
import api from './api'

const patientService = {
  listPatients: (params = {}) => 
    api.get('/patients', { params }),
  
  getPatient: (id) => 
    api.get(`/patients/${id}`),
  
  createPatient: (data) => 
    api.post('/patients', data),
  
  updatePatient: (id, data) => 
    api.put(`/patients/${id}`, data),
  
  deletePatient: (id) => 
    api.delete(`/patients/${id}`)
}

export default patientService
```

---

## Authentication & Authorization

### JWT Token Flow

```
1. User logs in → POST /api/v1/auth/login
2. Server returns access_token + refresh_token
3. Client stores tokens in localStorage
4. Client includes token in Authorization header
5. Server validates token and extracts user info
```

### Protected Routes (Backend)

```python
from functools import wraps
from app.utils.auth import verify_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'success': False, 'message': 'Token required'}, 401
        
        try:
            user_data = verify_token(token.split()[-1])
            g.user_id = user_data['user_id']
            g.hospital_id = user_data['hospital_id']
            g.role = user_data['role']
        except:
            return {'success': False, 'message': 'Invalid token'}, 401
        
        return f(*args, **kwargs)
    return decorated

# Usage
@app.route('/api/v1/patients')
@token_required
def get_patients():
    # user_id available as g.user_id
    pass
```

### Role-Based Access Control

```python
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.role not in roles:
                return {'success': False, 'message': 'Insufficient permissions'}, 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# Usage
@app.route('/api/v1/admin/users')
@token_required
@role_required('admin')
def admin_users():
    pass
```

---

## Testing

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
```

### Writing Backend Tests

```python
# tests/test_patients.py
import unittest
from app import create_app, db
from app.models import Patient, Hospital, User, RoleEnum

class PatientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Setup test data
    
    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
    
    def test_list_patients(self):
        response = self.client.get(
            '/api/v1/patients',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
```

---

## Coding Standards

### Python (Backend)

- Use **PEP 8** style guide
- Type hints for function parameters and returns
- Docstrings for functions and classes
- 4 spaces indentation
- Max line length: 100 characters

```python
def create_patient(user_id: str, data: dict) -> tuple[bool, Patient, str]:
    """
    Create new patient record.
    
    Args:
        user_id: ID of user creating patient
        data: Patient data dictionary
    
    Returns:
        (success, patient_record, error_message)
    """
    pass
```

### JavaScript (Frontend)

- Use **ESLint** configuration
- Functional components with hooks
- CamelCase for variables/functions
- PascalCase for components
- Proper error handling

```javascript
// Good
function PatientCard({ patient, onEdit, onDelete }) {
  const handleClick = useCallback(() => {
    onEdit(patient.id)
  }, [patient.id, onEdit])
  
  return <div onClick={handleClick}>{patient.name}</div>
}
```

### Git Commits

```
[FEATURE] Add patient search functionality
[BUGFIX] Fix appointment status update
[DOCS] Update API documentation
[REFACTOR] Simplify patient validation logic
[TEST] Add tests for prescription creation
```

---

## Common Tasks

### Add New API Endpoint

1. **Create route** in appropriate blueprint
2. **Add request validation** in schemas/
3. **Implement business logic** in services/
4. **Write tests** in tests/
5. **Document** in API_COMPLETE.md

### Add New Database Field

1. **Update model** in models/__init__.py
2. **Create migration**: `alembic revision --autogenerate`
3. **Review migration** file
4. **Apply migration**: `alembic upgrade head`
5. **Update serialization** in to_dict() method

### Add New Frontend Page

1. **Create component** in pages/
2. **Create service** in services/ (if needed)
3. **Add route** in App.jsx
4. **Add navigation** link in sidebar
5. **Implement page** layout and logic

### Fix Bug

1. **Write failing test** that reproduces bug
2. **Implement fix**
3. **Verify test passes**
4. **Check for side effects**
5. **Create commit** with [BUGFIX] prefix

---

## Debugging

### Backend Debugging

```bash
# Enable debugging
export FLASK_DEBUG=1
python run.py

# Interactive debugger
import pdb; pdb.set_trace()

# Logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Frontend Debugging

```javascript
// Browser console
console.log('Value:', value)
console.error('Error:', error)

// React DevTools
// Install Chrome extension for component inspection

// Network tab
// Monitor API calls in DevTools

// Storage
localStorage.getItem('token')
```

### Database Debugging

```sql
-- Check active queries
SELECT * FROM pg_stat_activity;

-- View query plans
EXPLAIN ANALYZE SELECT ...;

-- Check indexes
SELECT * FROM pg_indexes WHERE tablename = 'patients';
```

---

## Useful Commands

```bash
# Backend
python -m flask shell              # Interactive Python shell
python manage.py db:migrate       # Run migrations
python -m pytest -v               # Verbose testing
python -m black backend/          # Code formatting

# Frontend
npm run lint                       # Check code style
npm run format                     # Format code
npm run build:analyze             # Analyze bundle size
npm run preview                    # Preview production build

# Database
psql -U postgres -d datacure_local # Connect to database
\dt                               # List tables
\d patients                        # Describe table

# Docker
docker-compose logs -f backend     # View logs
docker exec -it datacure bash      # Enter container
```

---

**Last Updated**: March 2025
**Version**: 1.0
