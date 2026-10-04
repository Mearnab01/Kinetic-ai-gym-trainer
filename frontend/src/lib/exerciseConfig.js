export const EXERCISE_OPTIONS = [
  "Squats",
  "Push-ups",
  "Biceps Curls (Dumbbell)",
  "Shoulder Press",
  "Lunges",
];

export const BAD_FORM_CHECK = {
  Squats: { field: "depth_status", badValue: "TOO HIGH" },
  "Push-ups": { field: "body_alignment", badValue: "Poor Form" },
  "Biceps Curls (Dumbbell)": { field: "shoulder_status", badValue: "ELBOW DRIFTING" },
  "Shoulder Press": { field: "back_arch_status", badValue: "Excessive Arch" },
  Lunges: { field: "balance_status", badValue: "OFF BALANCE" },
};

export const METRICS_FIELDS = {
  Squats: [
    { key: "knee_angle", label: "Knee Angle", suffix: "\u00b0" },
    { key: "back_angle", label: "Back Angle", suffix: "\u00b0" },
    { key: "depth_status", label: "Depth Status" },
  ],
  "Push-ups": [
    { key: "elbow_angle", label: "Elbow Angle", suffix: "\u00b0" },
    { key: "body_alignment", label: "Body Alignment" },
    { key: "hip_status", label: "Hip Position" },
  ],
  "Biceps Curls (Dumbbell)": [
    { key: "elbow_angle", label: "Elbow Angle", suffix: "\u00b0" },
    { key: "shoulder_status", label: "Shoulder Stability" },
    { key: "swing_status", label: "Swing Detection" },
  ],
  "Shoulder Press": [
    { key: "elbow_angle", label: "Elbow Angle", suffix: "\u00b0" },
    { key: "extension_status", label: "Arm Extension" },
    { key: "back_arch_status", label: "Back Arch" },
  ],
  Lunges: [
    { key: "front_knee_angle", label: "Front Knee Angle", suffix: "\u00b0" },
    { key: "torso_angle", label: "Torso Angle", suffix: "\u00b0" },
    { key: "balance_status", label: "Balance Status" },
  ],
};