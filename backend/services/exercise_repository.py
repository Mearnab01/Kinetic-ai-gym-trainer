import datetime as dt

from backend.database.supabase_client import supabase
from backend.logger import logger


def add_exercise(user_id: int, exercise_name: str, reps: int, sets: int, duration_sec: float):
    today = dt.date.today().isoformat()

    existing = (
        supabase.table("gym_exercises")
        .select("*")
        .eq("user_id", user_id)
        .eq("exercise_name", exercise_name)
        .eq("log_date", today)
        .execute()
    )

    if existing.data:
        row = existing.data[0]
        supabase.table("gym_exercises").update({
            "reps": row["reps"] + reps,
            "sets": row["sets"] + sets,
            "duration_sec": round(row["duration_sec"] + duration_sec, 1),
        }).eq("id", row["id"]).execute()
        logger.info(
            "Exercise log updated: user_id=%s %s +%d reps / +%d sets",
            user_id, exercise_name, reps, sets,
        )
    else:
        supabase.table("gym_exercises").insert({
            "user_id": user_id,
            "exercise_name": exercise_name,
            "reps": reps,
            "sets": sets,
            "duration_sec": round(duration_sec, 1),
            "log_date": today,
        }).execute()
        logger.info(
            "Exercise log created: user_id=%s %s %d reps / %d sets",
            user_id, exercise_name, reps, sets,
        )


def get_users_exercises(user_id: int) -> list:
    response = (
        supabase.table("gym_exercises")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data