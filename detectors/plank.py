from core.base_exercise import BaseExercise
import time


class PlankDetector(BaseExercise):
    MIN_VISIBILITY = 0.7
    BODY_THRESHOLD = 160
    HIP_TOLERANCE = 0.08

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()
        self.start_time = None

    def reset(self):
        self.start_time = None

    def process(self, landmarks):
        shoulder = self.get_point(landmarks, self.LEFT_SHOULDER)
        hip = self.get_point(landmarks, self.LEFT_HIP)
        ankle = self.get_point(landmarks, self.LEFT_ANKLE)

        body_angle = self.calculate_angle(shoulder, hip, ankle)

        shoulder_y = landmarks[self.LEFT_SHOULDER].y
        ankle_y = landmarks[self.LEFT_ANKLE].y
        hip_y = landmarks[self.LEFT_HIP].y

        expected_hip_y = (shoulder_y + ankle_y) / 2
        hip_deviation = hip_y - expected_hip_y

        visible = (
            landmarks[self.LEFT_SHOULDER].visibility > self.MIN_VISIBILITY and
            landmarks[self.LEFT_HIP].visibility > self.MIN_VISIBILITY and
            landmarks[self.LEFT_ANKLE].visibility > self.MIN_VISIBILITY
        )

        if visible and body_angle > self.BODY_THRESHOLD and abs(hip_deviation) < self.HIP_TOLERANCE:
            if self.start_time is None:
                self.start_time = time.time()
        else:
            self.start_time = None

        duration = int(time.time() - self.start_time) if self.start_time else 0

        return {
            "duration": duration,
            "body_angle": int(body_angle),
            "status": "HOLDING" if duration > 0 else "NOT HOLDING"
        }