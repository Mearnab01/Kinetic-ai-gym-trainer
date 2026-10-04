import hashlib
import os

from gtts import gTTS

from backend.logger import logger

CACHE_DIR = os.path.join(os.path.dirname(__file__), "audio_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

TEMPLATES = {
    # Set / Workout
    "set_complete": "{username}, set complete! Keep going, you're doing great.",
    "workout_complete": "{username}, workout complete! Great job today.",
    
    # Pose / Camera
    "pose_lost": "{username}, I can't see you clearly. Please get back in frame.",
    "pose_detected": "{username}, I can see you. Let's get started.",
    
    # Rep milestones
    "rep_complete": "Nice rep, {username}!",
    "halfway": "You're halfway there, {username}! Keep pushing.",
    "last_rep": "Last rep, {username}! Make it count.",
    
    # Form
    "good_form": "Great form, {username}!",
    "form_improved": "Much better, {username}! Keep that form.",
    "slow_down": "{username}, slow down and control the movement.",
    "too_fast": "{username}, you're moving too fast. Focus on control.",
    
    # Motivation
    "keep_going": "Keep going, {username}! You've got this.",
    "almost_done": "Almost there, {username}! Just a little more.",
    "great_job": "Great job, {username}! Keep it up.",
    
    # Workout transitions
    "exercise_start": "Get ready, {username}. Let's begin.",
    "next_exercise": "Next exercise, {username}. Get ready.",
    "rest_start": "Nice work, {username}. Take a short rest.",
    "rest_over": "Rest is over, {username}. Let's get back to work.",
}


def _cache_path(username: str, event: str) -> str:
    key = hashlib.sha1(f"{username}:{event}".encode()).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f"{key}.mp3")


def get_cached_audio(username: str, event: str) -> bytes:
    if event not in TEMPLATES:
        raise ValueError(f"No cached template for event: {event}")

    path = _cache_path(username, event)

    if not os.path.exists(path):
        text = TEMPLATES[event].format(username=username)
        gTTS(text=text, lang="en").save(path)
        logger.info("Coaching audio cached: user='%s' event='%s'", username, event)
    else:
        logger.debug("Coaching audio cache hit: user='%s' event='%s'", username, event)

    with open(path, "rb") as f:
        return f.read()