from flask import Blueprint, request, jsonify
from middlewares.auth import token_required  
from app import supabase  
from config import ADMIN_SECRET  # Load admin secret securely
import re

users_bp = Blueprint('users', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@users_bp.route('/signup', methods=['POST'])
def signup():
    """User Registration (Email, Password, Username, Phone) with Admin Code"""
    data = request.get_json()
    print("Received signup data:", data)  # Debug print
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    phone = data.get("phone")
    admin_code = data.get("admin_code")  # ✅ Admin code from request
    role = "user"  # Default role

    if not email or not password or not username or not phone:
        return jsonify({"error": "Email, password, username, and phone are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    # ✅ Check if the provided admin code is correct
    if admin_code and admin_code == ADMIN_SECRET:
        role = "admin"

    try:
        # First check if user exists
        try:
            existing_user = supabase.auth.get_user_by_email(email)
            if existing_user:
                # If user exists but email is not confirmed, resend verification
                if not existing_user.email_confirmed_at:
                    supabase.auth.resend({
                        "type": "signup",
                        "email": email
                    })
                    return jsonify({
                        "message": "User exists but email not verified. Verification email resent.",
                        "status": "resent"
                    })
                else:
                    return jsonify({"error": "User already registered and verified"}), 400
        except Exception as e:
            print("User check error:", str(e))
            # If user doesn't exist, proceed with signup
            pass

        # ✅ Sign up the user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "data": {  
                "username": username,
                "phone": phone,
                "role": role  # ✅ Store role in metadata
            }
        })
        print("Supabase response:", response)  # Debug print

        if response.user is None:
            return jsonify({"error": "Signup failed. Check email format or try again."}), 400

        # ✅ Get the UUID assigned by Supabase
        user_id = response.user.id  

        # ✅ Store user details in `users` table with correct role
        user_data = {
            "id": user_id,
            "email": email,
            "username": username,
            "phone": phone,
            "role": role  
        }
        supabase.table("users").insert(user_data).execute()

        return jsonify({
            "message": "User registered successfully. Check your email to verify your account.",
            "role": role
        })

    except Exception as e:
        print("Signup error:", str(e))  # Debug print
        return jsonify({"error": str(e)}), 500

### --- 🔑 User Login (Checks Email Confirmation) ---
@users_bp.route('/login', methods=['POST'])
def login():
    """User Login (Email/Password)"""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})

        if hasattr(response, 'error') and response.error:
            return jsonify({"error": response.error.message}), 400

        # ✅ Ensure email confirmation before login
        user = response.user
        if not user or not user.email_confirmed_at:
            return jsonify({"error": "Email not confirmed. Please check your email and verify your account."}), 403

        return jsonify({
            "message": "Login successful",
            "token": response.session.access_token
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# FIXME: gotrue.errors.AuthApiError: Missing one of these types: signup, email_change, sms, phone_change
### --- 🔹 Resend Confirmation Email ---
@users_bp.route('/resend-confirmation', methods=['POST'])
def resend_confirmation():
    """Resend Email Confirmation Link"""
    data = request.get_json()
    email = data.get("email")
    try:
        response = supabase.auth.resend({"email": email})

        if response.error:
            return jsonify({"error": response.error.message}), 400

        return jsonify({"message": "Confirmation email sent successfully."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# TODO: NOT implemented
### --- 🔹 Google Login ---
@users_bp.route('/google-login', methods=['POST'])
def google_login():
    """Google Login (Client provides OAuth token)"""
    data = request.get_json()
    access_token = data.get("access_token")  # Token from Google OAuth

    try:
        response = supabase.auth.sign_in_with_id_token({"provider": "google", "id_token": access_token})

        if response.error:
            return jsonify({"error": response.error.message}), 400

        return jsonify({"message": "Google login successful", "token": response.session.access_token})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


### --- 📖 Get All Articles (Users Can Read) ---
@users_bp.route('/articles', methods=['GET'])
@token_required
def get_articles(user):
    try:
        # Fetch articles from Supabase
        response = supabase.table("articles").select("*").execute()
        
        if response.data:
            return jsonify(response.data)
        else:
            return jsonify([])
            
    except Exception as e:
        print(f"Error fetching articles: {str(e)}")
        return jsonify({"error": "Failed to fetch articles"}), 500

### --- 📚 Mark Practice Questions (Track Progress) ---
@users_bp.route('/questions/<string:question_id>/mark-read', methods=['POST'])
@token_required
def mark_question_as_read(user, question_id):
    """Users can mark articles as read (Track Progress)"""
    progress_entry = {
        "user_id": user["id"],  
        "question_id": question_id
    }
    response = supabase.table("userprogress").insert(progress_entry).execute()
    return jsonify(response.data)

# TODO: fetch question from category not article 
@users_bp.route('/articles/<string:article_id>/questions', methods=['GET'])
@token_required
def get_related_questions(user, article_id):
    """Users can view practice questions related to a specific article"""
    # Fetch the article to ensure it exists
    response_article = supabase.table("articles").select("*").eq("id", article_id).execute()
    article = response_article.data

    if not article:
        return jsonify({"error": "Article not found"}), 404

    # Retrieve the category of the article
    category = article[0].get('category')
    if not category:
        return jsonify({"error": "Article does not have a category"}), 400

    # Fetch related practice questions based on the article's category
    response_questions = supabase.table("practicequestions").select("*").eq("category", category).execute()
    questions = response_questions.data

    return jsonify({"article": article[0], "related_questions": questions})

### --- 📊 Get User Progress ---
@users_bp.route('/user/progress', methods=['GET'])
@token_required
def get_user_progress(user):
    """Users can check their reading progress"""
    response = supabase.table("userprogress").select("*").eq("user_id", user["id"]).execute()
    return jsonify(response.data)

@users_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification"""
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Resend verification email using Supabase
        response = supabase.auth.resend({
            "type": "signup",
            "email": email
        })
        
        return jsonify({
            "message": "Verification email resent successfully. Please check your inbox."
        })

    except Exception as e:
        print("Resend verification error:", str(e))
        return jsonify({"error": str(e)}), 500

@users_bp.route('/list-users', methods=['GET'])
def list_users():
    """List all users (Development only)"""
    try:
        # Fetch all users
        response = supabase.table("users").select("*").execute()
        users = response.data
        
        # Print users for debugging
        print("\nRegistered Users:")
        for user in users:
            print(f"Email: {user.get('email')}")
            print(f"Username: {user.get('username')}")
            print(f"Role: {user.get('role')}")
            print("---")
            
        return jsonify(users)

    except Exception as e:
        print("Error listing users:", str(e))
        return jsonify({"error": str(e)}), 500
