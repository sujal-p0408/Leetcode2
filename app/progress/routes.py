from flask import Blueprint, request, jsonify
from app import create_app

progress = Blueprint('progress', __name__)

@progress.route('/progress', methods=['POST'])
def track_progress():
    app = create_app()
    data = request.get_json()
    response = app.supabase.table("user_progress").insert(data).execute()
    return jsonify(response.data)

@progress.route('/progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    app = create_app()
    response = app.supabase.table("user_progress").select("*").eq("user_id", user_id).execute()
    return jsonify(response.data)