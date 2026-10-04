import os
from groq import Groq

from backend.logger import logger

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.error("Groq client init failed: GROQ_API_KEY is not set")
            raise RuntimeError("GROQ_API_KEY is not set")
        _client = Groq(api_key=api_key)
        logger.info("Groq client initialized")
    return _client


SYSTEM_PROMPT = (
    "You are a concise, encouraging gym coach speaking live during a "
    "workout. Reply with ONE short spoken sentence only - no markdown, "
    "no emoji, under 15 words. Never invent numbers you weren't given. "
    "Do not explain your reasoning — output only the final spoken line."
)
FALLBACK_LINES = {
    "set_complete": "Nice set! Keep that pace going.",
    "workout_complete": "Workout complete! Great effort today.",
    "form_correction": "Watch your form — reset and go slower.",
}


def generate_feedback(event: str, exercise: str, metrics: dict) -> str:
    """
    event: "set_complete" | "workout_complete" | "form_correction"
    exercise: e.g. "Squats"
    metrics: whatever the detector returned for this frame (angles, status)
    """
    user_prompt = (
        f"Event: {event}\n"
        f"Exercise: {exercise}\n"
        f"Metrics: {metrics}\n"
        "Give one short coaching line for this moment."
    )

    client = _get_client()

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.6,
            reasoning_effort="low",
        )
    except TypeError:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.6,
        )

    raw = response.choices[0].message.content
    text = (raw or "").strip()

    if not text:
        logger.warning(
            "Groq returned empty content for event='%s' exercise='%s' — using fallback line",
            event, exercise,
        )
        return FALLBACK_LINES.get(event, "Keep going, you're doing great.")

    logger.debug("Groq coaching feedback generated: event='%s' exercise='%s'", event, exercise)
    return text