from core.base_exercise import BaseExercise

 
class LungesDetector(BaseExercise):
    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.7
    BALANCE_TOLERANCE = 0.10

    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    def __init__(self):
        super().__init__()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None

    def process(self, landmarks) -> dict:
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE),
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE),
        )

        if left_knee_angle <= right_knee_angle:
            front_knee_angle = left_knee_angle
            front_hip_idx = self.LEFT_HIP
            front_knee_idx = self.LEFT_KNEE
            front_ankle_idx = self.LEFT_ANKLE
            shoulder_idx_for_torso = self.LEFT_SHOULDER
        else:
            front_knee_angle = right_knee_angle
            front_hip_idx = self.RIGHT_HIP
            front_knee_idx = self.RIGHT_KNEE
            front_ankle_idx = self.RIGHT_ANKLE
            shoulder_idx_for_torso = self.RIGHT_SHOULDER

        key_landmarks_visible = landmarks[front_hip_idx].visibility > self.MIN_VISIBILITY and landmarks[front_knee_idx].visibility > self.MIN_VISIBILITY and landmarks[front_ankle_idx].visibility > self.MIN_VISIBILITY

        if key_landmarks_visible:
            if front_knee_angle < self.DOWN_THRESHOLD:
                self.stage = "down"

            if front_knee_angle > self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1

        torso_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx_for_torso),
            self.get_point(landmarks, front_hip_idx),
            self.get_point(landmarks, front_knee_idx),
        )

        shoulder_mid_x = (landmarks[self.LEFT_SHOULDER].x + landmarks[self.RIGHT_SHOULDER].x) / 2
        hip_mid_x = (landmarks[self.LEFT_HIP].x + landmarks[self.RIGHT_HIP].x) / 2
        lateral_offset = abs(shoulder_mid_x - hip_mid_x)

        if lateral_offset <= self.BALANCE_TOLERANCE:
            balance_status = "BALANCED"
        else:
            balance_status = "OFF BALANCE"

        return {
            "reps": self.reps,
            "front_knee_angle": int(front_knee_angle),
            "torso_angle": int(torso_angle),
            "balance_status": balance_status,
        }
        
""" 
LUNGES FLOW (STATE MACHINE)
Start → standing (both legs straight)
front_knee_angle ≈ 160-180°
stage = None
reps = 0

#========#============

🔥 Step 0: Identify FRONT LEG (VERY IMPORTANT)
Compare both knees:

left_knee_angle vs right_knee_angle

👉 smaller angle = more bent = FRONT LEG

Example:

Left = 80°, Right = 160°
→ Left leg = front leg

#========#============
🔽 Going DOWN (lunge position)
↓ step forward + bend
front_knee_angle decreases (160 → 130 → 100 → 80)

when:
front_knee_angle < 100 (DOWN_THRESHOLD)

→ stage = "down"

👉 Meaning:

You reached bottom of lunge

#========#============
🔼 Coming UP (push back to standing)
↓ push back
front_knee_angle increases (80 → 110 → 140 → 170)

when:
front_knee_angle > 160 (UP_THRESHOLD)
AND stage == "down"

→ stage = "up"
→ reps += 1 ✅

"""