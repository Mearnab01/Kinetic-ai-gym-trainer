"""
Single-frame pose processing for the /api/frame endpoint.

Adapted from services/cv_implementation/exercise_video_processor.py. The only
real change is running_mode: the original used vision.RunningMode.VIDEO with
a monotonically increasing timestamp counter, appropriate for a persistent
streamlit-webrtc connection. Here each HTTP request is an independent frame
with no guaranteed timing relationship to the last one, so we use
vision.RunningMode.IMAGE and .detect() instead of .detect_for_video(). The
landmarker model, confidence thresholds, and every detector class are
unchanged.

Landmarks are returned to the client (normalized x/y/visibility) so React can
draw the skeleton overlay on a canvas without round-tripping the frame image.
"""
import base64
import io
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from services.config.workout_config import POSE_CONNECTIONS
from backend.database.session_manager import sessions
from backend.logger import logger

MODEL_PATH = Path(__file__).resolve().parents[1] / "ml_models" / "pose_landmarker_full.task"


@lru_cache(maxsize=1)
def _load_landmarker():
    if not MODEL_PATH.is_file():
        logger.error("Pose model not found at %s", MODEL_PATH)
        raise RuntimeError(
            f"Pose landmarker model not found at {MODEL_PATH}. "
            "Make sure backend/models/pose_landmarker_full.task exists and "
            "hasn't been excluded by .gitignore/deployment."
        )

    size_bytes = MODEL_PATH.stat().st_size
    if size_bytes == 0:
        logger.error("Pose model at %s is empty (0 bytes)", MODEL_PATH)
        raise RuntimeError(
            f"Pose landmarker model at {MODEL_PATH} is empty (0 bytes) — "
            "it looks corrupted or was not downloaded/copied correctly."
        )

    logger.info("Loading pose landmarker model: %s (%.1f MB)", MODEL_PATH, size_bytes / 1_048_576)

    base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        min_pose_detection_confidence=0.7,
        min_pose_presence_confidence=0.7,
        min_tracking_confidence=0.7,
        output_segmentation_masks=False,
    )
    landmarker = vision.PoseLandmarker.create_from_options(options)
    logger.info("Pose landmarker model loaded successfully")
    return landmarker


def _decode_image(image_base64: str) -> np.ndarray:
    if "," in image_base64:
        image_base64 = image_base64.split(",", 1)[1]
    raw = base64.b64decode(image_base64)
    pil_img = Image.open(io.BytesIO(raw)).convert("RGB")
    return np.array(pil_img)


def process_frame(session_id: str, exercise_type: str, image_base64: str) -> dict:
    state = sessions.get(session_id)
    if state is None:
        raise KeyError("Unknown or expired session_id")

    landmarker = _load_landmarker()
    image_np = _decode_image(image_base64)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_np)
    result = landmarker.detect(mp_image)

    if not result.pose_landmarks:
        return {"pose_detected": False, "reps": state.get_detector(exercise_type).reps}

    landmarks = result.pose_landmarks[0]
    detector = state.get_detector(exercise_type)

    with state.lock:
        raw_metrics = detector.process(landmarks)
        metrics = state.smoother.smooth(raw_metrics)

    metrics["pose_detected"] = True
    metrics["landmarks"] = [
        {"x": lm.x, "y": lm.y, "visibility": lm.visibility} for lm in landmarks
    ]
    metrics["connections"] = POSE_CONNECTIONS
    return metrics