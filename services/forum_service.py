from services.supabase_client import supabase
from datetime import datetime

# ==============================
# 📬 POSTS
# ==============================

def get_all_posts():
    """Obtiene todos los posts ordenados por fecha descendente."""
    response = supabase.table("posts").select(
        "id, title, content, category, likes, created_at, author_id, profiles(username, avatar_url)"
    ).order("created_at", desc=True).execute()

    return response.data or []


def get_post_by_id(post_id: str):
    """Obtiene un post por su ID."""
    response = supabase.table("posts").select(
        "id, title, content, category, likes, created_at, author_id, profiles(username, avatar_url)"
    ).eq("id", post_id).single().execute()

    return response.data


def create_post(title: str, content: str, author_id: str, category: str):
    """Crea un nuevo post."""   
    new_post = {
        "title": title,
        "content": content,
        "author_id": author_id,
        "category": category,
        "created_at": datetime.utcnow().isoformat(),
    }

    response = supabase.table("posts").insert(new_post).execute()
    return response.data[0] if response.data else None


def delete_post(post_id: str, author_id: str):
    """Elimina un post solo si pertenece al autor autenticado."""
    supabase.table("posts").delete().eq("id", post_id).eq("author_id", author_id).execute()


# ==============================
# 💬 COMMENTS
# ==============================

def get_comments_by_post(post_id: str):
    """Obtiene los comentarios asociados a un post."""
    response = supabase.table("comments").select(
        "id, content, created_at, author_id, profiles(username, avatar_url)"
    ).eq("post_id", post_id).order("created_at", desc=False).execute()

    return response.data or []


def create_comment(post_id: str, author_id: str, content: str):
    """Crea un nuevo comentario."""
    new_comment = {
        "post_id": post_id,
        "author_id": author_id,
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
    }

    response = supabase.table("comments").insert(new_comment).execute()
    return response.data[0] if response.data else None
