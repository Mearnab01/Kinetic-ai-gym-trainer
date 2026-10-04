from pathlib import Path


# ============================================================
# FILES
# ============================================================

files = [

    # ========================================================
    # ROOT
    # ========================================================
    "README.md",
    ".gitignore",
    "template.py",

    # ========================================================
    # BACKEND
    # ========================================================
    "backend/__init__.py",
    "backend/main.py",
    "backend/logger.py",
    "backend/coaching_cache.py",
    "backend/requirements.txt",
    "backend/Dockerfile",
    "backend/README.md",
    "backend/.env",
    "backend/.env.example",

    # --------------------------------------------------------
    # backend/database
    # --------------------------------------------------------
    "backend/database/__init__.py",
    "backend/database/session_manager.py",
    "backend/database/supabase_client.py",
    "backend/database/supabase_schema.sql",

    # --------------------------------------------------------
    # backend/services
    # --------------------------------------------------------
    "backend/services/__init__.py",
    "backend/services/auth_face.py",
    "backend/services/exercise_repository.py",
    "backend/services/pose_processor.py",

    # --------------------------------------------------------
    # backend/services/coaching
    # --------------------------------------------------------
    "backend/services/coaching/__init__.py",
    "backend/services/coaching/llm.py",
    "backend/services/coaching/tts.py",
    "backend/services/coaching/voice_pipeline.py",

    # ========================================================
    # CORE
    # ========================================================
    "core/__init__.py",
    "core/base_exercise.py",

    # ========================================================
    # DETECTORS
    # ========================================================
    "detectors/__init__.py",
    "detectors/biceps_curl.py",
    "detectors/deadlift.py",
    "detectors/lunges.py",
    "detectors/plank.py",
    "detectors/pushup.py",
    "detectors/shoulder_press.py",
    "detectors/squat.py",

    # ========================================================
    # SERVICES
    # ========================================================
    "services/__init__.py",

    # --------------------------------------------------------
    # services/config
    # --------------------------------------------------------
    "services/config/workout_config.py",

    # --------------------------------------------------------
    # services/cv_implementation
    # --------------------------------------------------------
    "services/cv_implementation/__init__.py",
    "services/cv_implementation/frame_processor.py",

    # ========================================================
    # ML MODELS
    # ========================================================
    "ml_models/__init__.py",
    "ml_models/pose_landmarker_full.task",

    # ========================================================
    # FRONTEND
    # ========================================================

    # --------------------------------------------------------
    # frontend root
    # --------------------------------------------------------
    "frontend/.env.example",
    "frontend/.gitignore",
    "frontend/.oxlintrc.json",
    "frontend/index.html",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/README.md",
    "frontend/vite.config.js",

    # --------------------------------------------------------
    # frontend/public
    # --------------------------------------------------------
    "frontend/public/favicon.svg",
    "frontend/public/icons.svg",

    # --------------------------------------------------------
    # frontend/src
    # --------------------------------------------------------
    "frontend/src/App.jsx",
    "frontend/src/index.css",
    "frontend/src/main.jsx",

    # --------------------------------------------------------
    # frontend/src/assets
    # --------------------------------------------------------
    "frontend/src/assets/hero.png",
    "frontend/src/assets/vite.svg",

    # --------------------------------------------------------
    # frontend/src/components
    # --------------------------------------------------------
    "frontend/src/components/MetricsPanel.jsx",
    "frontend/src/components/PoseOverlay.jsx",
    "frontend/src/components/WorkoutHistory.jsx",

    # --------------------------------------------------------
    # frontend/src/lib
    # --------------------------------------------------------
    "frontend/src/lib/api.js",
    "frontend/src/lib/AuthContext.jsx",
    "frontend/src/lib/exerciseConfig.js",
    "frontend/src/lib/useCamera.js",

    # --------------------------------------------------------
    # frontend/src/pages
    # --------------------------------------------------------
    "frontend/src/pages/Dashboard.jsx",
    "frontend/src/pages/FaceAuth.jsx",
    "frontend/src/pages/Landing.jsx",
]


# ============================================================
# FOLDERS
# ============================================================

folders = [
    # Backend
    "backend/audio_cache",

    # Frontend
    "frontend/src/assets",
]


# ============================================================
# CREATE FILES
# ============================================================

for file in files:
    path = Path(file)

    # Create parent directories automatically
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create only if it doesn't already exist
    if not path.exists():
        path.touch()
        print(f"Created file: {path}")
    else:
        print(f"Already exists: {path}")


for folder in folders:
    path = Path(folder)

    path.mkdir(parents=True, exist_ok=True)

    print(f"Folder ready: {path}")


print("\n" + "=" * 60)
print("AI Gym Trainer project scaffold complete!")
print("=" * 60)
print("All existing files were preserved.")
print("Missing files/folders were created.")
print("=" * 60)