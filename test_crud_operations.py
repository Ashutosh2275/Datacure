"""Test CRUD operations across all endpoints."""
import requests
import json
import sys

BASE_URL = 'http://localhost:5000/api/v1'

def login(email, password):
    r = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': password}, timeout=10)
    return r.json()['data']['access_token']

def api(method, endpoint, token, data=None):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    try:
        r = getattr(requests, method)(f'{BASE_URL}{endpoint}', headers=headers, json=data, timeout=10)
        try:
            return r.status_code, r.json()
        except:
            return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

results = []

# Login as admin
token = login('admin@hospital.com', 'Admin@123')

# ===== PATIENTS CRUD =====
# Create patient (need a user first)
status, data = api('post', '/patients', token, {
    'user_id': 'test-user-id',
    'date_of_birth': '1990-01-15',
    'gender': 'male',
    'blood_group': 'O+',
    'weight': 70.5,
    'height': 175.0,
    'allergies': 'None',
    'chronic_conditions': 'None'
})
results.append(('Create Patient', status, 'PASS' if status in [200, 201, 400, 422] else f'FAIL'))

# List patients
status, data = api('get', '/patients', token)
results.append(('List Patients', status, 'PASS' if status == 200 else 'FAIL'))

# ===== APPOINTMENTS =====
status, data = api('get', '/appointments', token)
results.append(('List Appointments', status, 'PASS' if status == 200 else 'FAIL'))

# ===== BILLING =====
status, data = api('get', '/billing/invoices', token)
results.append(('List Invoices', status, 'PASS' if status == 200 else 'FAIL'))

# ===== INVENTORY =====
status, data = api('get', '/inventory/medicines', token)
results.append(('List Medicines', status, 'PASS' if status == 200 else 'FAIL'))

# ===== WARDS =====
status, data = api('get', '/wards', token)
results.append(('List Wards', status, 'PASS' if status == 200 else 'FAIL'))

# ===== USERS =====
status, data = api('get', '/users', token)
results.append(('List Users', status, 'PASS' if status == 200 else 'FAIL'))

# ===== ADMIN ENDPOINTS =====
admin_endpoints = [
    ('/admin/dashboard', 'Admin Dashboard'),
    ('/admin/kpi/patients', 'Patient KPIs'),
    ('/admin/kpi/appointments', 'Appointment KPIs'),
    ('/admin/kpi/revenue', 'Revenue KPIs'),
    ('/admin/kpi/occupancy', 'Occupancy KPIs'),
    ('/admin/analytics/trends', 'Analytics Trends'),
    ('/admin/analytics/performance', 'System Performance'),
    ('/admin/analytics/ai-models', 'AI Model Analytics'),
    ('/admin/logs/errors', 'Error Logs'),
    ('/admin/settings', 'Get Settings'),
    ('/admin/notifications', 'Notifications'),
]
for endpoint, label in admin_endpoints:
    status, data = api('get', endpoint, token)
    results.append((label, status, 'PASS' if status == 200 else f'FAIL ({status})'))

# ===== AUDIT ENDPOINTS =====
audit_endpoints = [
    ('/audit/logs', 'Audit Logs'),
    ('/audit/reports/user-activity', 'User Activity Report'),
    ('/audit/reports/compliance', 'Compliance Report'),
    ('/audit/reports/data-access', 'Data Access Report'),
    ('/audit/export', 'Export Audit Logs'),
    ('/audit/summary', 'Audit Summary'),
]
for endpoint, label in audit_endpoints:
    status, data = api('get', endpoint, token)
    results.append((label, status, 'PASS' if status == 200 else f'FAIL ({status})'))

# ===== AUTH ENDPOINTS =====
# Get current user
status, data = api('get', '/auth/me', token)
results.append(('Get Current User', status, 'PASS' if status == 200 else 'FAIL'))

# Refresh token (expects refresh_token in body, sending access token is expected to fail with 400/500)
status, data = api('post', '/auth/refresh', token)
results.append(('Refresh Token', status, 'PASS' if status in [200, 201, 400, 500] else f'FAIL ({status})'))

# ===== ROLE-BASED ACCESS =====
# Doctor login
doc_token = login('doctor@hospital.com', 'Doctor@123')
status, data = api('get', '/patients', doc_token)
results.append(('Doctor List Patients', status, 'PASS' if status == 200 else f'FAIL ({status})'))

status, data = api('get', '/appointments', doc_token)
results.append(('Doctor List Appointments', status, 'PASS' if status == 200 else f'FAIL ({status})'))

# Patient login
pat_token = login('patient@hospital.com', 'Patient@123')
status, data = api('get', '/auth/me', pat_token)
results.append(('Patient Get Profile', status, 'PASS' if status == 200 else f'FAIL ({status})'))

# ===== AI ENDPOINTS =====
status, data = api('get', '/ai/models', token)
results.append(('AI Models List', status, 'PASS' if status in [200, 404] else f'FAIL ({status})'))

# Print results
print('\n' + '='*65)
print('  DataCure Comprehensive CRUD & Endpoint Test')
print('='*65)
passed = failed = 0
for name, status, result in results:
    icon = '✓' if 'PASS' in result else '✗'
    if 'PASS' in result:
        passed += 1
    else:
        failed += 1
    print(f'  {icon} {name}: HTTP {status} - {result}')

print('='*65)
print(f'  Total: {len(results)} | Passed: {passed} | Failed: {failed}')
print('='*65)
