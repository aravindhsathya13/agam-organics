"""
Test authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test signup
print("Testing Signup...")
signup_data = {
    "email": "testuser123@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "phone": "9876543210"
}

response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 201:
    print("✅ Signup successful!")
    tokens = response.json()
    
    # Test login
    print("\nTesting Login...")
    login_data = {
        "email": "testuser123@example.com",
        "password": "SecurePass123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
else:
    print(f"❌ Signup failed: {response.json()}")
