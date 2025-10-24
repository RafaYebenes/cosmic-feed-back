from flask import Blueprint, jsonify, request
from services.supabase_client import supabase

news_bp = Blueprint("news", __name__)

@news_bp.route("/news", methods=["GET"])
def get_news():
    category = request.args.get("category")
    query = supabase.table("news").select("*").order("published_at", desc=True)
    if category:
        query = query.eq("category_id", category)
    result = query.execute()
    return jsonify(result.data), 200

@news_bp.route("/news/<id>", methods=["GET"])
def get_news_detail(id):
    result = supabase.table("news").select("*").eq("id", id).execute()
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify(result.data[0]), 200

@news_bp.route("/categories", methods=["GET"])
def get_categories():
    result = supabase.table("categories").select("*").execute()
    return jsonify(result.data), 200
