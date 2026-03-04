#!/usr/bin/env python
import requests

base_url = 'http://localhost:5000/api/v1'
headers = {'Content-Type': 'application/json', 'Origin': 'http://localhost:3001'}
login_data = {'email': 'admin@hospital.com', 'password': 'Admin@123'}

response = requests.post(base_url + '/auth/login', json=login_data, headers=headers)
print('Login Status:', response.status_code)

if response.status_code == 200:
    data = response.json()
    user_email = data['data']['user']['email']
    user_role = data['data']['user']['role']
    token = data['data']['access_token'][:30] + '...'
    print('\n✓ SUCCESS!')
    print('  Email:', user_email)
    print('  Role:', user_role)
    print('  Token:', token)
    print('\nCORS is now working correctly!')
else:
    print('✗ Error:', response.text)
