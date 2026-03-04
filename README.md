# DataCure - AI-Powered Hospital Intelligence Platform

A production-grade, modular hospital management system with AI/ML capabilities for predictive analytics and optimization.

## 🏥 Overview

DataCure is a comprehensive digital healthcare platform designed for mid-scale hospitals with:

- **Core HMS**: Patient, Doctor, Appointment, Billing, Inventory Management
- **AI Intelligence**: Readmission risk prediction, No-show forecasting, Patient flow prediction, Medicine demand forecasting
- **Security**: JWT authentication, Role-based access control, Audit logging
- **Scalability**: Microservice-ready architecture, Docker containerization, Cloud-native deployment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│            (Firebase Hosting / Firebase RTK)            │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (JSON)
┌────────────────────▼────────────────────────────────────┐
│         API Gateway (Nginx Reverse Proxy)               │
│    Rate Limiting • CORS • SSL/TLS • Load Balancing      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Backend (Flask/Python)                     │
├─────────────────────────────────────────────────────────┤
│  Routes Layer       │ Authentication & Authorization    │
│  ↓                 │ ↓                                  │
│  Services Layer    │ JWT + Role-based Access Control    │
│  ↓                 │ ↓                                  │
│  Repository Layer  │ Audit Logging & Compliance         │
│  ↓                 │                                    │
│  Database Layer    │                                    │
└─────────┬──────────┴────────────────────────────────────┘
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Firebase │  │ AI/ML    │  │ Database │
    │ Real-time│  │ Module   │  │PostgreSQL│
    │ Notif    │  │Scikit-ML │  │  (RDS)   │
    └──────────┘  └──────────┘  └──────────┘
```

### Layer Breakdown

**1. Presentation Layer**: React frontend with role-based routing
**2. API Gateway**: Nginx reverse proxy with rate limiting and CORS
**3. Business Logic**: Service layer with clean architecture
**4. Data Access**: Repository pattern for database abstraction
**5. Database**: PostgreSQL with indexing and constraints
**6. AI Service**: Separate ML module for predictions

## 📋 System Requirements

- Python 3.11+
- PostgreSQL 13+
- Node.js 16+ (for frontend)
- Docker & Docker Compose
- 2GB+ RAM
- 10GB+ Storage

## 🚀 Quick Start (Local Development)

### 1. Setup Environment

```bash
# Clone repository
git clone <your-repo>
cd DataCure

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/ai-requirements.txt
```

### 2. Configure Database

```bash
# Update .env with PostgreSQL connection
# Default local: postgresql://postgres:password@localhost:5432/datacure_local

# Or use Docker Compose:
docker-compose -f docker/docker-compose.yml up -d postgres
```

### 3. Initialize Database

```bash
# Using Flask CLI
flask db init  # First time only
flask db migrate
flask db upgrade

# Or direct creation
flask init-db  # Creates tables
```

### 4. Run Backend Server

```bash
# Development
flask run

# Or using Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

### 5. Test API

```bash
# Health check
curl http://localhost:5000/health

# Should return:
# {
#   "status": "healthy",
#   "service": "DataCure API",
#   "environment": "development"
# }
```

## 🐳 Docker Deployment

### Using Docker Compose (Full Stack):

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up

# Logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop
docker-compose -f docker/docker-compose.yml down
```

### Services Started:
- PostgreSQL on port 5432
- Redis on port 6379
- Flask Backend on port 5000
- Nginx on ports 80/443

## 🔐 Authentication

### Register User

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "doctor",
    "hospital_id": "hospital-uuid"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "Bearer",
    "user": {...}
  }
}
```

### Use Token

```bash
curl http://localhost:5000/api/v1/patients \
  -H "Authorization: Bearer <access_token>"
```

## 📊 AI Predictions

### Readmission Risk

```bash
curl -X POST http://localhost:5000/api/v1/ai/predict/readmission \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid"
  }'
```

### No-Show Probability

```bash
curl -X POST http://localhost:5000/api/v1/ai/predict/no-show \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_id": "appt-uuid"
  }'
```

### Patient Flow Forecast

```bash
curl "http://localhost:5000/api/v1/ai/forecast/patient-flow?days=7" \
  -H "Authorization: Bearer <token>"
```

## 🗄️ Database Schema

Key entities:
- **Users**: System users with roles
- **Patients**: Patient demographics and medical history
- **Doctors**: Doctor profiles and specializations
- **Appointments**: Booking and scheduling
- **Prescriptions**: Medicine management
- **Billing**: Invoices and payments
- **Inventory**: Medicine stock management
- **Beds**: Ward and bed allocation
- **AI_Logs**: Model prediction tracking
- **Audit_Logs**: Compliance and security logging

## 🔒 Security Features

✅ JWT-based authentication with refresh tokens
✅ Role-based access control (RBAC)
✅ Bcrypt password hashing
✅ SQL injection prevention (ORM)
✅ XSS prevention (Marshmallow validation)
✅ CORS configuration
✅ Rate limiting (Nginx)
✅ Audit logging for all actions
✅ HTTPS/SSL enforcement

## 📈 Performance Optimization

- Connection pooling (SQLAlchemy)
- Query optimization with indexing
- N+1 query prevention
- Response caching
- Pagination for large datasets
- Async task processing (Celery ready)

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# API tests
pytest tests/api

# Load testing
locust -f tests/load/locustfile.py
```

## 📚 API Documentation

API endpoints follow RESTful conventions:

```
GET    /api/v1/patients              - List patients
POST   /api/v1/patients              - Create patient
GET    /api/v1/patients/{id}         - Get patient
PUT    /api/v1/patients/{id}         - Update patient

GET    /api/v1/appointments          - List appointments
POST   /api/v1/appointments          - Book appointment
PUT    /api/v1/appointments/{id}     - Reschedule

GET    /api/v1/prescriptions/{pid}   - Get prescriptions
POST   /api/v1/prescriptions         - Create prescription

GET    /api/v1/billing               - List invoices
POST   /api/v1/billing               - Create invoice

GET    /api/v1/ai/predict/readmission - AI predictions
GET    /api/v1/ai/forecast/patient-flow - Flow forecasting
```

## 🚢 Production Deployment

### AWS EC2 Deployment:

1. **Setup EC2 Instance** (t3.medium or larger)
2. **Install Docker**
3. **Clone Repository**
4. **Configure Environment**
5. **Run Docker Compose**
6. **Setup RDS PostgreSQL**
7. **Configure CloudFront CDN**
8. **Setup Load Balancer**

### Environment Variables for Production:

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:pwd@rds-endpoint:5432/datacure
SECRET_KEY=<generate-strong-key>
JWT_SECRET_KEY=<generate-strong-key>
AWS_S3_BUCKET=datacure-hospital-files
FIREBASE_CREDENTIALS_PATH=/secrets/firebase-credentials.json
```

## 📝 Configuration Files

- `.env` - Environment variables
- `backend/app/config.py` - Flask configuration
- `docker/docker-compose.yml` - Docker setup
- `docker/nginx.conf` - Reverse proxy config

## 🤖 AI Model Management

Models are stored in `backend/ai/models/`:
- `readmission_model_v1.0.joblib` - Readmission risk model
- `noshow_model_v1.0.joblib` - No-show prediction model
- `medicine_demand_v1.0.joblib` - Medicine demand forecast

Models can be retrained using:
```python
from app.services.ai import AIService
ai_service = AIService()
# Retrain and save models
```

## 📖 Documentation Files

- `/docs/API.md` - Detailed API endpoints
- `/docs/DATABASE.md` - Schema and migrations
- `/docs/DEPLOYMENT.md` - Production setup
- `/docs/AI_MODELS.md` - ML model documentation

## 🔧 Troubleshooting

### Common Issues:

**"Connection refused" error:**
```bash
# Check PostgreSQL is running
# For Docker: docker-compose up -d postgres
```

**"ModuleNotFoundError":**
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall
```

**Database migration errors:**
```bash
# Reset database (dev only!)
flask drop-db
flask init-db
```

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push branch: `git push origin feature/amazing-feature`
4. Create Pull Request

## 📄 License

This project is proprietary and confidential. Unauthorized copying is prohibited.

## 📧 Support

For issues and support:
- Email: ashutoshmishra2275@gmail.com
- Issues: GitHub Issues

---

**Built with ❤️ for better healthcare management**
