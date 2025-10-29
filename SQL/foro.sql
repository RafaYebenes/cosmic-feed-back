-- ============================================
-- 🚀 COSMIC FEED — MODELO DE DATOS COMPLETO
-- Autenticación + Perfiles + Foro (posts + comments)
-- ============================================

-- Habilitamos la extensión necesaria para generar UUIDs
create extension if not exists "uuid-ossp";

-- ============================================
-- 1️⃣ PROFILES (extensión de auth.users)
-- ============================================

create table if not exists public.profiles (
  id uuid primary key references auth.users on delete cascade,
  username text not null unique,
  avatar_url text,
  bio text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- ============================================
-- 2️⃣ TRIGGER: crear perfil automáticamente
-- ============================================

create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, username)
  values (
    new.id,
    split_part(new.email, '@', 1)  -- usa la parte antes del @ como nombre
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();

-- ============================================
-- 3️⃣ POSTS (foro principal)
-- ============================================

create table if not exists public.posts (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  content text not null,
  author_id uuid references public.profiles(id) on delete cascade,
  category text default 'General',
  likes integer default 0,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- ============================================
-- 4️⃣ COMMENTS (respuestas dentro de un post)
-- ============================================

create table if not exists public.comments (
  id uuid primary key default uuid_generate_v4(),
  post_id uuid references public.posts(id) on delete cascade,
  author_id uuid references public.profiles(id) on delete cascade,
  content text not null,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- ============================================
-- 5️⃣ ÍNDICES para rendimiento
-- ============================================

create index if not exists idx_posts_author on public.posts(author_id);
create index if not exists idx_comments_post on public.comments(post_id);
create index if not exists idx_comments_author on public.comments(author_id);

-- ============================================
-- 6️⃣ POLÍTICAS DE SEGURIDAD (RLS)
-- ============================================

-- Activamos Row Level Security
alter table public.profiles enable row level security;
alter table public.posts enable row level security;
alter table public.comments enable row level security;

-- Reglas de acceso para profiles
create policy "Profiles are viewable by everyone"
on public.profiles for select
using (true);

create policy "Users can update their own profile"
on public.profiles for update
using (auth.uid() = id);

-- Reglas de acceso para posts
create policy "Anyone can read posts"
on public.posts for select
using (true);

create policy "Authenticated users can insert posts"
on public.posts for insert
with check (auth.uid() = author_id);

create policy "Users can update their own posts"
on public.posts for update
using (auth.uid() = author_id);

create policy "Users can delete their own posts"
on public.posts for delete
using (auth.uid() = author_id);

-- Reglas de acceso para comments
create policy "Anyone can read comments"
on public.comments for select
using (true);

create policy "Authenticated users can insert comments"
on public.comments for insert
with check (auth.uid() = author_id);

create policy "Users can delete their own comments"
on public.comments for delete
using (auth.uid() = author_id);

-- ============================================
-- ✅ FINAL: Confirmación
-- ============================================
comment on table public.profiles is 'Perfiles de usuario extendidos, vinculados con auth.users';
comment on table public.posts is 'Publicaciones del foro';
comment on table public.comments is 'Comentarios en publicaciones del foro';
