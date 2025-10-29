from supabase import create_client, Client
import os
from flask import request, jsonify
from functools import wraps

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_supabase_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"error": "Token no proporcionado"}), 401

        try:
            scheme, token = auth_header.split(" ")
            if scheme.lower() != "bearer":
                return jsonify({"error": "Formato inválido"}), 401

            user = supabase.auth.get_user(token)
            if not user or not user.user:
                return jsonify({"error": "Token inválido"}), 401

            request.user = {
                "id": user.user.id,
                "email": user.user.email,
            }

        except Exception as e:
            print("🔴 Error verify_supabase_token:", e)
            return jsonify({"error": f"Token inválido: {str(e)}"}), 401

        return f(*args, **kwargs)
    return decorated_function
