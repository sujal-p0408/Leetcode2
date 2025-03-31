from flask import Flask
from supabase import create_client
from openai import OpenAI
import os
from config import SUPABASE_URL, SUPABASE_KEY, DEEPSEEK_API_KEY, DEEPSEEK_API_URL

# Initialize Supabase globally
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize OpenAI client
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)

def create_app():
    """Flask App Factory"""
    app = Flask(__name__)

    # Import blueprints inside the function to avoid circular imports
    from app.admin.routes import admin
    from app.users.routes import users_bp
    from app.progress.routes import progress
    from app.chatbot.chatbot import chatbot
    from app.main.routes import main
    
    # Register blueprints if not already registered
    if "admin" not in app.blueprints:
        app.register_blueprint(admin, url_prefix='/admin')
    if "users" not in app.blueprints:
        app.register_blueprint(users_bp, url_prefix='/api')
    if "progress" not in app.blueprints:
        app.register_blueprint(progress, url_prefix='/api/progress')
    if "chatbot" not in app.blueprints:
        app.register_blueprint(chatbot, url_prefix='/api/chat')
    if "main" not in app.blueprints:
        app.register_blueprint(main)
        
    return app
