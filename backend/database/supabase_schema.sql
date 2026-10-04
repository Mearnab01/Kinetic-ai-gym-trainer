-- Run in the Supabase SQL editor.
-- Two small, additive tables — nothing in Project 1's schema is touched.

create table if not exists gym_users (
    id bigint generated always as identity primary key,
    username text unique not null,
    face_embedding jsonb not null,       -- 512-d InceptionResnetV1 embedding
    created_at timestamptz default now()
);

create table if not exists gym_exercises (
    id bigint generated always as identity primary key,
    user_id bigint not null references gym_users(id) on delete cascade,
    exercise_name text not null,
    reps integer not null default 0,
    sets integer not null default 0,
    duration_sec numeric not null default 0,
    log_date date not null default current_date,
    created_at timestamptz default now(),
    unique (user_id, exercise_name, log_date)
);