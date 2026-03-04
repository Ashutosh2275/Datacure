# DataCure Database Schema

## Overview
Complete relational database schema for Hospital Intelligence Platform with 15+ entities covering patient management, appointments, billing, inventory, AI tracking, and audit logging.

---

## Core Tables

### users
User accounts with role-based access control.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| first_name | VARCHAR(100) | NOT NULL | User first name |
| last_name | VARCHAR(100) | NOT NULL | User last name |
| role | ENUM | NOT NULL | admin, doctor, nurse, reception, patient |
| hospital_id | UUID | FK users→hospitals, NOT NULL | Associated hospital |
| phone | VARCHAR(20) | | Phone number |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| last_login | TIMESTAMP | | Last login timestamp |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |
| deleted_at | TIMESTAMP | | Soft delete marker |

**Indexes:**
- UNIQUE(email, hospital_id)
- INDEX(role), INDEX(is_active)

---

### hospitals
Hospital/clinic organizations.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique hospital ID |
| name | VARCHAR(255) | NOT NULL | Hospital name |
| address | TEXT | NOT NULL | Full address |
| city | VARCHAR(100) | NOT NULL | City |
| state | VARCHAR(100) | NOT NULL | State |
| pincode | VARCHAR(10) | NOT NULL | Postal code |
| country | VARCHAR(100) | DEFAULT 'India' | Country |
| phone | VARCHAR(20) | NOT NULL | Hospital phone |
| email | VARCHAR(255) | | Hospital email |
| gst_number | VARCHAR(20) | UNIQUE | GST registration number |
| license_number | VARCHAR(50) | UNIQUE | Medical license |
| total_beds | INTEGER | | Total beds available |
| established_year | INTEGER | | Year established |
| is_active | BOOLEAN | DEFAULT TRUE | Operations status |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

---

### patients
Patient information and demographics.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique patient ID |
| user_id | UUID | FK patients→users, NOT NULL | Associated user |
| hospital_id | UUID | FK patients→hospitals, NOT NULL | Primary hospital |
| patient_id_number | VARCHAR(50) | UNIQUE, NOT NULL | Hospital patient number |
| date_of_birth | DATE | NOT NULL | Birth date |
| gender | ENUM | NOT NULL | M, F, Other |
| blood_group | VARCHAR(10) | | ABO blood type |
| weight | DECIMAL(5,2) | | Current weight (kg) |
| height | INTEGER | | Height (cm) |
| allergies | TEXT | | Known allergies |
| chronic_conditions | TEXT | | Permanent conditions |
| insurance_provider | VARCHAR(100) | | Insurance company |
| insurance_policy_number | VARCHAR(50) | | Policy number |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- UNIQUE(patient_id_number, hospital_id)
- INDEX(user_id), INDEX(hospital_id)

---

### doctors
Doctor/physician information.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique doctor ID |
| user_id | UUID | FK doctors→users, NOT NULL | Associated user |
| hospital_id | UUID | FK doctors→hospitals, NOT NULL | Primary hospital |
| specialization | VARCHAR(100) | NOT NULL | Medical specialty |
| license_number | VARCHAR(50) | UNIQUE, NOT NULL | Medical license |
| experience_years | INTEGER | | Years of experience |
| consultation_fee | DECIMAL(10,2) | | Consultation charge (INR) |
| availability_start | TIME | | Daily availability start |
| availability_end | TIME | | Daily availability end |
| working_days | VARCHAR(50) | | Comma-separated days |
| is_available | BOOLEAN | DEFAULT TRUE | Currently accepting patients |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- INDEX(hospital_id), INDEX(specialization), INDEX(is_available)

---

### appointments
Appointment scheduling and tracking.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique appointment ID |
| patient_id | UUID | FK appointments→patients, NOT NULL | Patient |
| doctor_id | UUID | FK appointments→doctors, NOT NULL | Doctor |
| hospital_id | UUID | FK appointments→hospitals, NOT NULL | Hospital |
| appointment_date | DATE | NOT NULL | Appointment date |
| start_time | TIME | NOT NULL | Start time |
| end_time | TIME | NOT NULL | End time |
| status | ENUM | DEFAULT 'scheduled' | scheduled, confirmed, completed, cancelled, no_show |
| appointment_type | VARCHAR(50) | | consultation, follow_up, procedure |
| chief_complaint | TEXT | | Patient's reason for visit |
| diagnosis | TEXT | | Doctor's diagnosis |
| notes | TEXT | | Additional notes |
| is_emergency | BOOLEAN | DEFAULT FALSE | Emergency status |
| is_telemedicine | BOOLEAN | DEFAULT FALSE | Virtual appointment |
| no_show_prediction_score | DECIMAL(3,2) | | ML prediction (0-1) |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- INDEX(patient_id), INDEX(doctor_id), INDEX(appointment_date, status)
- INDEX(hospital_id), INDEX(is_emergency)

---

### prescriptions
Medication prescriptions.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique prescription ID |
| appointment_id | UUID | FK prescriptions→appointments | Associated appointment |
| patient_id | UUID | FK prescriptions→patients, NOT NULL | Patient |
| doctor_id | UUID | FK prescriptions→doctors, NOT NULL | Doctor |
| hospital_id | UUID | FK prescriptions→hospitals, NOT NULL | Hospital |
| prescription_number | VARCHAR(50) | UNIQUE, NOT NULL | Unique reference |
| issue_date | DATE | NOT NULL | Issue date |
| validity_until | DATE | NOT NULL | Expiry date |
| status | ENUM | DEFAULT 'active' | active, partially_dispensed, fully_dispensed, cancelled |
| special_instructions | TEXT | | Patient instructions |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- UNIQUE(prescription_number, hospital_id)
- INDEX(patient_id, status), INDEX(appointment_id)

---

### prescription_items
Individual medicines in prescription.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique item ID |
| prescription_id | UUID | FK prescription_items→prescriptions, NOT NULL | Parent prescription |
| medicine_id | UUID | FK prescription_items→medicines, NOT NULL | Medicine |
| quantity | INTEGER | NOT NULL | Quantity prescribed |
| unit | VARCHAR(20) | NOT NULL | mg, tablet, ml, etc. |
| frequency | VARCHAR(50) | NOT NULL | times_daily, times_weekly |
| duration_days | INTEGER | NOT NULL | Days to take |
| dosage_per_dose | DECIMAL(10,2) | | Dose per administration |
| quantity_dispensed | INTEGER | DEFAULT 0 | Already dispensed |
| special_instructions | TEXT | | Special notes |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- INDEX(prescription_id), INDEX(medicine_id)

---

### medicines
Pharmacy medicine master list.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique medicine ID |
| hospital_id | UUID | FK medicines→hospitals, NOT NULL | Hospital |
| name | VARCHAR(255) | NOT NULL | Trade name |
| generic_name | VARCHAR(255) | NOT NULL | Generic name |
| manufacturer | VARCHAR(100) | | Manufacturer |
| strength | VARCHAR(50) | | e.g., 500mg |
| form | VARCHAR(50) | | tablet, capsule, injection, syrup |
| price | DECIMAL(10,2) | NOT NULL | Unit cost (INR) |
| unit | VARCHAR(20) | NOT NULL | tablet, ml, etc. |
| hsn_code | VARCHAR(10) | | GST HSN code |
| gst_percentage | DECIMAL(5,2) | DEFAULT 5 | GST tax percentage |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- UNIQUE(name, hospital_id)
- INDEX(generic_name)

---

### medicine_inventory
Stock tracking for medicines.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique record ID |
| medicine_id | UUID | FK medicine_inventory→medicines, NOT NULL | Medicine |
| hospital_id | UUID | FK medicine_inventory→hospitals, NOT NULL | Hospital |
| batch_number | VARCHAR(50) | NOT NULL | Batch identifier |
| quantity_in_stock | INTEGER | NOT NULL DEFAULT 0 | Current quantity |
| reorder_level | INTEGER | NOT NULL | Minimum level before reorder |
| expiry_date | DATE | NOT NULL | Batch expiry |
| manufacturing_date | DATE | | Manufacturing date |
| supplier_id | UUID | | Supplier reference |
| purchase_price | DECIMAL(10,2) | | Cost per unit |
| last_received_date | DATE | | Last stock addition |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- UNIQUE(medicine_id, batch_number, hospital_id)
- INDEX(expiry_date), INDEX(quantity_in_stock)

---

### billings
Invoice/billing records.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique billing ID |
| invoice_number | VARCHAR(50) | UNIQUE, NOT NULL | Invoice reference |
| patient_id | UUID | FK billings→patients, NOT NULL | Patient |
| hospital_id | UUID | FK billings→hospitals, NOT NULL | Hospital |
| doctor_id | UUID | FK billings→doctors | Attending doctor |
| appointment_id | UUID | FK billings→appointments | Associated appointment |
| billing_date | DATE | NOT NULL | Bill generation date |
| subtotal | DECIMAL(12,2) | NOT NULL | Before tax |
| gst_amount | DECIMAL(12,2) | DEFAULT 0 | Tax amount |
| discount_amount | DECIMAL(12,2) | DEFAULT 0 | Discount applied |
| total_amount | DECIMAL(12,2) | NOT NULL | Final amount |
| amount_paid | DECIMAL(12,2) | DEFAULT 0 | Paid so far |
| balance_due | DECIMAL(12,2) | NOT NULL | Remaining |
| status | ENUM | DEFAULT 'pending' | pending, partial, paid, cancelled |
| payment_method | VARCHAR(50) | | cash, cheque, card, net_banking |
| due_date | DATE | | Payment due date |
| notes | TEXT | | Additional notes |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- UNIQUE(invoice_number, hospital_id)
- INDEX(patient_id, status), INDEX(billing_date)

---

### billing_items
Line items in billing.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique item ID |
| billing_id | UUID | FK billing_items→billings, NOT NULL | Parent billing |
| description | VARCHAR(255) | NOT NULL | Service/item description |
| quantity | DECIMAL(10,2) | NOT NULL | Quantity |
| unit_price | DECIMAL(12,2) | NOT NULL | Price per unit |
| amount | DECIMAL(12,2) | NOT NULL | Total (quantity × price) |
| gst_percentage | DECIMAL(5,2) | DEFAULT 5 | Applicable GST |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- INDEX(billing_id)

---

### wards
Hospital wards/departments.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique ward ID |
| hospital_id | UUID | FK wards→hospitals, NOT NULL | Hospital |
| name | VARCHAR(100) | NOT NULL | Ward name |
| ward_type | VARCHAR(50) | NOT NULL | general, icu, pediatric |
| floor_number | INTEGER | | Floor level |
| total_beds | INTEGER | NOT NULL | Total beds |
| available_beds | INTEGER | NOT NULL | Currently free |
| head_nurse_id | UUID | FK wards→users | Ward head |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- UNIQUE(name, hospital_id)
- INDEX(hospital_id)

---

### beds
Individual bed allocation.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique bed ID |
| ward_id | UUID | FK beds→wards, NOT NULL | Parent ward |
| hospital_id | UUID | FK beds→hospitals, NOT NULL | Hospital |
| bed_number | VARCHAR(20) | NOT NULL | Bed identifier |
| bed_type | VARCHAR(50) | | general, high_dependency, isolation |
| status | ENUM | DEFAULT 'available' | available, occupied, maintenance |
| patient_id | UUID | FK beds→patients | Currently assigned patient |
| admission_date | DATE | | When patient admitted |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- UNIQUE(bed_number, ward_id)
- INDEX(ward_id, status), INDEX(patient_id)

---

## AI/ML Tables

### ai_risk_scores
ML prediction scores for patient risk assessment.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique score ID |
| patient_id | UUID | FK ai_risk_scores→patients, NOT NULL | Patient |
| hospital_id | UUID | FK ai_risk_scores→hospitals, NOT NULL | Hospital |
| risk_type | VARCHAR(50) | NOT NULL | readmission, no_show, mortality |
| risk_score | DECIMAL(3,2) | NOT NULL | Score 0.0-1.0 |
| risk_level | VARCHAR(20) | | low, medium, high |
| confidence | DECIMAL(3,2) | | Model confidence |
| explanation | JSONB | | Feature importance dict |
| is_acknowledged | BOOLEAN | DEFAULT FALSE | Reviewed by doctor |
| acknowledged_by | UUID | FK ai_risk_scores→users | Acknowledging user |
| acknowledged_at | TIMESTAMP | | Review timestamp |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- INDEX(patient_id, risk_type)
- INDEX(hospital_id, created_at)

---

### ai_logs
Audit trail for ML predictions.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique log ID |
| hospital_id | UUID | FK ai_logs→hospitals, NOT NULL | Hospital |
| model_type | VARCHAR(100) | NOT NULL | Model identifier |
| prediction_result | JSONB | NOT NULL | Raw prediction output |
| input_features | JSONB | | Input feature values |
| patient_id | UUID | FK ai_logs→patients | Associated patient |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- INDEX(hospital_id, created_at)
- INDEX(model_type)

---

### model_metrics
Performance tracking for AI models.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique metric ID |
| hospital_id | UUID | FK model_metrics→hospitals, NOT NULL | Hospital |
| model_type | VARCHAR(100) | NOT NULL | Model identifier |
| accuracy | DECIMAL(3,2) | | Classification accuracy |
| precision | DECIMAL(3,2) | | Precision score |
| recall | DECIMAL(3,2) | | Recall score |
| f1_score | DECIMAL(3,2) | | F1 score |
| auc_roc | DECIMAL(3,2) | | AUC-ROC metric |
| total_predictions | INTEGER | | Total predictions made |
| last_trained | TIMESTAMP | | Last training date |
| version | VARCHAR(20) | | Model version |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- UNIQUE(model_type, hospital_id)

---

## Audit & Compliance

### audit_logs
Complete audit trail for compliance.

| Column | Type | Constraints | Description |
|--------|------|-----------|---|
| id | UUID | PRIMARY KEY | Unique log ID |
| hospital_id | UUID | FK audit_logs→hospitals, NOT NULL | Hospital |
| user_id | UUID | FK audit_logs→users | Performing user |
| action | VARCHAR(50) | NOT NULL | create, read, update, delete |
| entity_type | VARCHAR(100) | NOT NULL | Model name |
| entity_id | UUID | | Modified entity |
| changes | JSONB | | Before/after values |
| ip_address | VARCHAR(45) | | Source IP |
| user_agent | TEXT | | Browser/client info |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- INDEX(hospital_id, created_at)
- INDEX(user_id), INDEX(entity_type)

---

## Relationships Summary

```
hospitals 1--* users
hospitals 1--* patients
hospitals 1--* doctors
hospitals 1--* appointments
hospitals 1--* wards
hospitals 1--* medicines
hospitals 1--* billings

users 1--* patients (user_id)
users 1--* doctors (user_id)
users 1--* audit_logs

patients 1--* appointments
patients 1--* prescriptions
patients 1--* billings
patients 1--* ai_risk_scores
patients 1--* beds

doctors 1--* appointments
doctors 1--* prescriptions
doctors 1--* billings

appointments 1--* prescriptions
appointments 1--* billings

prescriptions 1--* prescription_items

medicines 1--* prescription_items
medicines 1--* medicine_inventory

wards 1--* beds

billing_items 1--* billings
```

---

## Enums

### UserRole
- `admin` - System administrator
- `doctor` - Medical doctor
- `nurse` - Registered nurse
- `reception` - Reception staff
- `patient` - Patient user

### AppointmentStatus
- `scheduled` - Initial booking
- `confirmed` - Confirmed by doctor
- `completed` - Completed
- `cancelled` - Cancelled by user
- `no_show` - Patient didn't show

### AppointmentType
- `consultation` - Regular visit
- `follow_up` - Follow-up visit
- `procedure` - Medical procedure

### BillingStatus
- `pending` - Not yet paid
- `partial` - Partially paid
- `paid` - Fully paid
- `cancelled` - Cancelled

### PrescriptionStatus
- `active` - Ongoing
- `partially_dispensed` - Some items dispensed
- `fully_dispensed` - All items dispensed
- `cancelled` - Cancelled

### Gender
- `M` - Male
- `F` - Female
- `Other` - Other

### WardType
- `general` - General ward
- `icu` - Intensive care
- `pediatric` - Children ward

### BedStatus
- `available` - Not occupied
- `occupied` - Patient assigned
- `maintenance` - Under maintenance

---

## Constraints & Rules

1. **Patient ID Number**: Unique format `PAT-{HOSP-CODE}-{DATE}-{RANDOM}`
2. **Invoice Number**: Unique format `INV-{HOSP-CODE}-{DATE}-{SEQUENCE}`
3. **Prescription Number**: Unique format `RX-{HOSP-CODE}-{DATE}-{SEQUENCE}`
4. **Password**: Minimum 8 characters, uppercase, lowercase, digit, special character
5. **Soft Delete**: All entities include `deleted_at` for GDPR compliance
6. **Timestamps**: All entities track `created_at` and `updated_at`
7. **GST**: All medicines have GST, applied on billing
8. **Insurance**: Optional but tracked when available

---

**Last Updated**: February 2025
**Version**: 1.0
**Total Tables**: 18
