# DataCure - Getting Started Guide

## Quick Start

This guide will help you get the DataCure Hospital Intelligence Platform up and running.

---

## Prerequisites

### Required
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Git

### Optional
- Docker & Docker Compose
- Postman (for API testing)
- VS Code or any IDE

---

## Backend Setup

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb datacure

# Or using PostgreSQL client:
psql -U postgres
CREATE DATABASE datacure;
```

### 3. Environment Configuration

Create `.env` file in backend directory:

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/datacure
SQLALCHEMY_TRACK_MODIFICATIONS=false

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost

# Firebase (optional)
FIREBASE_API_KEY=your-firebase-key
FIREBASE_PROJECT_ID=your-project-id

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-app-password
```

### 4. Database Initialization

```bash
# Create all tables
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()

# Or using Flask CLI
flask db upgrade  # if using migrations
```

### 5. Run Backend Server

```bash
# Development server
python app.py

# Server will run on http://localhost:5000
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend

npm install
```

### 2. Environment Configuration

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:5000/api/v1
VITE_ENV=development
```

### 3. Run Development Server

```bash
npm run dev

# Server will run on http://localhost:3000
```

### 4. Build for Production

```bash
npm run build

# Output in dist/ directory
```

---

## Testing the Application

### 1. Open Application

Open browser and navigate to:
```
http://localhost:3000
```

### 2. Login Credentials

**Admin Account**:
```
Email: admin@hospital.com
Password: Admin@123
```

**Doctor Account**:
```
Email: doctor@hospital.com
Password: Doctor@123
```

**Patient Account**:
```
Email: patient@hospital.com
Password: Patient@123
```

### 3. Verify Features

- Login with credentials
- View dashboard
- Navigate to different sections
- Create and manage records
- Check API calls in browser network tab

---

## Docker Setup (Optional)

### Prerequisites
- Docker
- Docker Compose

### Run with Docker Compose

```bash
# From project root
docker-compose up -d

# Services will start:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:5000
# - Database: localhost:5432
```

### Stop Services

```bash
docker-compose down
```

---

## API Testing

### Using Postman

1. Open Postman
2. Import API collection from `backend/docs/datacure-api.postman_collection.json`
3. Set environment variables:
   - `api_url`: http://localhost:5000/api/v1
   - `token`: (auto-populated after login)
4. Start testing endpoints

### Using cURL

```bash
# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hospital.com","password":"Admin@123"}'

# Get token from response
TOKEN="your-access-token"

# Get patients
curl -X GET http://localhost:5000/api/v1/patients \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### Backend Issues

**Port 5000 already in use**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

**Database connection error**:
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Check database credentials

**Module not found**:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend Issues

**API connection error**:
- Check backend is running on port 5000
- Verify VITE_API_URL in .env
- Check CORS configuration in backend

**Node modules issues**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Project Structure

### Backend
```
backend/
├── app/
│   ├── __init__.py      # App factory
│   ├── models/          # Database models
│   ├── schemas/         # Marshmallow schemas
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── repositories/    # Data access
│   ├── utils/           # Utilities
│   └── extensions/      # Flask extensions
├── migrations/          # Database migrations
├── tests/               # Test files
├── config.py            # Configuration
├── requirements.txt     # Dependencies
└── app.py              # Entry point
```

### Frontend
```
frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── store/           # Zustand stores
│   ├── utils/           # Helper functions
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── public/              # Static assets
├── package.json
└── vite.config.js
```

---

## Development Workflow

### 1. Start Services

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2. Make Changes

Edit files in either backend or frontend directories

### 3. Test Changes

- Backend: Changes auto-reload with Flask
- Frontend: Changes auto-reload with Vite

### 4. Commit Changes

```bash
git add .
git commit -m "Description of changes"
git push
```

---

## Useful Commands

### Backend

```bash
# Run tests
pytest

# Run with different environment
FLASK_ENV=production python app.py

# Database migrations
flask db migrate -m "Migration name"
flask db upgrade
flask db downgrade

# Seed database
python -m flask seed-db
```

### Frontend

```bash
# Lint code
npm run lint
npm run lint:fix

# Format code
npm run format

# Type checking (if using TypeScript)
npm run typecheck
```

---

## Common Ports

| Service | Port | URL |
|---------|------|-----|
| Backend API | 5000 | http://localhost:5000 |
| Frontend React | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | localhost:5432 |
| Nginx (with Docker) | 80/443 | http://localhost |

---

## Documentation

- **API Documentation**: See `backend/docs/API.md`
- **Architecture**: See `backend/docs/ARCHITECTURE.md`
- **Database Schema**: See `backend/docs/DATABASE_SCHEMA.md`
- **Frontend README**: See `frontend/README.md`
- **Deployment**: See `backend/docs/DEPLOYMENT.md`

---

## Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Review error messages in console/logs
3. Check browser network tab for API errors
4. Review database logs for data issues

---

## Next Steps

1. Complete the setup steps above
2. Test with provided credentials
3. Explore the application
4. Review codebase structure
5. Start development/customization

---

**Happy coding! 🚀**
