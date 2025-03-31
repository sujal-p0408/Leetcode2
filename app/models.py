# Reference schema for Supabase tables
class User:
    table_name = "users"
    columns = ["id", "username", "email", "password_hash", "created_at", "updated_at"]

class Article:
    table_name = "articles"
    columns = ["id", "title", "content", "category", "image_url", "gif_url", "created_at", "updated_at"]

class PracticeQuestion:
    table_name = "practice_questions"
    columns = ["id", "title", "link", "difficulty", "created_at", "updated_at"]

class UserProgress:
    table_name = "user_progress"
    columns = ["id", "user_id", "article_id", "question_id", "completed_at"]