from fastapi.testclient import TestClient
from app.main import app
import sys

client = TestClient(app)

def test_register_and_login():
    # Test Registration
    username = "testuser_verify"
    password = "testpassword123"
    email = "test_verify@example.com"
    
    print(f"Testing registration for user: {username}")
    response = client.post(
        "/users/register",
        json={"username": username, "password": password, "email": email, "role": "user"}
    )
    
    if response.status_code == 400 and "用户名已被注册" in response.text:
        print("User already exists, proceeding to login test.")
    elif response.status_code != 201:
        print(f"Registration failed: {response.status_code} - {response.text}")
        sys.exit(1)
    else:
        print("Registration successful!")
        data = response.json()
        assert data["username"] == username
        assert "id" in data

    # Test Login
    print("Testing login...")
    login_response = client.post(
        "/users/login",
        json={"username": username, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        sys.exit(1)
        
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    print("Login successful! Token received.")

if __name__ == "__main__":
    try:
        test_register_and_login()
        print("All verification tests passed!")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
