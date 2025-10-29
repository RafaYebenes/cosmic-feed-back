from flask import Blueprint, jsonify, request
from services.forum_service import (
    get_all_posts,
    get_post_by_id,
    create_post,
    delete_post,
    get_comments_by_post,
    create_comment,
    update_post_votes
)
from services.auth_guard import verify_supabase_token

forum_bp = Blueprint("forum", __name__)

# ==============================
# 📖 Rutas públicas
# ==============================

@forum_bp.route("/posts", methods=["GET"])
def fetch_posts():
    try:
        posts = get_all_posts()
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@forum_bp.route("/posts/<post_id>", methods=["GET"])
def fetch_post(post_id):
    try:
        post = get_post_by_id(post_id)
        comments = get_comments_by_post(post_id)
        return jsonify({"post": post, "comments": comments}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@forum_bp.route("/posts/<post_id>/comments", methods=["GET"])
def fetch_comments(post_id):
    try:
        comments = get_comments_by_post(post_id)
        return jsonify(comments), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================
# 🔒 Rutas protegidas
# ==============================

@forum_bp.route("/posts", methods=["POST"])
@verify_supabase_token
def create_new_post():
    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        category = data.get("category", "General")
        author_id = request.user["id"]  # 🧠 del token

        if not all([title, content]):
            return jsonify({"error": "Faltan campos requeridos"}), 400

        new_post = create_post(title, content, author_id, category)
        return jsonify(new_post), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@forum_bp.route("/comments", methods=["POST"])
@verify_supabase_token
def add_comment():
    try:
        data = request.get_json()
        post_id = data.get("post_id")
        content = data.get("content")
        author_id = request.user["id"]  # 🧠 del token

        if not all([post_id, content]):
            return jsonify({"error": "Faltan campos requeridos"}), 400

        comment = create_comment(post_id, author_id, content)
        return jsonify(comment), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@forum_bp.route("/posts/<post_id>", methods=["DELETE"])
@verify_supabase_token
def remove_post(post_id):
    try:
        delete_post(post_id, request.user["id"])
        return jsonify({"message": "Post eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@forum_bp.route("/posts/<post_id>/vote", methods=["POST"])
@verify_supabase_token
def vote_post(post_id):
    try:
        data = request.get_json()
        delta = int(data.get("delta", 0))
        updated_post = update_post_votes(post_id, delta)
        return jsonify(updated_post), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

