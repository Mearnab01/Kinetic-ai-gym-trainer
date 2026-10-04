import base64
import io
from functools import lru_cache

import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

from backend.database.supabase_client import supabase
from backend.logger import logger

MATCH_DISTANCE_THRESHOLD = 0.9  # same threshold used in Project 1


@lru_cache(maxsize=1)
def _load_models():
    mtcnn = MTCNN(keep_all=False, device="cpu", post_process=True)
    resnet = InceptionResnetV1(pretrained="vggface2").eval()
    return mtcnn, resnet


def _decode_image(image_base64: str) -> np.ndarray:
    if "," in image_base64:  
        image_base64 = image_base64.split(",", 1)[1]
    raw = base64.b64decode(image_base64)
    pil_img = Image.open(io.BytesIO(raw)).convert("RGB")
    return np.array(pil_img)


class NoFaceDetectedError(Exception):
    pass


def get_embedding(image_base64: str) -> np.ndarray:
    """Return a single 512-d face embedding for the (single, largest) face."""
    mtcnn, resnet = _load_models()
    image_np = _decode_image(image_base64)
    pil_img = Image.fromarray(image_np)

    face = mtcnn(pil_img)
    if face is None:
        logger.warning("Face auth: no face detected in captured image")
        raise NoFaceDetectedError("No face detected in the captured image.")

    embedding = resnet(face.unsqueeze(0))
    return embedding.detach().numpy()[0]


def enroll_user(username: str, image_base64: str) -> dict:
    """Create (or overwrite) a gym_users row with the user's face embedding."""
    embedding = get_embedding(image_base64)

    existing = (
        supabase.table("gym_users")
        .select("id")
        .eq("username", username)
        .execute()
    )

    payload = {"username": username, "face_embedding": embedding.tolist()}

    if existing.data:
        user_id = existing.data[0]["id"]
        supabase.table("gym_users").update(payload).eq("id", user_id).execute()
        logger.info("Face auth: updated enrollment for user '%s' (id=%s)", username, user_id)
        return {"id": user_id, "username": username}

    response = supabase.table("gym_users").insert(payload).execute()
    new_id = response.data[0]["id"]
    logger.info("Face auth: enrolled new user '%s' (id=%s)", username, new_id)
    return {"id": new_id, "username": username}


def verify_face(image_base64: str) -> dict | None:
    """Compare the captured face against every enrolled user's embedding."""
    embedding = get_embedding(image_base64)

    users = supabase.table("gym_users").select("*").execute().data
    if not users:
        logger.warning("Face auth: verify attempted with no enrolled users")
        return None

    best_user, best_distance = None, float("inf")
    for user in users:
        stored = user.get("face_embedding")
        if not stored:
            continue
        distance = float(np.linalg.norm(np.array(stored) - embedding))
        if distance < best_distance:
            best_distance = distance
            best_user = user

    if best_user is not None and best_distance <= MATCH_DISTANCE_THRESHOLD:
        logger.info("Face auth: verified user '%s' (distance=%.3f)", best_user["username"], best_distance)
        return {"id": best_user["id"], "username": best_user["username"]}

    logger.warning("Face auth: no match within threshold (closest distance=%.3f)", best_distance)
    return None