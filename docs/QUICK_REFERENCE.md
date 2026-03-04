# DataCure Developer Quick Reference

## Quick Start (5 minutes)

### 1. Setup
```bash
# Clone and navigate
git clone <repo>
cd DataCure

# Create env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install deps
pip install -r backend/requirements.txt

# Configure
cp backend/.env.example backend/.env
# Edit .env with local settings
```

### 2. Start Services
```bash
# Terminal 1: PostgreSQL
docker run --name postgres -e POSTGRES_DB=datacure \
  -e POSTGRES_PASSWORD=dev123 -p 5432:5432 -d postgres:15

# Terminal 2: Backend
cd backend
flask run  # Runs on http://localhost:5000
```

### 3. Test
```bash
# Health check
curl http://localhost:5000/health

# Register user
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@hospital.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "doctor",
    "hospital_id": "hosp-uuid"
  }'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@hospital.com", "password": "SecurePass123!"}'
```

---

## Project Structure

```
DataCure/
├── backend/
│   ├── app/
│   │   ├── __init__.py         # App factory
│   │   ├── config.py           # Configuration
│   │   ├── extensions.py       # DB, marshmallow, CORS
│   │   ├── models/
│   │   │   └── __init__.py     # 20+ ORM models
│   │   ├── schemas/
│   │   │   └── __init__.py     # Marshmallow validators
│   │   ├── services/           # Business logic
│   │   │   ├── auth.py         # Auth service
│   │   │   ├── patient.py      # Patient service
│   │   │   ├── appointment.py
│   │   │   ├── operations.py   # Billing, inventory, ward
│   │   │   └── ai.py           # ML predictions
│   │   ├── repositories/       # Data access
│   │   │   └── __init__.py     # Generic + specialized repos
│   │   ├── routes/             # API endpoints
│   │   │   ├── auth.py         # /api/v1/auth
│   │   │   ├── patients.py     # /api/v1/patients
│   │   │   ├── appointments.py
│   │   │   ├── ai.py           # /api/v1/ai
│   │   │   └── __init__.py     # Placeholder stubs
│   │   ├── utils/              # Helpers
│   │   │   ├── auth.py         # JWT, RBAC
│   │   │   ├── errors.py       # Error classes
│   │   │   ├── helpers.py      # Utilities
│   │   │   └── logging_config.py
│   ├── run.py                  # Entry point
│   ├── requirements.txt        # Python deps
│   ├── ai-requirements.txt     # ML deps
│   └── .env                    # Configuration
├── docker/
│   ├── Dockerfile              # Multi-stage build
│   ├── docker-compose.yml      # PostgreSQL, Redis, Nginx
│   └── nginx.conf              # Reverse proxy config
├── docs/
│   ├── API.md                  # API documentation
│   ├── DATABASE_SCHEMA.md      # Schema design
│   ├── ARCHITECTURE.md         # System design
│   ├── DEPLOYMENT.md           # Ops guide
│   ├── TESTING.md              # Test strategy
│   └── ROADMAP.md              # Implementation plan
├── tests/                       # Test suite (to create)
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── load/
├── frontend/                    # React app (to create)
└── README.md                   # Main guide
```

---

## Key Concepts

### Authentication Flow
```
Register → Hash password (bcrypt) → Create user
Login → Verify password → Generate JWT (1h) & refresh token (7d)
Request → Authorization header → Validate token → Extract claims
```

### Layer Architecture
```
Routes (HTTP) → Services (Logic) → Repositories (DB) → PostgreSQL
     ↑
  Schema validation
```

### Authorization
```
Token contains: user_id, email, role, hospital_id
@role_required→ Checks permission matrix → Allows/denies access
```

### Error Handling
```
ValidationError (400) → Missing/invalid input
UnauthorizedError (401) → Missing token
ForbiddenError (403) → Insufficient permissions
NotFoundError (404) → Resource not found
ConflictError (409) → Scheduling conflict
```

---

## Common Code Patterns

### Creating an Endpoint
```python
@patients_bp.route('', methods=['POST'])
@token_required              # Require JWT
@role_required('admin', 'doctor')  # Require role
def create_patient():
    # 1. Get & validate input
    data = request.get_json()
    schema = PatientCreateSchema()
    validated = schema.load(data)
    
    # 2. Call service
    success, patient_id = PatientService.create_patient(
        hospital_id=request.hospital_id,
        **validated
    )
    
    # 3. Return formatted response
    if success:
        return APIResponse.created({'patient_id': patient_id})
    else:
        return APIResponse.bad_request("Creation failed")
```

### Creating a Service
```python
class PatientService:
    @staticmethod
    def create_patient(hospital_id, **kwargs):
        """Create new patient with validation."""
        # 1. Validate input
        if not kwargs.get('user_id'):
            raise ValidationError("user_id required")
        
        # 2. Check business rules
        user = UserRepository.get_by_id(kwargs['user_id'])
        if not user:
            raise NotFoundError("User not found")
        
        # 3. Generate data
        patient_id_number = IDGenerator.generate_patient_id(hospital_id)
        
        # 4. Create and save
        patient = Patient(
            user_id=kwargs['user_id'],
            hospital_id=hospital_id,
            patient_id_number=patient_id_number,
            date_of_birth=kwargs['date_of_birth'],
            gender=kwargs['gender'],
            blood_group=kwargs.get('blood_group'),
            # ... more fields
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return True, patient.id
```

### Database Query (Repository)
```python
class PatientRepository(BaseRepository):
    model = Patient
    
    @staticmethod
    def get_by_patient_id_number(hospital_id, patient_id_number):
        """Get patient by unique ID number."""
        return Patient.query.filter_by(
            hospital_id=hospital_id,
            patient_id_number=patient_id_number,
            deleted_at=None  # Soft delete check
        ).first()
    
    @staticmethod
    def get_by_hospital(hospital_id, page=1, per_page=20):
        """Get all patients in hospital with pagination."""
        query = Patient.query.filter(
            Patient.hospital_id == hospital_id,
            Patient.deleted_at.is_(None)
        )
        return query.paginate(page=page, per_page=per_page)
```

### Validation (Schema)
```python
from marshmallow import Schema, fields, validate, validates, ValidationError

class PatientCreateSchema(Schema):
    user_id = fields.UUID(required=True)
    date_of_birth = fields.Date(required=True)
    gender = fields.String(required=True, validate=validate.OneOf(['M', 'F', 'Other']))
    blood_group = fields.String(validate=validate.OneOf(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']))
    weight = fields.Decimal(places=2)
    height = fields.Integer()
    allergies = fields.String(validate=validate.Length(max=500))
    
    @validates('date_of_birth')
    def validate_dob(self, value):
        """Ensure valid age."""
        age = (datetime.now() - value).days // 365
        if age < 0 or age > 150:
            raise ValidationError("Invalid date of birth")
```

---

## Common Commands

### Development
```bash
# Run app
flask run

# Create database
flask init_db

# Seed sample data
flask seed_db

# Run tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_auth.py::TestAuthenticationService::test_register_success -v
```

### Database
```bash
# Start PostgreSQL
docker run --name postgres -e POSTGRES_PASSWORD=dev123 \
  -p 5432:5432 -d postgres:15

# Connect to DB
psql postgresql://postgres:dev123@localhost:5432/datacure

# View users
SELECT id, email, role FROM users;

# View appointments
SELECT id, patient_id, doctor_id, appointment_date FROM appointments;
```

### Docker
```bash
# Build image
docker build -f docker/Dockerfile -t datacure:1.0 .

# Run stack
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f backend

# Stop all
docker-compose -f docker/docker-compose.yml down
```

### API Testing with curl
```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@hosp.com","password":"Pass123!","confirm_password":"Pass123!","first_name":"John","last_name":"Doe","role":"doctor","hospital_id":"hosp-uuid"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@hosp.com","password":"Pass123!"}'

# Get patients (with token)
curl -X GET "http://localhost:5000/api/v1/patients?page=1" \
  -H "Authorization: Bearer <access_token>"

# Create appointment
curl -X POST http://localhost:5000/api/v1/appointments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"uuid","doctor_id":"uuid","appointment_date":"2025-03-15","start_time":"10:00","end_time":"10:30"}'

# Predict readmission risk
curl -X POST http://localhost:5000/api/v1/ai/predict/readmission \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"uuid"}'
```

### Environment Variables
```bash
# .env required values
DATABASE_URL=postgresql://user:password@localhost:5432/datacure
JWT_SECRET_KEY=your-very-long-random-secret-key-min-32-chars
FLASK_ENV=development
FLASK_APP=run.py
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 days

# Optional (Firebase, AWS, etc)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-key.json
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

---

## Troubleshooting Quick Fixes

### "ModuleNotFoundError: No module named 'flask'"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "psycopg2: connection refused"
```bash
# Start PostgreSQL
docker run --name postgres -e POSTGRES_PASSWORD=dev123 \
  -p 5432:5432 -d postgres:15

# Or verify DATABASE_URL is correct
echo $DATABASE_URL
# Should be: postgresql://user:password@localhost:5432/dbname
```

### "401 Unauthorized" on protected routes
```bash
# Get fresh token
TOKEN=$(curl ... /api/v1/auth/login)
# Use token
curl -H "Authorization: Bearer $TOKEN" ...
```

### "409 Conflict - Patient conflict"
```bash
# Check if email/user already exists
SELECT COUNT(*) FROM users WHERE email = 'user@hospital.com';

# Check if patient already created
SELECT COUNT(*) FROM patients WHERE user_id = 'user-uuid';
```

### "High database query time"
```bash
# Index critical columns
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_patients_hospital ON patients(hospital_id);
CREATE INDEX idx_users_email ON users(email, hospital_id);

# Check slow queries
SELECT query, calls, mean_time FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
```

---

## Role-based Access Control Quick Reference

| Role | Can Access |
|------|-----------|
| **admin** | All endpoints, user management, analytics |
| **doctor** | Own patients, appointments, prescriptions, AI predictions |
| **nurse** | Patient records, ward management, prescriptions |
| **reception** | Patient registration, appointment booking, billing |
| **patient** | Own data only (appointments, records, billing) |

---

## API Response Format

### Success Response (200, 201)
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "uuid",
    "name": "John Doe"
  },
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
```

### Error Response (4xx, 5xx)
```json
{
  "success": false,
  "message": "Patient not found",
  "error_code": "NOT_FOUND",
  "details": {
    "patient_id": "uuid"
  }
}
```

---

## Key Files and Their Purpose

| File | Purpose |
|------|---------|
| `app/__init__.py` | App factory, blueprint registration |
| `app/config.py` | Environment-based configuration |
| `app/models/__init__.py` | All ORM entity definitions |
| `app/schemas/__init__.py` | Request/response validation |
| `app/services/*.py` | Business logic implementation |
| `app/repositories/__init__.py` | Data access abstraction |
| `app/routes/*.py` | HTTP endpoint handlers |
| `app/utils/auth.py` | JWT, RBAC, decorators |
| `app/utils/errors.py` | Error handling, response formatting |
| `run.py` | Application entry point |

---

## Performance Tips

1. **Use pagination**: Always paginate list responses
2. **Lazy load**: Use relationships with `lazy='select'`
3. **Cache**: Redis for frequently accessed data
4. **Index**: Create indexes on frequently queried columns
5. **Batch**: Group database operations
6. **Connection pooling**: Configured in SQLAlchemy

---

## Security Reminders

✅ Always validate input with schemas
✅ Always use @token_required on protected routes
✅ Always check role permissions with @role_required
✅ Never log passwords or tokens
✅ Always hash passwords with bcrypt
✅ Always use HTTPS in production
✅ Always set strong JWT secret key
✅ Always enable rate limiting

---

## Getting Help

1. **API Issues** → Check [API.md](docs/API.md)
2. **Database** → Check [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)
3. **Deployment** → Check [DEPLOYMENT.md](docs/DEPLOYMENT.md)
4. **Architecture** → Check [ARCHITECTURE.md](docs/ARCHITECTURE.md)
5. **Tests** → Check [TESTING.md](docs/TESTING.md)
6. **Roadmap** → Check [ROADMAP.md](docs/ROADMAP.md)

---

**Last Updated**: February 2025
**Version**: 1.0
