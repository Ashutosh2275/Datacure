# DataCure Deployment & Operations Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Firebase Integration](#firebase-integration)
5. [Database Management](#database-management)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Checklist](#security-checklist)
8. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)

### Step 1: Clone & Navigate
```bash
git clone <repository-url>
cd DataCure
```

### Step 2: Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Backend
pip install -r backend/requirements.txt
pip install -r backend/ai-requirements.txt

# Frontend (optional)
cd frontend
npm install
cd ..
```

### Step 4: Configure Environment
```bash
# Copy example config
cp backend/.env.example backend/.env

# Edit with local settings
# DATABASE_URL=postgresql://user:password@localhost:5432/datacure_dev
# JWT_SECRET_KEY=your-dev-secret-key
```

### Step 5: Setup Database
```bash
# Create database
createdb datacure_dev

# Or via Docker
docker run --name postgres-dev -e POSTGRES_DB=datacure_dev \
  -e POSTGRES_USER=datacure -e POSTGRES_PASSWORD=dev123 \
  -p 5432:5432 -d postgres:15

# Run migrations
cd backend
alembic upgrade head
cd ..
```

### Step 6: Seed Sample Data (Optional)
```bash
cd backend
flask init_db
flask seed_db
cd ..
```

### Step 7: Start Backend
```bash
cd backend
flask run
```

Server runs on: `http://localhost:5000`

### Step 8: Start Frontend (Optional)
```bash
cd frontend
npm start
```

Frontend runs on: `http://localhost:3000`

---

## Docker Deployment

### Quick Start (Docker Compose)
```bash
# From project root
docker-compose -f docker/docker-compose.yml up -d

# Check services
docker-compose -f docker/docker-compose.yml ps

# View logs
docker-compose -f docker/docker-compose.yml logs -f backend

# Shutdown
docker-compose -f docker/docker-compose.yml down
```

**Services Running:**
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Backend: `http://localhost:5000`
- Nginx: `http://localhost:80`, `https://localhost:443`

### Manual Docker Build
```bash
# Build image
docker build -f docker/Dockerfile -t datacure:1.0 .

# Run backend
docker run -d \
  --name datacure-backend \
  -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:pass@postgres:5432/datacure \
  -e FLASK_ENV=production \
  --network datacure_network \
  datacure:1.0

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up -d
```

### Health Check
```bash
# Backend health
curl http://localhost:5000/health

# Response
{
  "status": "healthy",
  "timestamp": "2025-02-28T10:30:00Z"
}
```

---

## AWS Deployment

### 1. Setup RDS PostgreSQL
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier datacure-prod \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username datacure \
  --master-user-password <strong-password> \
  --allocated-storage 100 \
  --multi-az
```

### 2. Setup Elasticache Redis
```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id datacure-cache \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --engine-version 7.0
```

### 3. Setup ECR Repository
```bash
# Create repository
aws ecr create-repository --repository-name datacure

# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag datacure:1.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/datacure:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/datacure:latest
```

### 4. Deploy to ECS
```bash
# Create task definition
aws ecs register-task-definition \
  --family datacure-task \
  --container-definitions file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster datacure-cluster \
  --service-name datacure-service \
  --task-definition datacure-task \
  --desired-count 2 \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=backend,containerPort=5000
```

### 5. Setup CloudFront CDN
```bash
# Create distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json
```

### 6. Configure Domain (Route53)
```bash
# Create hosted zone
aws route53 create-hosted-zone --name datacure.hospital --caller-reference 2025-02-28

# Create A record
aws route53 change-resource-record-sets \
  --hosted-zone-id <zone-id> \
  --change-batch file://route53-changes.json
```

---

## Firebase Integration

### Setup Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create new project: "DataCure"
3. Enable following services:
   - Cloud Firestore
   - Cloud Messaging
   - Authentication
   - Cloud Storage

### Configure Backend
```bash
# Download service account key
# Place in: backend/config/firebase-key.json

# Add to .env
FIREBASE_CREDENTIALS_PATH=config/firebase-key.json
FIREBASE_DATABASE_URL=https://datacure.firebaseio.com
FIREBASE_STORAGE_BUCKET=datacure.appspot.com
```

### Create Notification Service
```bash
# File: backend/app/services/notifications.py
from firebase_admin import credentials, db, messaging

class NotificationService:
    def __init__(self):
        cred = credentials.Certificate(config.FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
    
    def send_appointment_reminder(self, patient_id, appointment_id):
        """Send 24-hour appointment reminder"""
        message = messaging.Message(
            notification=messaging.Notification(
                title="Appointment Reminder",
                body="Your appointment is in 24 hours"
            ),
            data={
                "appointment_id": appointment_id,
                "action": "open_appointment"
            },
            token=self.get_device_token(patient_id)
        )
        messaging.send(message)
```

### Test Notification
```bash
curl -X POST http://localhost:5000/api/v1/notifications/test \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-uuid"}'
```

---

## Database Management

### Backup Strategy
```bash
# PostgreSQL backup
pg_dump -h localhost -U datacure datacure_dev > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -h localhost -U datacure datacure_dev < backup_20250228_100000.sql

# AWS RDS backup (automatic)
aws rds create-db-snapshot \
  --db-instance-identifier datacure-prod \
  --db-snapshot-identifier datacure-manual-$(date +%Y%m%d)
```

### Migration Management
```bash
# Create new migration
alembic revision --autogenerate -m "Add new column to users"

# View pending migrations
alembic current
alembic history

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Database Optimization
```bash
# Analyze and vacuum
ANALYZE;
VACUUM ANALYZE;

# Create indexes
CREATE INDEX CONCURRENTLY idx_appointments_date ON appointments(appointment_date);

# Monitor slow queries
SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

---

## Monitoring & Logging

### Application Logs
```bash
# View logs
tail -f /var/log/datacure/app.log

# Search logs
grep "ERROR" /var/log/datacure/app.log
grep "appointment" /var/log/datacure/app.log

# Log rotation configured in docker-compose
# Logs: backend/logs/app.log
```

### CloudWatch Monitoring (AWS)
```bash
# View logs
aws logs tail /aws/ecs/datacure-service --follow

# Create metric alarm
aws cloudwatch put-metric-alarm \
  --alarm-name datacure-cpu-high \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

### Performance Monitoring
```bash
# Check Redis stats
redis-cli INFO stats

# PostgreSQL connections
psql -h localhost -U datacure datacure_dev -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# Application metrics endpoint
curl http://localhost:5000/api/v1/ai/model-metrics
```

---

## Security Checklist

### Pre-Deployment
- [ ] All hardcoded secrets removed from code
- [ ] Environment variables defined in `.env`
- [ ] JWT_SECRET_KEY is strong (min 32 chars random)
- [ ] Database password is strong
- [ ] SSL/TLS certificates obtained
- [ ] CORS origins restricted

### Deployment
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] Security headers set in nginx.conf
  - [ ] Strict-Transport-Security
  - [ ] X-Content-Type-Options
  - [ ] X-Frame-Options
  - [ ] Content-Security-Policy
- [ ] Rate limiting configured (100 req/min API, 10 req/min auth)
- [ ] Database backups scheduled
- [ ] Firewall rules restricted

### Runtime
- [ ] Monitor error logs regularly
- [ ] Review audit logs weekly
- [ ] Update dependencies monthly
- [ ] Test disaster recovery quarterly
- [ ] Rotate SSL certificates before expiry
- [ ] Review access logs for suspicious activity

### Data Protection
- [ ] Patient data encrypted at rest
- [ ] Passwords hashed with bcrypt (12 rounds)
- [ ] Tokens expire (access: 1h, refresh: 7d)
- [ ] Soft deletes enabled (GDPR compliance)
- [ ] Audit trail complete
- [ ] PII not logged

---

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Verify dependencies
pip list | grep -E "Flask|SQLAlchemy"

# Check environment variables
echo $DATABASE_URL
echo $JWT_SECRET_KEY

# Test database connection
psql $DATABASE_URL -c "SELECT 1"
```

### Database Connection Error
```bash
# Check PostgreSQL running
psql -h localhost -U postgres -d template1 -c "SELECT 1"

# Verify DATABASE_URL format
# PostgreSQL: postgresql://user:password@host:port/database

# Test with psycopg2
python -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL')"
```

### Docker Compose Issues
```bash
# Check service status
docker-compose -f docker/docker-compose.yml ps

# View service logs
docker-compose -f docker/docker-compose.yml logs postgres
docker-compose -f docker/docker-compose.yml logs backend

# Restart services
docker-compose -f docker/docker-compose.yml restart backend

# Full rebuild
docker-compose -f docker/docker-compose.yml down -v
docker-compose -f docker/docker-compose.yml up -d
```

### API Returns 401 Unauthorized
```bash
# Verify token generation
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@hospital.com", "password": "pass123"}'

# Use token in header
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/v1/patients

# Check token expiration
python -c "import jwt; jwt.decode('<token>', options={'verify_signature': False})"
```

### High Database Query Time
```bash
# Enable slow query log
ALTER DATABASE datacure_dev SET log_min_duration_statement = 1000;  # 1 second

# View slow queries
SELECT query, calls, total_time, mean_time FROM pg_stat_statements 
WHERE mean_time > 1000 ORDER BY mean_time DESC;

# Add indexes
CREATE INDEX idx_appointments_patient_date ON appointments(patient_id, appointment_date);
```

### Memory Issues
```bash
# Check container limits
docker stats

# Increase memory in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1024M
        reservations:
          memory: 512M

# Restart container
docker-compose -f docker/docker-compose.yml restart backend
```

### SSL Certificate Issues
```bash
# Check certificate expiry
openssl s_client -connect localhost:443 </dev/null | grep -E "notBefore|notAfter"

# Generate self-signed cert (dev only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Verify certificate chain
openssl verify -CAfile ca.pem cert.pem
```

---

## Performance Optimization

### Database
```sql
-- Connection pooling
CREATE EXTENSION pg_stat_statements;

-- Index creation
CREATE INDEX CONCURRENTLY idx_patients_hospital ON patients(hospital_id);
CREATE INDEX CONCURRENTLY idx_appointments_status_date ON appointments(status, appointment_date);

-- Partitioning (large tables)
CREATE TABLE billings_2025 PARTITION OF billings
  FOR VALUES FROM ('2025-01-01') TO ('2025-12-31');
```

### Caching
```python
# Redis caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def get_doctor_list():
    return DoctorRepository.get_all()
```

### API Response
```python
# Pagination limits
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

# Compression
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 512
```

---

**Last Updated**: February 2025
**Version**: 1.0
