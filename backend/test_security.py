import requests
import sys

BASE_URL = "http://localhost:8000"

def test_security_flow():
    # 1. Register users
    admin_user = {"username": "admin_sec_test", "password": "password", "email": "admin@test.com"}
    normal_user = {"username": "user_sec_test", "password": "password", "email": "user@test.com"}
    
    # Clean up (if exists) - requires manual DB cleanup or just ignore error
    
    print("Registering users...")
    requests.post(f"{BASE_URL}/users/register", json=admin_user) # might fail if exists
    requests.post(f"{BASE_URL}/users/register", json=normal_user) # might fail if exists
    
    # 2. Login as Admin (assuming manually set as admin in DB or just testing user logic first)
    # Since we can't easily make admin via API without existing admin, let's assume we use an existing admin or skip admin parts if we can't.
    # Actually, we can just test user password change first.
    
    print("Logging in as normal user...")
    resp = requests.post(f"{BASE_URL}/users/login", data={"username": normal_user["username"], "password": normal_user["password"]})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        # Try to login with new password if previous run changed it
        resp = requests.post(f"{BASE_URL}/users/login", data={"username": normal_user["username"], "password": "newpassword"})
        if resp.status_code != 200:
             print("Login failed with new password too. Exiting.")
             return
        else:
            print("Logged in with new password from previous run.")
            normal_user["password"] = "newpassword"
            
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Change Password
    print("Changing password...")
    new_password = "newpassword_updated"
    resp = requests.put(f"{BASE_URL}/users/password", json={"old_password": normal_user["password"], "new_password": new_password}, headers=headers)
    if resp.status_code != 200:
        print(f"Change password failed: {resp.text}")
        sys.exit(1)
    print("Password changed successfully.")
    
    # 4. Verify login with old password fails
    print("Verifying old password fails...")
    resp = requests.post(f"{BASE_URL}/users/login", data={"username": normal_user["username"], "password": normal_user["password"]})
    if resp.status_code == 200:
        print("Error: Old password still works!")
        sys.exit(1)
    print("Old password rejected.")
    
    # 5. Verify login with new password works
    print("Verifying new password works...")
    resp = requests.post(f"{BASE_URL}/users/login", data={"username": normal_user["username"], "password": new_password})
    if resp.status_code != 200:
        print(f"Error: New password failed! {resp.text}")
        sys.exit(1)
    print("New password accepted.")
    
    print("\nUser Security Flow Test Passed!")

if __name__ == "__main__":
    try:
        test_security_flow()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
