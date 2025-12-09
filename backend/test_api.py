"""
Einfaches Python-Script zum Testen der API
Installation: pip install requests
"""
import requests
import json

# API Base URL - anpassen für Produktion
BASE_URL = "https://roboadvisor-frontend-vrpob.ondigitalocean.app"
# Für lokale Tests: BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test Health Check Endpoint"""
    print("=" * 50)
    print("1. Testing Health Check...")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_register(name, email, password):
    """Test User Registration"""
    print("=" * 50)
    print("2. Testing User Registration...")
    print("=" * 50)
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "name": name,
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.status_code == 201

def test_login(email, password):
    """Test User Login"""
    print("=" * 50)
    print("3. Testing User Login...")
    print("=" * 50)
    
    url = f"{BASE_URL}/api/auth/login-json"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_get_current_user(token):
    """Test Get Current User"""
    print("=" * 50)
    print("4. Testing Get Current User...")
    print("=" * 50)
    
    url = f"{BASE_URL}/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Hauptfunktion - führt alle Tests aus"""
    print("\n" + "=" * 50)
    print("API Testing Script")
    print("=" * 50 + "\n")
    
    # Test-Daten
    test_name = "Test User"
    test_email = "test@example.com"
    test_password = "test123456"
    
    # 1. Health Check
    try:
        test_health_check()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 2. Registrierung
    try:
        registered = test_register(test_name, test_email, test_password)
        if not registered:
            print("⚠️  User might already exist, trying login instead...\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 3. Login
    try:
        token = test_login(test_email, test_password)
        if not token:
            print("❌ Login failed!\n")
            return
    except Exception as e:
        print(f"Error: {e}\n")
        return
    
    # 4. Get Current User
    try:
        test_get_current_user(token)
    except Exception as e:
        print(f"Error: {e}\n")
    
    print("=" * 50)
    print("Testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()





