# DataCure Hospital Intelligence Platform - Complete API Reference

**API Base URL**: `http://localhost:5000/api/v1`

**Authentication**: JWT Bearer Token in Authorization header

---

## Table of Contents
1. [Authentication](#authentication)
2. [Patients](#patients)
3. [Doctors](#doctors)
4. [Appointments](#appointments)
5. [Prescriptions](#prescriptions)
6. [Billing](#billing)
7. [Inventory](#inventory)
8. [Wards](#wards)
9. [Users](#users)
10. [Medical Records](#medical-records)
11. [Reports & Analytics](#reports--analytics)
12. [AI Predictions](#ai-predictions)
13. [Error Handling](#error-handling)
14. [Rate Limiting](#rate-limiting)

---

## Authentication

### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@hospital.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+91-9876543210",
  "role": "doctor",
  "hospital_id": "hosp-uuid"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": "usr-uuid",
    "email": "user@hospital.com"
  }
}
```

**Status Codes:**
- `201`: User created successfully
- `400`: Invalid input or email already exists
- `422`: Validation error

---

### POST /api/v1/auth/login
Authenticate and get JWT tokens.

**Request Body:**
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
    "expires_in": 900,
    "user": {
      "id": "usr-uuid",
      "email": "user@hospital.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "doctor",
      "hospital_id": "hosp-uuid"
    }
  }
}
```

**Required Headers:**
```
Content-Type: application/json
```

**Status Codes:**
- `200`: Login successful
- `401`: Invalid credentials
- `422`: Validation error

---

### POST /api/v1/auth/refresh
Refresh access token.

**Request Body:**
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
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

**Status Codes:**
- `200`: Token refreshed
- `401`: Invalid refresh token
- `422`: Validation error

---

### POST /api/v1/auth/logout
Logout user (optional, mainly for client-side cleanup).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### POST /api/v1/auth/change-password
Change user password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "CurrentPass123!",
  "new_password": "NewPass456!",
  "confirm_password": "NewPass456!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Status Codes:**
- `200`: Password changed
- `401`: Invalid old password
- `422`: Validation error

---

### GET /api/v1/auth/me
Get current user details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "usr-uuid",
    "email": "user@hospital.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+91-9876543210",
    "role": "doctor",
    "hospital_id": "hosp-uuid",
    "is_active": true,
    "created_at": "2025-02-01T10:30:00Z"
  }
}
```

---

## Patients

### GET /api/v1/patients
List all patients (paginated).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| per_page | integer | 20 | Items per page (max: 100) |
| search | string | - | Search by name or patient ID |
| gender | string | - | Filter by gender (M/F) |
| blood_group | string | - | Filter by blood group |

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "pat-uuid",
      "patient_id_number": "PAT-HOSP-20250228-ABC1",
      "user": {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@hospital.com"
      },
      "date_of_birth": "1985-05-10",
      "gender": "F",
      "blood_group": "O+",
      "weight": 65.0,
      "height": 165,
      "allergies": "Nuts",
      "chronic_conditions": "Asthma",
      "emergency_contact_name": "John Smith",
      "emergency_contact_phone": "+91-9876543210"
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

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `403`: Forbidden

---

### POST /api/v1/patients
Create new patient.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "user_id": "usr-uuid",
  "date_of_birth": "1990-05-15",
  "gender": "M",
  "blood_group": "B+",
  "weight": 75.5,
  "height": 180,
  "allergies": "Penicillin, Sulfa",
  "chronic_conditions": "Diabetes, Hypertension",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+91-9999999999",
  "insurance_provider": "Apollo",
  "insurance_policy_number": "POL123456",
  "insurance_expiry": "2025-12-31"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Patient registered successfully",
  "data": {
    "patient_id": "pat-uuid",
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
    "id": "pat-uuid",
    "patient_id_number": "PAT-HOSP-20250228-ABC1",
    "user": {...},
    "date_of_birth": "1985-05-10",
    "gender": "F",
    "blood_group": "A+",
    "weight": 65.0,
    "height": 165,
    "allergies": "Nuts",
    "chronic_conditions": "Asthma",
    "emergency_contact_name": "John Smith",
    "emergency_contact_phone": "+91-9876543210",
    "insurance_provider": "ICICI",
    "insurance_policy_number": "POL789456",
    "insurance_expiry": "2025-12-31",
    "created_at": "2025-02-01T10:30:00Z"
  }
}
```

---

### PUT /api/v1/patients/{id}
Update patient details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "weight": 70.0,
  "height": 180,
  "allergies": "Updated allergies",
  "chronic_conditions": "Updated conditions"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Patient updated successfully"
}
```

---

### DELETE /api/v1/patients/{id}
Delete patient (soft delete).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Patient deleted successfully"
}
```

---

## Doctors

### GET /api/v1/doctors
List all doctors.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| per_page | integer | 20 | Items per page |
| specialization | string | - | Filter by specialization |
| availability | string | - | Filter by status |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "doc-uuid",
      "user": {
        "first_name": "Dr.",
        "last_name": "Smith",
        "email": "doctor@hospital.com"
      },
      "license_number": "MED123456",
      "specialization": "General Medicine",
      "qualification": "MBBS, MD",
      "experience_years": 8,
      "consultation_fee": 500.0,
      "availability_status": "available"
    }
  ],
  "meta": {...}
}
```

---

### GET /api/v1/doctors/{id}
Get doctor details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "doc-uuid",
    "user": {...},
    "license_number": "MED123456",
    "specialization": "Cardiology",
    "qualification": "MBBS, MD, DM (Cardiology)",
    "experience_years": 15,
    "consultation_fee": 750.0,
    "availability_status": "available"
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

**Request Body:**
```json
{
  "patient_id": "pat-uuid",
  "doctor_id": "doc-uuid",
  "appointment_date": "2025-03-15",
  "start_time": "10:00",
  "end_time": "10:30",
  "appointment_type": "consultation",
  "chief_complaint": "Fever and cough",
  "is_emergency": false,
  "is_telemedicine": false,
  "consultation_room": "Room 201"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Appointment booked successfully",
  "data": {
    "appointment_id": "appt-uuid",
    "appointment_date": "2025-03-15",
    "time": "10:00 - 10:30"
  }
}
```

---

### GET /api/v1/appointments
List appointments.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| per_page | integer | 20 | Items per page |
| patient_id | string | - | Filter by patient |
| doctor_id | string | - | Filter by doctor |
| status | string | - | Filter by status |
| date | string | - | Filter by date (YYYY-MM-DD) |

**Status Values**: `scheduled`, `confirmed`, `completed`, `cancelled`, `no_show`, `rescheduled`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "appt-uuid",
      "patient_id": "pat-uuid",
      "doctor_id": "doc-uuid",
      "appointment_date": "2025-03-15",
      "start_time": "10:00:00",
      "end_time": "10:30:00",
      "status": "scheduled",
      "appointment_type": "consultation",
      "chief_complaint": "Fever and cough",
      "is_emergency": false,
      "is_telemedicine": false,
      "consultation_room": "Room 201",
      "no_show_prediction_score": 0.15
    }
  ],
  "meta": {...}
}
```

---

### PUT /api/v1/appointments/{id}
Update appointment.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "status": "confirmed",
  "chief_complaint": "Updated complaint",
  "notes": "Updated notes"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Appointment updated successfully"
}
```

---

### PUT /api/v1/appointments/{id}/reschedule
Reschedule appointment.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
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

### DELETE /api/v1/appointments/{id}
Cancel appointment.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Appointment cancelled successfully"
}
```

---

## Prescriptions

### GET /api/v1/prescriptions
List prescriptions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number
- `per_page`: Items per page
- `patient_id`: Filter by patient
- `doctor_id`: Filter by doctor
- `status`: Filter by status

**Status Values**: `issued`, `dispensed`, `completed`, `cancelled`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "presc-uuid",
      "prescription_number": "RX001",
      "patient_id": "pat-uuid",
      "doctor_id": "doc-uuid",
      "appointment_id": "appt-uuid",
      "status": "issued",
      "notes": "Take after food",
      "expiry_date": "2025-03-28",
      "created_at": "2025-02-28T10:00:00Z",
      "prescription_items": [
        {
          "id": "item-uuid",
          "medicine_id": "med-uuid",
          "medicine_name": "Paracetamol",
          "dosage": "500mg",
          "frequency": "Twice a day",
          "duration": "7 days",
          "quantity": 14
        }
      ]
    }
  ],
  "meta": {...}
}
```

---

### POST /api/v1/prescriptions
Create prescription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "appointment_id": "appt-uuid",
  "patient_id": "pat-uuid",
  "doctor_id": "doc-uuid",
  "notes": "Take after food",
  "items": [
    {
      "medicine_id": "med-uuid",
      "dosage": "500mg",
      "frequency": "Twice a day",
      "duration": "7 days",
      "quantity": 14
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Prescription created successfully",
  "data": {
    "prescription_id": "presc-uuid",
    "prescription_number": "RX001"
  }
}
```

---

### PUT /api/v1/prescriptions/{id}
Update prescription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "status": "dispensed",
  "notes": "Updated notes"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Prescription updated successfully"
}
```

---

### DELETE /api/v1/prescriptions/{id}
Delete prescription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Prescription deleted successfully"
}
```

---

## Billing

### GET /api/v1/billing
List invoices.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number
- `per_page`: Items per page
- `patient_id`: Filter by patient
- `status`: Filter by status
- `from_date`: Filter from date
- `to_date`: Filter to date

**Status Values**: `pending`, `paid`, `partial`, `refunded`, `cancelled`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "bill-uuid",
      "invoice_number": "INV001",
      "patient_id": "pat-uuid",
      "invoice_date": "2025-02-28",
      "amount_due": 2500.0,
      "amount_paid": 2500.0,
      "status": "paid",
      "payment_date": "2025-02-28",
      "description": "Consultation and Medicine"
    }
  ],
  "meta": {...}
}
```

---

### POST /api/v1/billing
Create invoice.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "patient_id": "pat-uuid",
  "amount_due": 5000.0,
  "description": "Lab Tests and Consultation",
  "items": [
    {
      "description": "Consultation Fee",
      "amount": 500.0
    },
    {
      "description": "Lab Tests",
      "amount": 4500.0
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Invoice created successfully",
  "data": {
    "invoice_id": "bill-uuid",
    "invoice_number": "INV002"
  }
}
```

---

### PUT /api/v1/billing/{id}
Update invoice.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "status": "paid",
  "amount_paid": 2500.0,
  "payment_date": "2025-02-28"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Invoice updated successfully"
}
```

---

### DELETE /api/v1/billing/{id}
Delete invoice.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Invoice deleted successfully"
}
```

---

## Inventory

### GET /api/v1/inventory
List medicines.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number
- `per_page`: Items per page
- `search`: Search by name
- `low_stock`: Show only low stock items

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "med-uuid",
      "medicine_name": "Paracetamol",
      "generic_name": "Acetaminophen",
      "dosage": "500mg",
      "quantity_in_stock": 500,
      "reorder_level": 100,
      "unit_price": 10.0,
      "manufacturer": "ABC Pharma",
      "batch_number": "BATCH001",
      "expiry_date": "2025-12-31",
      "storage_location": "Cabinet A1",
      "is_low_stock": false
    }
  ],
  "meta": {...}
}
```

---

### POST /api/v1/inventory
Add medicine to inventory.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "medicine_name": "Amoxicillin",
  "generic_name": "Amoxicillin Trihydrate",
  "dosage": "250mg",
  "quantity_in_stock": 300,
  "reorder_level": 50,
  "unit_price": 15.0,
  "manufacturer": "XYZ Pharma",
  "batch_number": "BATCH002",
  "expiry_date": "2025-11-30",
  "storage_location": "Cabinet B2"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Medicine added successfully",
  "data": {
    "medicine_id": "med-uuid"
  }
}
```

---

### PUT /api/v1/inventory/{id}
Update medicine details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "quantity_in_stock": 250,
  "reorder_level": 60,
  "unit_price": 12.0
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Medicine updated successfully"
}
```

---

### DELETE /api/v1/inventory/{id}
Delete medicine.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Medicine deleted successfully"
}
```

---

## Wards

### GET /api/v1/wards
List wards.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number
- `per_page`: Items per page
- `ward_type`: Filter by type

**Ward Types**: `general`, `icu`, `pediatrics`, `maternity`, `surgery`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "ward-uuid",
      "name": "General Ward",
      "ward_type": "general",
      "floor": "1",
      "total_beds": 20,
      "available_beds": 15,
      "head_nurse": "Sarah Williams"
    }
  ],
  "meta": {...}
}
```

---

### POST /api/v1/wards
Create ward.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "ICU Ward",
  "ward_type": "icu",
  "floor": "2",
  "total_beds": 10,
  "available_beds": 7,
  "head_nurse": "Michael Brown"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Ward created successfully",
  "data": {
    "ward_id": "ward-uuid"
  }
}
```

---

### PUT /api/v1/wards/{id}
Update ward.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "available_beds": 8,
  "head_nurse": "NewNurseName"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Ward updated successfully"
}
```

---

### DELETE /api/v1/wards/{id}
Delete ward.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Ward deleted successfully"
}
```

---

## Users

### GET /api/v1/users
List all users (Admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number
- `per_page`: Items per page
- `role`: Filter by role
- `is_active`: Filter by active status

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "usr-uuid",
      "email": "user@hospital.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+91-9876543210",
      "role": "doctor",
      "is_active": true,
      "created_at": "2025-02-01T10:30:00Z"
    }
  ],
  "meta": {...}
}
```

---

### POST /api/v1/users
Create user (Admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newuser@hospital.com",
  "password": "SecurePass123!",
  "first_name": "New",
  "last_name": "User",
  "phone": "+91-9876543210",
  "role": "doctor"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user_id": "usr-uuid"
  }
}
```

---

### PUT /api/v1/users/{id}
Update user (Admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User updated successfully"
}
```

---

### DELETE /api/v1/users/{id}
Delete user (Admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## Medical Records

### GET /api/v1/medical-records
List medical records.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `patient_id`: Filter by patient
- `doctor_id`: Filter by doctor
- `record_type`: Filter by type

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "record-uuid",
      "patient_id": "pat-uuid",
      "doctor_id": "doc-uuid",
      "record_type": "lab_report",
      "description": "Blood test results",
      "file_url": "https://...",
      "diagnosis": "Normal",
      "notes": "All values within normal range",
      "created_at": "2025-02-28T10:00:00Z"
    }
  ],
  "meta": {...}
}
```

---

### POST /api/v1/medical-records
Create medical record.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (multipart/form-data):**
```
patient_id: pat-uuid
doctor_id: doc-uuid
record_type: lab_report
description: Blood test results
diagnosis: Normal
notes: All values within normal range
file: <file_upload>
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Medical record created successfully",
  "data": {
    "record_id": "record-uuid"
  }
}
```

---

## Reports & Analytics

### GET /api/v1/reports/hospital-statistics
Get hospital statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_patients": 150,
    "total_appointments_month": 450,
    "total_revenue_month": 225000.0,
    "average_patient_satisfaction": 4.5,
    "bed_occupancy_rate": 75.0
  }
}
```

---

### GET /api/v1/reports/daily-statistics
Get daily statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "date": "2025-02-28",
    "appointments_today": 45,
    "new_patients": 5,
    "completed_appointments": 42,
    "cancelled_appointments": 3,
    "revenue_today": 25000.0
  }
}
```

---

## AI Predictions

### POST /api/v1/ai/predict/readmission
Predict patient readmission risk.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "patient_id": "pat-uuid"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "prediction_type": "readmission_risk",
    "patient_id": "pat-uuid",
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

**Risk Levels:**
- `low` (0.0-0.3): Monitor routinely
- `medium` (0.31-0.7): Increased monitoring recommended
- `high` (0.71-1.0): Immediate intervention needed

---

### POST /api/v1/ai/predict/no-show
Predict no-show probability.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
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

**Headers:**
```
Authorization: Bearer <access_token>
```

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

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Permission denied |
| `CONFLICT` | 409 | Resource conflict |
| `INTERNAL_ERROR` | 500 | Server error |
| `DUPLICATE_ENTRY` | 400 | Resource already exists |
| `INVALID_TOKEN` | 401 | Invalid JWT token |
| `EXPIRED_TOKEN` | 401 | JWT token expired |
| `RATE_LIMITED` | 429 | Too many requests |

### Example Error Response

```json
{
  "success": false,
  "message": "Email already exists in the system",
  "error_code": "DUPLICATE_ENTRY",
  "details": {
    "field": "email",
    "value": "user@hospital.com"
  }
}
```

---

## Rate Limiting

Rate limits are applied per endpoint type:

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 10 | 1 minute |
| API (reads) | 100 | 1 minute |
| API (writes) | 50 | 1 minute |
| File upload | 10 | 1 minute |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1645962000
```

When rate limited, response:
```json
{
  "success": false,
  "message": "API rate limit exceeded",
  "error_code": "RATE_LIMITED",
  "details": {
    "retry_after": 30
  }
}
```

---

## Pagination

All list endpoints support pagination:

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

## Response Time SLA

Target response times:

| Operation | Target |
|-----------|--------|
| Simple reads | < 100ms |
| List endpoints | < 500ms |
| Complex queries | < 1000ms |
| AI predictions | < 2000ms |
| File uploads | < 5000ms |

---

**Last Updated**: March 2025
**API Version**: 1.0.0
**Contact**: api-support@datacure.com
