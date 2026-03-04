"""Test to see exactly what happens when hospital_isolated reads request.json on GET."""
import requests

BASE_URL = 'http://localhost:5000/api/v1'

# Login
response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'admin@hospital.com', 'password': 'Admin@123'
}, headers={'Content-Type': 'application/json'})
token = response.json()['data']['access_token']

# Test with no Content-Type header (pure GET)
headers_no_ct = {'Authorization': f'Bearer {token}'}
resp = requests.get(f'{BASE_URL}/patients', headers=headers_no_ct, timeout=5)
print(f'Without Content-Type -> Status {resp.status_code}: {resp.text[:200]}')

# Test with Content-Type but no body
headers_with_ct = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
resp = requests.get(f'{BASE_URL}/patients', headers=headers_with_ct, timeout=5)
print(f'With Content-Type    -> Status {resp.status_code}: {resp.text[:200]}')
