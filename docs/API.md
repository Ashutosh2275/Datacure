# DataCure - Complete API Documentation

## Authentication Endpoints

### POST /api/v1/auth/register
Register new user in the system.

**Request:**
```json
{
  "email": "user@hospital.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "doctor",
  "hospital_id": "hosp-uuid",
  "phone": "+91-9876543210"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "message": "User registered successfully",
    "user_id": "user-uuid",
    "email": "user@hospital.com"
  }
}
```

**Status Codes:**
- 201: User created successfully
- 400: Invalid input or email already exists
- 422: Validation error

---

### POST /api/v1/auth/login
Authenticate user and get JWT tokens.

**Request:**
```json
{
  "email": "user@hospital.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "user": {
      "id": "user-uuid",
      "email": "user@hospital.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "doctor",
      "hospital_id": "hosp-uuid"
    }
  }
}
```

**Status Codes:**
- 200: Login successful
- 401: Invalid credentials
- 422: Validation error

---

### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer"
  }
}
```

---

### POST /api/v1/auth/change-password
Change password for authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "old_password": "CurrentPass123!",
  "new_password": "NewPass456!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## Patient Management

### GET /api/v1/patients
Get all patients in hospital with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "patient-uuid",
      "patient_id_number": "PAT-HOSP-20250228-ABC1",
      "first_name": "Jane",
      "last_name": "Smith",
      "gender": "F",
      "date_of_birth": "1985-05-10",
      "blood_group": "O+"
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 20,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### POST /api/v1/patients
Create new patient.

**Headers:**
```
Authorization: Bearer <access_token>
Role: admin, doctor
```

**Request:**
```json
{
  "user_id": "user-uuid",
  "date_of_birth": "1990-05-15",
  "gender": "M",
  "blood_group": "B+",
  "weight": 75.5,
  "height": 180,
  "allergies": "Penicillin, Sulfa",
  "chronic_conditions": "Diabetes, Hypertension",
  "insurance_provider": "Apollo",
  "insurance_policy_number": "POL123456"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Patient registered successfully",
  "data": {
    "message": "Patient registered successfully",
    "patient_id": "patient-uuid",
    "patient_id_number": "PAT-HOSP-20250228-XYZ5"
  }
}
```

---

### GET /api/v1/patients/{id}
Get patient details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "patient-uuid",
    "patient_id_number": "PAT-HOSP-20250228-ABC1",
    "date_of_birth": "1985-05-10",
    "gender": "F",
    "blood_group": "A+",
    "weight": 65.0,
    "height": 165,
    "user": {...},
    "allergies": "Nuts",
    "chronic_conditions": "Asthma",
    "insurance_provider": "ICICI",
    "insurance_policy_number": "POL789456"
  }
}
```

---

## Appointments

### POST /api/v1/appointments
Book new appointment.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "patient_id": "patient-uuid",
  "doctor_id": "doctor-uuid",
  "appointment_date": "2025-03-15",
  "start_time": "10:00",
  "end_time": "10:30",
  "appointment_type": "consultation",
  "chief_complaint": "Fever and cough",
  "is_emergency": false,
  "is_telemedicine": false
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Appointment booked successfully",
  "data": {
    "message": "Appointment booked successfully",
    "appointment_id": "appt-uuid",
    "appointment_date": "2025-03-15",
    "time": "10:00 - 10:30"
  }
}
```

---

### GET /api/v1/appointments
List appointments with filters.

**Query Parameters:**
- `patient_id`: Filter by patient
- `doctor_id`: Filter by doctor
- `status`: Filter by status (scheduled, confirmed, completed, cancelled)
- `date`: Filter by date (YYYY-MM-DD)
- `page`: Page number
- `per_page`: Items per page

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "appt-uuid",
      "patient_id": "patient-uuid",
      "doctor_id": "doctor-uuid",
      "appointment_date": "2025-03-15",
      "start_time": "10:00:00",
      "status": "scheduled",
      "is_emergency": false,
      "no_show_prediction_score": 0.15
    }
  ],
  "meta": {...}
}
```

---

### PUT /api/v1/appointments/{id}/reschedule
Reschedule appointment.

**Request:**
```json
{
  "appointment_date": "2025-03-20",
  "start_time": "14:00",
  "end_time": "14:30"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Appointment rescheduled successfully"
}
```

---

## AI Predictions

### POST /api/v1/ai/predict/readmission
Predict readmission risk.

**Headers:**
```
Authorization: Bearer <access_token>
Role: admin, doctor
```

**Request:**
```json
{
  "patient_id": "patient-uuid"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "prediction_type": "readmission_risk",
    "patient_id": "patient-uuid",
    "risk_score": 0.62,
    "risk_level": "medium",
    "confidence": 0.85,
    "explanation": {
      "age_group": "normal",
      "chronic_conditions": "Diabetes",
      "recent_visits": 3
    }
  }
}
```

### Risk Levels:
- **low** (0.0-0.3): Monitor routinely
- **medium** (0.31-0.7): Increased monitoring recommended
- **high** (0.71-1.0): Immediate intervention needed

---

### POST /api/v1/ai/predict/no-show
Predict no-show probability.

**Request:**
```json
{
  "appointment_id": "appt-uuid"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "prediction_type": "no_show",
    "appointment_id": "appt-uuid",
    "risk_score": 0.25,
    "risk_level": "low",
    "explanation": {
      "days_until_appointment": 5,
      "patient_no_show_rate": 8.5,
      "previous_no_shows": 1
    }
  }
}
```

---

### GET /api/v1/ai/forecast/patient-flow
Forecast patient flow.

**Query Parameters:**
- `days`: Days to forecast (1-30, default: 7)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "forecast_type": "patient_flow",
    "hospital_id": "hosp-uuid",
    "forecast_period": "Next 7 days",
    "average_daily": 45,
    "predictions": [
      {
        "date": "2025-02-28",
        "predicted_appointments": 48,
        "confidence": 0.75
      },
      {
        "date": "2025-03-01",
        "predicted_appointments": 52,
        "confidence": 0.72
      }
    ]
  }
}
```

---

## Error Responses

All errors follow consistent format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

**Common Error Codes:**
- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Permission denied
- `CONFLICT`: Resource conflict
- `INTERNAL_ERROR`: Server error

---

## Rate Limiting

- **Authentication endpoints**: 10 requests/minute
- **API endpoints**: 100 requests/minute
- **File upload**: 10 requests/minute

Headers returned:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1645962000
```

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1, min: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Response Meta:**
```json
"meta": {
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8,
  "has_next": true,
  "has_prev": false
}
```

---

## Sorting & Filtering

Endpoints support query parameters for filtering and sorting:

**Examples:**
```
GET /api/v1/appointments?status=scheduled&doctor_id=doc-123&page=1

GET /api/v1/patients?specialization=Cardiology&available_only=true
```

---

## Response Time (SLA)

Target response times:
- Simple queries: < 100ms
- List endpoints: < 500ms
- AI predictions: < 2000ms

---

## Clients & SDKs

- REST API: Direct HTTP calls
- JavaScript: Axios/Fetch
- Python: Requests library
- Mobile: Native HTTP clients

---

**Last Updated**: February 2025
**API Version**: 1.0
