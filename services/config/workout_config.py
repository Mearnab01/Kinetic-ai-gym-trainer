EXERCISE_OPTIONS=[
    "Squats",
    "Push-ups",
    "Biceps Curls (Dumbbell)",
    "Shoulder Press",
    "Lunges"
]

# ── Pose Connections ──────────────────────────────────────────────────────────
_FACE = [
    (0, 1), (1, 2), (2, 3), (3, 7),    # nose → l-eye chain → l-ear
    (0, 4), (4, 5), (5, 6), (6, 8),    # nose → r-eye chain → r-ear
    (9, 10), (0, 9), (0, 10),           # mouth line + nose-to-mouth
]
 
_TORSO = [
    (11, 12),                           # shoulder bar
    (23, 24),                           # hip bar
    (11, 23), (12, 24),                 # left / right side torso
]
 
_LEFT_ARM = [
    (11, 13), (13, 15),                 # shoulder → elbow → wrist
    (15, 17), (15, 19), (15, 21),       # wrist → pinky / index / thumb
    (17, 19),                           # palm closure
]
 
_RIGHT_ARM = [
    (12, 14), (14, 16),
    (16, 18), (16, 20), (16, 22),
    (18, 20),
]
 
_LEFT_LEG = [
    (23, 25), (25, 27),                 # hip → knee → ankle
    (27, 29), (29, 31), (27, 31),       # ankle → heel → foot + arch
]
 
_RIGHT_LEG = [
    (24, 26), (26, 28),
    (28, 30), (30, 32), (28, 32),
]
 
# Flat list for any code that just needs (start, end) pairs
POSE_CONNECTIONS = _TORSO + _LEFT_ARM + _RIGHT_ARM + _LEFT_LEG + _RIGHT_LEG



METRICS_FIELDS = {
    "Squats": {
        "knee_angle": 0,
        "back_angle": 0,
        "depth_status": "N/A",
    },
    "Push-ups": {
        "elbow_angle": 0,
        "body_alignment": "N/A",
        "hip_status": "N/A",
    },
    "Biceps Curls (Dumbbell)": {
        "elbow_angle": 0,
        "shoulder_status": "N/A",
        "swing_status": "N/A",
    },
    "Shoulder Press": {
        "elbow_angle": 0,
        "extension_status": "N/A",
        "back_arch_status": "N/A",
    },
    "Lunges": {
        "front_knee_angle": 0,
        "torso_angle": 0,
        "balance_status": "N/A",
    },
}