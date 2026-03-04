"""Full end-to-end test of the DataCure application."""
import requests
import json
import sys

BASE_URL = 'http://localhost:5000/api/v1'

def test_cors_preflight():
    """Test CORS preflight from localhost:3000"""
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
    }
    response = requests.options(f'{BASE_URL}/auth/login', headers=headers, timeout=5)
    cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
    assert response.status_code == 200, f'Preflight failed: {response.status_code}'
    assert 'http://localhost:3000' in cors_origin, f'CORS origin missing: {cors_origin}'
    return True

def test_login(email, password, role):
    """Test login for a specific user."""
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': email, 'password': password
    }, headers={'Content-Type': 'application/json'}, timeout=5)
    assert response.status_code == 200, f'Login failed ({email}): {response.status_code} - {response.text}'
    data = response.json()
    assert data['success'], f'Login response not successful: {data}'
    user = data['data']['user']
    assert user['role'] == role, f'Expected role {role}, got {user["role"]}'
    return data['data']['access_token']

def test_authenticated_endpoint(token, endpoint, label):
    """Test an authenticated endpoint."""
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response = requests.get(f'{BASE_URL}{endpoint}', headers=headers, timeout=5)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def test_health():
    """Test health endpoint."""
    response = requests.get('http://localhost:5000/health', timeout=5)
    assert response.status_code == 200
    return True

results = []

# Test 1: Health check
try:
    test_health()
    results.append(('Health Check', 'PASS'))
except Exception as e:
    results.append(('Health Check', f'FAIL: {e}'))

# Test 2: CORS Preflight
try:
    test_cors_preflight()
    results.append(('CORS Preflight (localhost:3000)', 'PASS'))
except Exception as e:
    results.append(('CORS Preflight (localhost:3000)', f'FAIL: {e}'))

# Test 3: Admin Login
admin_token = None
try:
    admin_token = test_login('admin@hospital.com', 'Admin@123', 'admin')
    results.append(('Admin Login', 'PASS'))
except Exception as e:
    results.append(('Admin Login', f'FAIL: {e}'))

# Test 4: Doctor Login
doctor_token = None
try:
    doctor_token = test_login('doctor@hospital.com', 'Doctor@123', 'doctor')
    results.append(('Doctor Login', 'PASS'))
except Exception as e:
    results.append(('Doctor Login', f'FAIL: {e}'))

# Test 5: Patient Login
patient_token = None
try:
    patient_token = test_login('patient@hospital.com', 'Patient@123', 'patient')
    results.append(('Patient Login', 'PASS'))
except Exception as e:
    results.append(('Patient Login', f'FAIL: {e}'))

# Test 6-15: Authenticated endpoints (using admin token)
if admin_token:
    endpoints = [
        ('/auth/me', 'Get Current User'),
        ('/patients', 'List Patients'),
        ('/appointments', 'List Appointments'),
        ('/billing/invoices', 'List Invoices'),
        ('/inventory/medicines', 'List Medicines'),
        ('/wards', 'List Wards'),
        ('/users', 'List Users'),
        ('/admin/dashboard', 'Admin Dashboard'),
        ('/audit/logs', 'Audit Logs'),
    ]
    for endpoint, label in endpoints:
        try:
            status, data = test_authenticated_endpoint(admin_token, endpoint, label)
            if status == 200:
                results.append((label, 'PASS'))
            elif status == 404:
                results.append((label, f'WARN: 404 (endpoint may not exist)'))
            else:
                results.append((label, f'FAIL: Status {status}'))
        except Exception as e:
            results.append((label, f'FAIL: {e}'))

# Print results
print('\n' + '='*60)
print('  DataCure Full System Test Results')
print('='*60)
passed = 0
failed = 0
warnings = 0
for test_name, result in results:
    if result == 'PASS':
        icon = '✓'
        passed += 1
    elif result.startswith('WARN'):
        icon = '⚠'
        warnings += 1
    else:
        icon = '✗'
        failed += 1
    print(f'  {icon} {test_name}: {result}')

print('='*60)
print(f'  Total: {len(results)} | Passed: {passed} | Failed: {failed} | Warnings: {warnings}')
print('='*60)

if failed > 0:
    sys.exit(1)
