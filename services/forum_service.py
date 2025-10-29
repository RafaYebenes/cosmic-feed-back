from services.supabase_client import supabase
from datetime import datetime

# ==============================
# 📬 POSTS
# ==============================

def get_all_posts():
    """Obtiene todos los posts ordenados por fecha descendente."""
    response = supabase.table("posts").select(
        "id, title, content, category, likes, created_at, author_id, upvotes, downvotes"
    ).order("created_at", desc=True).execute()

    posts = response.data or []

    # opcional: obtener username desde profiles si lo necesitas
    for post in posts:
        prof = (
            supabase.table("profiles")
            .select("username, avatar_url")
            .eq("id", post["author_id"])
            .single()
            .execute()
        )
        post["profiles"] = prof.data if prof.data else {}

    return posts



def get_post_by_id(post_id: str):
    """Obtiene un post por su ID junto con los datos del autor."""
    response = supabase.table("posts").select(
        "id, title, content, category, likes, created_at, author_id, upvotes, downvotes"
    ).eq("id", post_id).single().execute()

    if not response.data:
        return None  # Si no existe el post, devolvemos None

    post = response.data

    # Buscar perfil del autor
    prof = (
        supabase.table("profiles")
        .select("username, avatar_url")
        .eq("id", post["author_id"])
        .single()
        .execute()
    )

    post["profiles"] = prof.data if prof.data else {}
    return post



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

def update_post_votes(post_id: str, delta: int):
    """
    Actualiza los votos de un post.
    delta = +1 → voto positivo
    delta = -1 → voto negativo
    Devuelve el post actualizado.
    """
    try:
        # Obtener post actual
        post = (
            supabase.table("posts")
            .select("id, upvotes, downvotes")
            .eq("id", post_id)
            .single()
            .execute()
        )

        print("🧩 POST_ID:", post_id)
        print("🧩 DATA:", post.data)

        if not post.data:
            raise ValueError("Post no encontrado")

        current = post.data
        new_up = current.get("upvotes", 0)
        new_down = current.get("downvotes", 0)

        if delta > 0:
            new_up += 1
        elif delta < 0:
            new_down += 1

        # ✅ Actualizamos siempre (fuera del bloque if/elif)
        updated = (
            supabase.table("posts")
            .update({"upvotes": new_up, "downvotes": new_down})
            .eq("id", post_id)
            .execute()
        )

        print("🧠 UPDATED:", updated.data)

        # Retornar el post actualizado completo
        if updated.data:
            post_full = (
                supabase.table("posts")
                .select(
                    "id, title, content, category, upvotes, downvotes, created_at, author_id"
                )
                .eq("id", post_id)
                .single()
                .execute()
            )
            return post_full.data

        return None

    except Exception as e:
        print("❌ Error en update_post_votes:", e)
        raise  # ⚠️ importante: deja que el decorador capture y devuelva 400
