import io
from gtts import gTTS

from backend.logger import logger

_FALLBACK_TEXT = "Keep going, you're doing great."


def synthesize(text: str) -> bytes:
    text = (text or "").strip()
    if not text:
        logger.warning("tts.synthesize() got empty text — using fallback line")
        text = _FALLBACK_TEXT

    buffer = io.BytesIO()
    gTTS(text=text, lang="en").write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()