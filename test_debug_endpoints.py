"""Detailed debug test for failing endpoints."""
import requests
import json

BASE_URL = 'http://localhost:5000/api/v1'

# Login as admin
response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'admin@hospital.com', 'password': 'Admin@123'
}, headers={'Content-Type': 'application/json'})
token = response.json()['data']['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

endpoints = [
    ('GET', '/patients'),
    ('GET', '/appointments'),
    ('GET', '/billing/invoices'),
    ('GET', '/inventory/medicines'),
    ('GET', '/wards'),
    ('GET', '/users'),
]

for method, endpoint in endpoints:
    try:
        resp = requests.request(method, f'{BASE_URL}{endpoint}', headers=headers, timeout=5)
        print(f'{method} {endpoint}: Status {resp.status_code}')
        if resp.status_code != 200:
            try:
                print(f'  Response: {resp.json()}')
            except:
                print(f'  Response text: {resp.text[:200]}')
        else:
            data = resp.json()
            print(f'  Success: {json.dumps(data, indent=2)[:200]}')
    except Exception as e:
        print(f'{method} {endpoint}: ERROR: {e}')
    print()
