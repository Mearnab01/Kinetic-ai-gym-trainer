from core.base_exercise import BaseExercise


class DeadliftDetector(BaseExercise):
    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    LEFT_HIP = 23
    LEFT_KNEE = 25

    def process(self, landmarks):
        shoulder = self.get_point(landmarks, self.LEFT_SHOULDER)
        hip = self.get_point(landmarks, self.LEFT_HIP)
        knee = self.get_point(landmarks, self.LEFT_KNEE)

        back_angle = self.calculate_angle(shoulder, hip, knee)

        visible = (
            landmarks[self.LEFT_SHOULDER].visibility > self.MIN_VISIBILITY and
            landmarks[self.LEFT_HIP].visibility > self.MIN_VISIBILITY and
            landmarks[self.LEFT_KNEE].visibility > self.MIN_VISIBILITY
        )

        if visible:
            if back_angle < self.DOWN_THRESHOLD:
                self.stage = "down"

            if back_angle > self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1

        if back_angle > 160:
            posture = "STRAIGHT"
        elif back_angle > 140:
            posture = "SLIGHT BEND"
        else:
            posture = "ROUNDED BACK"

        return {
            "reps": self.reps,
            "back_angle": int(back_angle),
            "posture": posture
        }
        
""" 
Start → standing

↓ bend down
back_angle decreases
→ stage = "down"

↓ stand up
back_angle increases (>160)
AND stage == "down"

→ reps += 1
"""