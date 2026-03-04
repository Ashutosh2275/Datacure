# DataCure Architecture & Design

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Clients                                      │
├─────────────────────────────────────────────────────────────────────┤
│  Web (React)  │  Mobile (iOS/Android)  │  Desktop  │  Admin Portal  │
└────────────┬──────────────────────────────┬────────────────────────┘
             │                              │
             └──────────────┬───────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │      Nginx Reverse Proxy              │
        │  (SSL/TLS, Rate Limiting, CORS)       │
        └────────────────┬──────────────────────┘
                         │
        ┌────────────────▼──────────────────────┐
        │   Flask REST API (Python 3.11+)       │
        │                                        │
        │  ┌──────────────────────────────────┐ │
        │  │   Routes Layer                    │ │
        │  │  (/api/v1/auth, /patients, ...)  │ │
        │  └──────────────┬───────────────────┘ │
        │                 │                      │
        │  ┌──────────────▼───────────────────┐ │
        │  │   Services Layer                  │ │
        │  │  (Business Logic)                 │ │
        │  └──────────────┬───────────────────┘ │
        │                 │                      │
        │  ┌──────────────▼───────────────────┐ │
        │  │   Repositories Layer              │ │
        │  │  (Data Access)                    │ │
        │  └──────────────┬───────────────────┘ │
        │                 │                      │
        └─────────────────┼──────────────────────┘
                          │
        ┌─────────────────┴────────────────────┐
        │                                       │
        │                                       │
    ┌───▼────────────┐              ┌──────────▼────┐
    │  PostgreSQL    │              │   Redis       │
    │  (Primary DB)  │              │  (Cache)      │
    └────────────────┘              └────────────────┘
        │
        ├── Patients, Users, Doctors
        ├── Appointments, Prescriptions
        ├── Billing, Inventory
        ├── AI Risk Scores
        └── Audit Logs

    External Services:
    ├── Firebase (Push Notifications)
    ├── AWS S3 (File Storage)
    └── SendGrid/SMTP (Email)
```

---

## Layered Architecture

### Layer 1: Presentation (HTTP/REST)
**Responsibility**: Handle HTTP requests/responses

**Components**:
- HTTP Routes (`app/routes/`)
- Request validation (Marshmallow schemas)
- Response formatting (APIResponse)
- Pagination handling

**Technologies**: Flask, Flask-CORS, blueprints

**Example Flow**:
```
POST /api/v1/appointments
    ↓
Route handler validates request
    ↓
Calls AppointmentService.book_appointment()
    ↓
Returns formatted JSON response
```

---

### Layer 2: Service (Business Logic)
**Responsibility**: Implement business logic, workflows, validations

**Components**:
- `AuthenticationService` - Login, registration, token refresh
- `PatientService` - Patient registration, medical records
- `AppointmentService` - Appointment lifecycle (book, reschedule, cancel)
- `PrescriptionService` - Prescription management
- `BillingService` - Invoice creation and payment tracking
- `InventoryService` - Medicine stock management
- `WardService` - Bed allocation and discharge
- `AIService` - ML predictions and risk scoring

**Design Pattern**: Service pattern with dependency injection

**Characteristics**:
- Pure business logic, no HTTP awareness
- Reusable across different interfaces
- Comprehensive error handling
- State management

**Example Service**:
```python
class AppointmentService:
    def book_appointment(self, patient_id, doctor_id, date, time):
        # Validation
        if not self._patient_exists(patient_id):
            raise NotFoundError("Patient not found")
        
        if not self._date_valid(date):
            raise ValidationError("Invalid date")
        
        # Check conflicts
        if self._has_conflict(doctor_id, date, time):
            raise ConflictError("Time slot not available")
        
        # Create appointment
        appointment = Appointment(...)
        db.session.add(appointment)
        db.session.commit()
        
        return True, appointment.id
```

---

### Layer 3: Repository (Data Access)
**Responsibility**: Abstract database operations

**Components**:
- `BaseRepository` - Common CRUD operations
- Specialized repositories for each entity
- Query building and filtering
- Lazy loading optimization

**Design Pattern**: Repository pattern

**Methods**:
```python
class BaseRepository:
    def create(entity, **kwargs)      # INSERT
    def get_by_id(id)                  # SELECT WHERE id
    def get_all()                      # SELECT all
    def update(id, **kwargs)           # UPDATE
    def delete(id)                     # DELETE (soft or hard)
    def count()                        # COUNT
    def filter(**kwargs)               # WHERE clauses
    def paginate(page, per_page)       # Pagination
```

**Specialized Repositories**:
```python
class AppointmentRepository:
    def get_by_patient(patient_id)
    def get_by_doctor(doctor_id)
    def get_by_date(date)
    def get_today_appointments()
    def get_by_status(status)
```

---

### Layer 4: Database (Data Persistence)
**Responsibility**: Persist and retrieve data

**Components**:
- PostgreSQL database
- SQLAlchemy ORM models
- Database migrations (Alembic)

**Technologies**: PostgreSQL, SQLAlchemy 2.0

**Key Tables**:
| Table | Purpose |
|-------|---------|
| users | User accounts and authentication |
| patients | Patient information |
| doctors | Doctor profiles and schedules |
| appointments | Appointment bookings |
| prescriptions | Medicine prescriptions |
| medicines | Medicine master list |
| medicine_inventory | Stock tracking |
| billings | Invoices and payments |
| wards, beds | Ward and bed management |
| ai_risk_scores | ML predictions |
| ai_logs | Prediction audit |
| audit_logs | Compliance tracking |

---

## Cross-Cutting Concerns

### Authentication & Authorization

**Flow**:
```
1. User provides email + password
    ↓
2. AuthenticationService.login()
    ├─ Hash password with bcrypt
    ├─ Compare with stored hash
    ├─ Generate JWT access token (expires 1h)
    └─ Generate refresh token (expires 7d)
    ↓
3. Client stores tokens (localStorage/cookie)
    ↓
4. Subsequent requests include: Authorization: Bearer <token>
    ↓
5. @token_required decorator:
    ├─ Extracts token from header
    ├─ Validates signature
    ├─ Checks expiration
    └─ Extracts user claims (user_id, hospital_id, role)
    ↓
6. @role_required decorator:
    ├─ Checks role in claims
    └─ Validates against PermissionMatrix
    ↓
7. Request proceeds with user context
```

**JWT Structure**:
```json
{
  "sub": "user-uuid",
  "email": "user@hospital.com",
  "role": "doctor",
  "hospital_id": "hospital-uuid",
  "exp": 1645978800,
  "iat": 1645975200
}
```

**Permission Matrix**:
```python
PERMISSIONS = {
    'admin': {
        'user:read', 'user:create', 'user:update', 'user:delete',
        'patient:read', 'patient:create', 'patient:update',
        'appointment:read', 'appointment:manage',
        'billing:read', 'billing:create', 'billing:approve',
        'inventory:read', 'inventory:manage',
        'ai:read', 'ai:acknowledge',
        'audit:read', 'admin:access'
    },
    'doctor': {
        'patient:read', 'patient:create', 'patient:update',
        'appointment:read', 'appointment:manage',
        'prescription:create', 'prescription:read',
        'billing:read',
        'ai:read', 'ai:acknowledge'
    },
    'patient': {
        'patient:read',  # Own data only
        'appointment:read',  # Own appointments
        'prescription:read',  # Own prescriptions
        'billing:read'  # Own bills
    }
}
```

---

### Error Handling

**Error Hierarchy**:
```
APIError (base)
├── ValidationError (400)
│   └── Invalid input, constraints violated
├── UnauthorizedError (401)
│   └── Missing or invalid token
├── ForbiddenError (403)
│   └── Insufficient permissions
├── NotFoundError (404)
│   └── Resource not found
├── ConflictError (409)
│   └── Resource already exists, scheduling conflict
└── InternalError (500)
    └── Server error
```

**Usage**:
```python
@app.errorhandler(APIError)
def handle_api_error(error):
    response = {
        'success': False,
        'error_code': error.error_code,
        'message': error.message,
        'details': error.details
    }
    return jsonify(response), error.status_code

# In route/service:
if not doctor.is_available:
    raise ForbiddenError("Doctor not accepting new patients")
```

---

### Validation Strategy

**Multi-Layer Validation**:
```
1. Schema Validation (Marshmallow)
   ├─ Field types
   ├─ Required fields
   ├─ Custom validators (email, phone, password strength)
   └─ Nested objects

2. Business Logic Validation (Service Layer)
   ├─ User existence
   ├─ Role permissions
   ├─ Schedule conflicts
   ├─ Expiry dates
   └─ Stock availability

3. Database Constraints (PostgreSQL)
   ├─ UNIQUE constraints
   ├─ FOREIGN KEY constraints
   ├─ CHECK constraints
   └─ NOT NULL
```

**Validation Example**:
```python
# Schema level
class AppointmentCreateSchema(Schema):
    patient_id = UUID(required=True)
    doctor_id = UUID(required=True)
    appointment_date = Date(required=True, validate=validate_future_date)
    start_time = Time(required=True)
    chief_complaint = String(required=True, validate=Length(min=10, max=500))

# Service level
class AppointmentService:
    def book_appointment(self, patient_id, doctor_id, date, time):
        # Check patient exists
        patient = PatientRepository.get_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient not found")
        
        # Check doctor availability
        if not DoctorService.is_available(doctor_id, date, time):
            raise ConflictError("Doctor not available")
        
        # Check past date
        if date < datetime.now().date():
            raise ValidationError("Cannot book past appointments")
        
        # Create and return
        appointment = Appointment(...)
        return appointment
```

---

### Soft Deletes & GDPR Compliance

**Mixin Implementation**:
```python
class SoftDeleteMixin:
    deleted_at = db.Column(db.DateTime)
    
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def restore(self):
        self.deleted_at = None
        db.session.commit()

# Usage in queries
class BaseRepository:
    def get_all(self):
        return self.model.query.filter(self.model.deleted_at.is_(None)).all()
```

**Benefits**:
- Data recovery capability
- Audit trail (when deleted)
- Referential integrity (soft deletes don't break FKs)
- GDPR compliance (user can request deletion)

---

### Logging & Audit Trail

**Logging Strategy**:
```python
# File: app/utils/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request.headers.get('X-Request-ID', 'N/A')
        return True

# Setup
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('logs/app.log', maxBytes=10MB, backupCount=10)
logger.addFilter(RequestIdFilter())

# Usage
logger.info(f"User {user_id} logged in", extra={'request_id': req_id})
logger.error(f"Failed to book appointment", exc_info=True)
```

**Audit Logging** (for HIPAA compliance):
```python
class AuditLog(db.Model):
    """Track all changes for compliance."""
    hospital_id = db.Column(db.UUID, FK)
    user_id = db.Column(db.UUID, FK)  # Who made change
    action = db.Column(db.String(50))  # create, read, update, delete
    entity_type = db.Column(db.String(100))  # Model name
    entity_id = db.Column(db.UUID)  # What changed
    changes = db.Column(db.JSON)  # Before/after values
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Usage
def audit_log(user_id, action, entity_type, entity_id, changes):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes
    )
    db.session.add(log)
    db.session.commit()
```

---

## AI/ML Integration

### ML Service Architecture

```
┌─────────────────────────────────────────┐
│   ML Model Manager (AIService)          │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Readmission Risk Predictor     │   │
│  │  ├─ Feature extraction          │   │
│  │  ├─ Model: LightGBM             │   │
│  │  ├─ Output: 0.0-1.0 score       │   │
│  │  └─ SHAP explanations           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  No-Show Predictor              │   │
│  │  ├─ Features: Appointment data  │   │
│  │  ├─ Model: Random Forest        │   │
│  │  └─ Output: Probability         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Patient Flow Forecaster        │   │
│  │  ├─ Time series analysis        │   │
│  │  ├─ ARIMA model                 │   │
│  │  └─ 7-30 day forecast           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Medicine Demand Forecast       │   │
│  │  ├─ Historical usage analysis   │   │
│  │  ├─ Seasonal patterns           │   │
│  │  └─ Prediction: Items/day       │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Model Persistence (joblib)     │   │
│  │  ├─ Load from /models/          │   │
│  │  ├─ Save trained models         │   │
│  │  └─ Version management          │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**Feature Extraction Pipeline**:
```python
class PatientFeatureExtractor:
    def extract_readmission_features(self, patient_id):
        """Extract features for readmission prediction."""
        patient = Patient.query.get(patient_id)
        
        recent_appointments = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.created_at >= datetime.now() - timedelta(days=90)
        ).count()
        
        chronic_conditions = len(patient.chronic_conditions.split(','))
        age = (datetime.now() - patient.date_of_birth).days // 365
        
        return {
            'age': age,
            'gender_encoded': self.encode_gender(patient.gender),
            'chronic_count': chronic_conditions,
            'recent_visits': recent_appointments,
            'avg_appointment_days_apart': self.calculate_interval(patient_id),
            'prescription_count': patient.prescriptions.count(),
            'billing_amount_90d': self.sum_billing_90d(patient_id)
        }

# Prediction
features = extractor.extract_readmission_features(patient_id)
risk_score = ml_service.predict_readmission_risk(features)
```

**Model Performance Tracking**:
```python
class ModelMetrics(db.Model):
    """Track model performance over time."""
    hospital_id = db.Column(db.UUID, FK)
    model_type = db.Column(db.String(100))
    accuracy = db.Column(db.Numeric(3,2))  # 0.0-1.0
    precision = db.Column(db.Numeric(3,2))
    recall = db.Column(db.Numeric(3,2))
    f1_score = db.Column(db.Numeric(3,2))
    auc_roc = db.Column(db.Numeric(3,2))
    total_predictions = db.Column(db.Integer)
    last_trained = db.Column(db.DateTime)
    version = db.Column(db.String(20))
```

---

## Security Architecture

### Defense in Depth

```
Layer 1: Network Security
├─ HTTPS/TLS encryption
├─ Nginx reverse proxy
└─ Rate limiting

Layer 2: Authentication
├─ JWT tokens
├─ Refresh token rotation
└─ Session management

Layer 3: Authorization
├─ Role-based access control (RBAC)
├─ Permission checks
└─ Hospital isolation

Layer 4: Input Validation
├─ Schema validation
├─ SQL injection prevention (ORM)
└─ XSS prevention (JSON responses)

Layer 5: Data Protection
├─ Password hashing (bcrypt)
├─ Soft deletes (GDPR)
├─ Audit logs (HIPAA)
└─ Encryption at rest (optional)
```

### Security Headers (Nginx)
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

---

## Data Flow Examples

### Patient Registration Flow
```
1. POST /api/v1/auth/register
   Request: {email, password, first_name, last_name, hospital_id, role}
   
2. Route Layer (@role_required('admin'))
   ├─ Validate schema
   └─ Pass to AuthenticationService
   
3. AuthenticationService.register()
   ├─ Check email uniqueness
   ├─ Validate password strength
   ├─ Hash password with bcrypt
   ├─ Create User entity
   └─ Save to database via UserRepository
   
4. Return response with user_id
   Response: {success: true, user_id: "uuid"}
   
5. Frontend stores user_id for patient creation
   
6. POST /api/v1/patients
   Request: {user_id, date_of_birth, gender, blood_group, ...}
   
7. PatientService.create_patient()
   ├─ Generate unique patient_id_number
   ├─ Create Patient entity
   ├─ Link to User
   └─ Save to database
   
8. Return response with patient_id
   Response: {success: true, patient_id_number: "PAT-HOSP-20250228-ABC1"}
```

### Appointment Booking Flow
```
1. POST /api/v1/appointments
   Request: {patient_id, doctor_id, appointment_date, start_time, ...}
   
2. Route Layer (@token_required)
   ├─ Validate JWT token
   ├─ Extract user context (user_id, hospital_id)
   ├─ Validate schema
   └─ Pass to AppointmentService
   
3. AppointmentService.book_appointment()
   ├─ Verify patient exists and belongs to hospital
   ├─ Verify doctor exists and available
   ├─ Check for scheduling conflicts (Repository query)
   ├─ Check for hard constraints (double booking)
   ├─ Create Appointment entity
   ├─ Save to database
   ├─ Get AI no-show predictor
   ├─ Generate no-show prediction
   ├─ Update appointment with prediction score
   └─ Log to audit trail
   
4. Return success response with appointment_id
   Response: {success: true, appointment_id: "uuid"}
   
5. Send notification (async job)
   ├─ Format appointment details
   ├─ Send Firebase notification
   └─ Log to audit trail
```

---

## Design Patterns Used

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Repository Pattern** | `app/repositories/` | Abstract data access |
| **Service Pattern** | `app/services/` | Encapsulate business logic |
| **Decorator Pattern** | `app/utils/auth.py` | Attach auth behavior (@token_required) |
| **Factory Pattern** | `app/__init__.py` | Create app instances (create_app) |
| **Singleton Pattern** | Extensions (db, ma) | Single instance per app |
| **Observer Pattern** | Audit logs | Track all changes |
| **Strategy Pattern** | AI models | Multiple prediction strategies |
| **Mixin Pattern** | `TimestampMixin`, `SoftDeleteMixin` | Reuse common behavior |

---

## Performance Considerations

### Database Optimization
- Connection pooling (SQLAlchemy)
- Query optimization (select only needed columns)
- Indexing on frequently queried fields
- Eager loading for relationships
- Pagination for large datasets

### Caching Strategy
- HTTP caching headers
- Redis for session/token caching
- Doctor availability: Cache for 30 minutes
- Medicine list: Cache for 1 hour
- Hospital data: Cache for 1 day

### API Response Times (SLA)
- Simple queries: < 100ms
- List endpoints (paginated): < 500ms
- AI predictions: < 2 seconds
- Complex reports: < 5 seconds

---

## Scalability Architecture

### Horizontal Scaling
```
Load Balancer (AWS ELB)
├─ Flask Backend 1
├─ Flask Backend 2
├─ Flask Backend 3
└─ Flask Backend 4
    └─ All connect to shared PostgreSQL + Redis
```

### Database Scaling
- Read replicas for queries
- Write to primary, read from replicas
- Partitioning large tables (appointments by year)
- Archiving old records

### Async Jobs (Celery Ready)
```python
@celery.task
def send_appointment_reminder(appointment_id):
    """Send reminder 24 hours before appointment."""
    pass

@celery.task
def train_ml_model(model_type):
    """Train/retrain ML models."""
    pass

@celery.task
def generate_daily_reports():
    """Generate daily KPI reports."""
    pass
```

---

**Last Updated**: February 2025
**Version**: 1.0
