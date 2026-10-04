import threading
import uuid

from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector

from services.cv_implementation.frame_processor import AngleSmoother
from backend.logger import logger

DETECTOR_FACTORY = {
    "Squats": SquatDetector,
    "Push-ups": PushUpDetector,
    "Biceps Curls (Dumbbell)": BicepsCurlDetector,
    "Shoulder Press": ShoulderPressDetector,
    "Lunges": LungesDetector,
}


class SessionState:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.exercise_type: str | None = None
        self.detectors: dict = {}
        self.smoother = AngleSmoother()
        self.lock = threading.Lock()

    def get_detector(self, exercise_type: str):
        if exercise_type not in DETECTOR_FACTORY:
            raise ValueError(f"Unknown exercise: {exercise_type}")

        if exercise_type != self.exercise_type:
            self.smoother.reset()
            self.exercise_type = exercise_type

        if exercise_type not in self.detectors:
            self.detectors[exercise_type] = DETECTOR_FACTORY[exercise_type]()

        return self.detectors[exercise_type]

    def reset_exercise(self, exercise_type: str):
        if exercise_type in self.detectors:
            self.detectors[exercise_type].reset()
        self.smoother.reset()


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, SessionState] = {}
        self._lock = threading.Lock()

    def start(self, user_id: int) -> str:
        session_id = str(uuid.uuid4())
        with self._lock:
            self._sessions[session_id] = SessionState(user_id)
        logger.info("Workout session started: %s (user_id=%s)", session_id, user_id)
        return session_id

    def get(self, session_id: str) -> SessionState | None:
        with self._lock:
            return self._sessions.get(session_id)

    def end(self, session_id: str):
        with self._lock:
            existed = self._sessions.pop(session_id, None) is not None
        if existed:
            logger.info("Workout session ended: %s", session_id)


sessions = SessionManager()