from backend.services.coaching import llm, tts


def get_coaching_audio(event: str, exercise: str, metrics: dict) -> bytes:
    sentence = llm.generate_feedback(event, exercise, metrics)
    return tts.synthesize(sentence)