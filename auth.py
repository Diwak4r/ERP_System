import os
from functools import wraps
from flask import request, jsonify, session
import jwt

# Import Supabase client conditionally
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    from supabase import create_client, Client
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase_client = None # For local testing without Supabase

# Dummy user data for local testing
LOCAL_USERS = {
    "admin@factory.com": {"password": "pass123", "role": "admin", "section_id": None, "id": "admin-uuid"},
    "staff1@factory.com": {"password": "pass123", "role": "staff", "section_id": 1, "id": "staff1-uuid"},
    "staff2@factory.com": {"password": "pass123", "role": "staff", "section_id": 2, "id": "staff2-uuid"}
}

def login_user(email, password):
    """Login user with Supabase Auth or local dummy auth"""
    if supabase_client:
        try:
            response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                user_role = get_user_role(response.user.id) # This will fetch from Supabase user metadata
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session,
                    "role": user_role
                }
            else:
                return {"success": False, "error": "Invalid credentials"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        # Local dummy authentication
        user_data = LOCAL_USERS.get(email)
        if user_data and user_data["password"] == password:
            # Simulate Supabase user object
            class DummyUser:
                def __init__(self, email, id, user_metadata):
                    self.email = email
                    self.id = id
                    self.user_metadata = user_metadata
            
            class DummySession:
                def __init__(self, access_token):
                    self.access_token = access_token

            dummy_user = DummyUser(email, user_data["id"], {"role": user_data["role"], "section_id": user_data["section_id"]})
            dummy_session = DummySession("dummy-jwt-token")

            return {
                "success": True,
                "user": dummy_user,
                "session": dummy_session,
                "role": user_data["role"]
            }
        else:
            return {"success": False, "error": "Invalid credentials"}

def register_user(email, password, role="staff", section_id=1):
    """Register a new user with Supabase Auth or local dummy auth"""
    if supabase_client:
        try:
            response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "role": role,
                        "section_id": section_id
                    }
                }
            })
            
            if response.user:
                return {"success": True, "user": response.user}
            else:
                return {"success": False, "error": "Registration failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        # Local dummy registration
        if email in LOCAL_USERS:
            return {"success": False, "error": "User already exists locally"}
        LOCAL_USERS[email] = {"password": password, "role": role, "section_id": section_id, "id": f"{role}-new-uuid"}
        return {"success": True, "user": {"email": email, "id": f"{role}-new-uuid", "user_metadata": {"role": role, "section_id": section_id}}}

def get_user_role(user_id):
    """Get user role from user metadata (Supabase or local dummy) """
    if supabase_client:
        try:
            user = supabase_client.auth.get_user()
            if user and user.user:
                return user.user.user_metadata.get("role", "staff")
            return "staff"
        except:
            return "staff"
    else:
        # Local dummy role retrieval
        for email, data in LOCAL_USERS.items():
            if data["id"] == user_id:
                return data["role"]
        return "staff"

def verify_token(token):
    """Verify JWT token"""
    try:
        # For demo purposes, we'll use a simple verification
        # In production, use proper JWT verification with Supabase
        payload = jwt.decode(token, options={"verify_signature": False})
        return {"success": True, "payload": payload}
    except Exception as e:
        return {"success": False, "error": str(e)}

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        result = verify_token(token)
        if not result["success"]:
            return jsonify({"error": "Invalid token"}), 401
        
        request.user = result["payload"]
        return f(*args, **kwargs)
    return decorated_function

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({"error": "Authentication required"}), 401
            
            user_role = request.user.get('user_metadata', {}).get('role', 'staff')
            if user_role != role and role != 'any':
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# For testing without Supabase (local development)
def create_test_users():
    """Create test users for local development"""
    test_users = [
        {"email": "admin@factory.com", "password": "pass123", "role": "admin", "section_id": None},
        {"email": "staff1@factory.com", "password": "pass123", "role": "staff", "section_id": 1},
        {"email": "staff2@factory.com", "password": "pass123", "role": "staff", "section_id": 2}
    ]
    
    for user in test_users:
        result = register_user(user["email"], user["password"], user["role"], user["section_id"])
        print(f"Created user {user['email']}: {result}")

if __name__ == "__main__":
    create_test_users()

