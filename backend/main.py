import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from backend import coaching_cache
from backend.logger import logger, LOG_TRACEBACK as _log_tracebacks
from backend.services import auth_face, pose_processor, exercise_repository
from backend.services.coaching.voice_pipeline import get_coaching_audio
from backend.database.session_manager import sessions, DETECTOR_FACTORY
from services.config.workout_config import EXERCISE_OPTIONS

app = FastAPI(title="Kinetic API")

# CORS — unchanged.
origins = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging + crash containment ──────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(
            "%s %s | %s: %s",
            request.method, request.url.path, type(exc).__name__, exc,
            exc_info=_log_tracebacks,
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    if response.status_code >= 500:
        logger.error("%s %s | %d", request.method, request.url.path, response.status_code)
    elif response.status_code >= 400:
        logger.warning("%s %s | %d", request.method, request.url.path, response.status_code)
    else:
        logger.info("%s %s | %d", request.method, request.url.path, response.status_code)

    return response


@app.on_event("startup")
async def on_startup():
    logger.info("Application started")


# ── Schemas ──────────────────────────────────────────────────────────────────

class EnrollRequest(BaseModel):
    username: str
    image_base64: str


class VerifyRequest(BaseModel):
    image_base64: str


class SessionStartRequest(BaseModel):
    user_id: int


class FrameRequest(BaseModel):
    session_id: str
    exercise_type: str
    image_base64: str


class ResetRequest(BaseModel):
    session_id: str
    exercise_type: str


class CoachCachedRequest(BaseModel):
    username: str
    event: str  # "set_complete" | "workout_complete" | "pose_lost"


class CoachSpeakRequest(BaseModel):
    event: str  # "set_complete" | "workout_complete" | "form_correction"
    exercise: str
    metrics: dict = {}


class SaveExerciseRequest(BaseModel):
    user_id: int
    exercise_name: str
    reps: int
    sets: int
    duration_sec: float


# ── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/exercises")
def list_exercises():
    return {"exercises": EXERCISE_OPTIONS}


# ── Face auth ────────────────────────────────────────────────────────────────

@app.post("/api/auth/enroll")
def enroll(req: EnrollRequest):
    username = req.username.strip()
    if len(username) < 2:
        raise HTTPException(400, "Username must be at least 2 characters.")
    try:
        user = auth_face.enroll_user(username, req.image_base64)
    except auth_face.NoFaceDetectedError as e:
        raise HTTPException(422, str(e))
    return user


@app.post("/api/auth/verify")
def verify(req: VerifyRequest):
    try:
        user = auth_face.verify_face(req.image_base64)
    except auth_face.NoFaceDetectedError as e:
        raise HTTPException(422, str(e))
    if user is None:
        raise HTTPException(401, "Face not recognized. Please enroll first or try again.")
    return user


# ── Workout session ──────────────────────────────────────────────────────────

@app.post("/api/session/start")
def session_start(req: SessionStartRequest):
    session_id = sessions.start(req.user_id)
    return {"session_id": session_id}


@app.post("/api/session/end")
def session_end(session_id: str):
    sessions.end(session_id)
    return {"ok": True}


@app.post("/api/session/reset")
def session_reset(req: ResetRequest):
    state = sessions.get(req.session_id)
    if state is None:
        raise HTTPException(404, "Session not found")
    if req.exercise_type not in DETECTOR_FACTORY:
        raise HTTPException(400, "Unknown exercise")
    state.reset_exercise(req.exercise_type)
    return {"ok": True}


@app.post("/api/frame")
def frame(req: FrameRequest):
    if req.exercise_type not in DETECTOR_FACTORY:
        raise HTTPException(400, "Unknown exercise")
    try:
        metrics = pose_processor.process_frame(
            req.session_id, req.exercise_type, req.image_base64
        )
    except KeyError:
        raise HTTPException(404, "Session not found or expired")
    return metrics


# ── Voice coaching (new, additive — not wired into the frame loop) ──────────

# ── Voice coaching — cached templates (no API call per trigger) ─────────────

@app.post("/api/coach/cached")
def coach_cached(req: CoachCachedRequest):
    try:
        audio_bytes = coaching_cache.get_cached_audio(req.username, req.event)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return Response(content=audio_bytes, media_type="audio/mpeg")


# ── Voice coaching — dynamic (Groq gpt-oss-120b, for future non-templated feedback) ──

@app.post("/api/coach/speak")
def coach_speak(req: CoachSpeakRequest):
    try:
        audio_bytes = get_coaching_audio(req.event, req.exercise, req.metrics)
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    return Response(content=audio_bytes, media_type="audio/mpeg")


# ── Exercise history / persistence ───────────────────────────────────────────

@app.post("/api/exercise/save")
def save_exercise(req: SaveExerciseRequest):
    exercise_repository.add_exercise(
        req.user_id, req.exercise_name, req.reps, req.sets, req.duration_sec
    )
    return {"ok": True}


@app.get("/api/exercise/history/{user_id}")
def exercise_history(user_id: int):
    return {"history": exercise_repository.get_users_exercises(user_id)}