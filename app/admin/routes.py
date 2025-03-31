from flask import Blueprint, request, jsonify
from middlewares.auth import token_required, is_admin
from app import supabase  

admin = Blueprint('admin', __name__)

### --- Articles Management (Admin Only) ---
@admin.route('/articles', methods=['POST'])
@token_required
def create_article(user):
    """Only Admin can add articles"""
    if not is_admin(user):
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    data = request.get_json()

    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    response = supabase.table("articles").insert(data).execute()
    return jsonify({"message": "Article added successfully!", "data": response.data})

@admin.route('/articles/<string:article_id>', methods=['PUT'])
@token_required
def update_article(user, article_id):
    """Only Admin can update articles"""
    if not is_admin(user):
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    response = supabase.table("articles").update(data).eq("id", article_id).execute()
    return jsonify({"message": "Article updated successfully!", "data": response.data})

@admin.route('/articles/<string:article_id>', methods=['DELETE'])
@token_required
def delete_article(user, article_id):
    """Only Admin can delete articles"""
    if not is_admin(user):
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    response = supabase.table("articles").delete().eq("id", article_id).execute()
    return jsonify({"message": "Article deleted successfully!"})

### --- Practice Questions Management (Admin Only) ---
@admin.route('/questions', methods=['POST'])
@token_required
def create_question(user):
    """Only Admin can add questions"""
    if not is_admin(user):
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    data = request.get_json()

    if not data or "title" not in data or "link" not in data or "difficulty" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    response = supabase.table("practicequestions").insert(data).execute()
    return jsonify({"message": "Question added successfully!", "data": response.data})

@admin.route('/questions/<int:question_id>', methods=['PUT'])
@token_required
def update_question(user, question_id):
    """Only Admin can update questions"""
    if not is_admin(user):
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    response = supabase.table("practicequestions").update(data).eq("id", question_id).execute()
    return jsonify({"message": "Question updated successfully!", "data": response.data})

@admin.route('/questions/<int:question_id>', methods=['DELETE'])
@token_required
def delete_question(user, question_id):
    """Only Admin can delete questions"""
    if not is_admin(user):
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    response = supabase.table("practicequestions").delete().eq("id", question_id).execute()
    return jsonify({"message": "Question deleted successfully!"})
