# Kinetic — React + FastAPI Migration

This documents the migration of Kinetic's Streamlit UI to a React frontend,
with face-unlock authentication adapted from the SnapClass biometric
attendance project.

## Architecture

```
React (Vite)  ──HTTP/JSON──►  FastAPI (backend/)  ──►  Existing ML pipeline
     │                              │                    (MediaPipe PoseLandmarker
     │                              │                     + detectors/*.py,
     │                              │                     unchanged)
     │                              │
     │                              └──►  Supabase (gym_users, gym_exercises)
     │
     └── webcam frames captured client-side, POSTed as JPEG every ~200ms
         (no WebSocket/WebRTC signaling — kept deliberately simple)
```

**Face auth → Project 2 auth.** Project 1 (SnapClass) has no reusable
Supabase Auth/session system to copy — its "auth" is a hand-rolled
bcrypt/username check for teachers only, and student face recognition is
used to mark attendance against a pre-enrolled classroom roster, not to log
anyone in. What _is_ reusable is the working embedding pipeline: MTCNN face
detection + InceptionResnetV1 (`vggface2`) embeddings + L2 distance matching
(`0.9` threshold). `backend/auth_face.py` repurposes that exact pipeline as a
direct face-unlock gate: `enroll()` stores one embedding per username in a
new `gym_users` Supabase table, `verify()` finds the closest match.

**Real-time pipeline.** The original `VideoProcessorClass` was a persistent
`streamlit-webrtc` object with `detect_for_video()`. Since React talks to the
backend over stateless HTTP, `backend/pose_processor.py` swaps
`RunningMode.VIDEO` for `RunningMode.IMAGE` (`.detect()` on each independent
frame) — the only real change to the CV logic. Everything else (`detectors/*.py`,
`AngleSmoother`, `POSE_CONNECTIONS`, confidence thresholds) is untouched.
Rep counts persist across frames via `backend/session_manager.py`, which
keeps one detector instance alive per `session_id` in memory — the HTTP
equivalent of the old per-connection `VideoProcessorClass` instance.

**Persistence.** `services/persistence/exercise_repository.py` used local
SQLite. Per the "Supabase only" requirement, `backend/exercise_repository.py`
reimplements the identical upsert-per-day logic against a new
`gym_exercises` Supabase table instead.

## What changed

### Added

- `backend/` — new FastAPI service: `main.py` (routes), `auth_face.py`
  (face enroll/verify), `pose_processor.py` (frame → metrics, adapted from
  `exercise_video_processor.py`), `session_manager.py` (per-session detector
  state), `exercise_repository.py` (Supabase persistence), `supabase_client.py`.
- `backend/supabase_schema.sql` — two new tables, additive only, nothing in
  Project 1's schema touched.
- `frontend/` — new Vite + React app: `Landing.jsx`, `FaceAuth.jsx`,
  `Dashboard.jsx`, `PoseOverlay.jsx` (canvas skeleton draw from
  backend-returned landmarks), `MetricsPanel.jsx`, `WorkoutHistory.jsx`,
  `useCamera.js`, `AuthContext.jsx`, `api.js`.

### Not changed

- `detectors/*.py`, `core/base_exercise.py`, `services/config/workout_config.py`,
  `ml_models/pose_landmarker_full.task` — the actual AI engine, byte-for-byte.
- Project 1 is untouched entirely; only its face-embedding _approach_ was
  ported, since Project 2 needed its own single-user auth table.

### Removed from the live path (kept in the repo)

- The Streamlit UI (`main.py`, `components/*`, `services/auth/login_wall.py`,
  `services/ui/*`) is superseded by `frontend/` but left in place — it's not
  wired into the new run path and can be deleted once you're happy with the
  React version.

## Run it

**Backend**

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SUPABASE_URL / SUPABASE_KEY (anon key only)
# run backend/supabase_schema.sql in the Supabase SQL editor first
uvicorn backend.main:app --reload --port 8000   # run from the project root
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL=http://localhost:8000
npm run dev
```

## Environment variables

| Var               | Where           | Purpose                                               |
| ----------------- | --------------- | ----------------------------------------------------- |
| `SUPABASE_URL`    | backend `.env`  | Supabase project URL                                  |
| `SUPABASE_KEY`    | backend `.env`  | **anon/public** key only — never the service-role key |
| `FRONTEND_ORIGIN` | backend `.env`  | CORS allow-list for the Vite origin                   |
| `VITE_API_URL`    | frontend `.env` | Backend base URL                                      |

## Testing performed

- `python -m py_compile` on every new backend module — all pass.
- FastAPI app imported and every route listed via `TestClient` (with
  `facenet_pytorch` mocked, since `torch`/`facenet-pytorch` could not be
  installed in this sandbox — disk space ran out mid-download). `/api/health`
  and `/api/exercises` were hit live and returned correct JSON.
- `npm run build` in `frontend/` — production build succeeds
  (`vite build` → `dist/`, ~91 KB gzipped JS).
- **Not yet verified in this environment** (needs a machine with more disk
  and a real webcam/Supabase project): end-to-end face enroll/verify against
  a live Supabase table, live frame-polling against a running backend, and
  the actual rep-counting accuracy of `detect()` in `IMAGE` mode vs the
  original `detect_for_video()` mode — logically equivalent per-frame, but
  worth a manual pass with real footage before you demo it.

## Resume / LinkedIn bullets

- Migrated a Streamlit computer-vision fitness app to a production-style
  React + FastAPI architecture, replacing in-process video callbacks with a
  stateless frame-polling REST API while preserving the existing MediaPipe
  pose-estimation and rep-counting pipeline unchanged.
- Implemented face-unlock authentication using MTCNN face detection and a
  FaceNet (InceptionResnetV1) embedding pipeline with L2-distance matching,
  adapted from a separate biometric-attendance system into a single-user
  auth flow backed by Supabase.
- Designed a session-scoped in-memory state layer so per-user rep/set
  counters persist correctly across stateless HTTP requests, mirroring the
  lifecycle of the original long-lived WebRTC video processor.
- Built a responsive, dark-mode React dashboard with live camera skeleton
  overlays rendered from server-side pose landmarks, real-time form
  feedback, and Supabase-backed workout history.
