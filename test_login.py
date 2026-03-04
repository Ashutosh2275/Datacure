import requests
import json

login_data = {
    "email": "admin@hospital.com",
    "password": "Admin@123"
}

try:
    print("Testing login API endpoint...")
    response = requests.post(
        'http://localhost:5000/api/v1/auth/login',
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Backend server may not be running on port 5000")
    print(f"Details: {str(e)}")
except Exception as e:
    print(f"Error: {str(e)}")
