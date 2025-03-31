from functools import wraps
from flask import request, jsonify
from app import supabase  

def token_required(f):
    """Middleware to check authentication token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token is missing!"}), 403

        # Remove 'Bearer ' prefix if present
        token = token.replace("Bearer ", "")

        try:
            # ✅ Decode token and get user info
            response = supabase.auth.get_user(token)

            # ✅ Fix: Access `user` property correctly
            if not response or not hasattr(response, "user") or not response.user:
                return jsonify({"error": "Invalid token"}), 403

            user_id = response.user.id  # ✅ Extract the UUID from the token

            # ✅ Fix: Ensure the user exists in `users` table
            user_data = supabase.table("users").select("role").eq("id", user_id).execute()

            # ✅ Fix: Properly check if user exists
            if not user_data.data or len(user_data.data) == 0:
                return jsonify({"error": "User not found in database!"}), 404

            user = {
                "id": user_id,
                "role": user_data.data[0]["role"]
            }

            return f(user, *args, **kwargs)

        except Exception as e:
            print("🚨 Token Error:", str(e))  # Debugging
            return jsonify({"error": "Token verification failed"}), 403

    return decorated_function

def is_admin(user):
    """Check if a user is an admin"""
    return user.get("role") == "admin"
