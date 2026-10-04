# Kinetic Backend

FastAPI service wrapping the existing pose-detection pipeline, face-unlock
auth (adapted from Project 1), and Supabase persistence.

See `/REACT_MIGRATION.md` at the repo root for full architecture notes and
run instructions.

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env   # fill in SUPABASE_URL / SUPABASE_KEY / GROQ_API_KEY
uvicorn backend.main:app --reload --port 8000   # run from the project root
```

## Deploying to Hugging Face Spaces

1. Create a new Space → SDK = **Docker**.
2. Push this repo (`backend/`, `detectors/`, `core/`, `services/`, `ml_models/`).
3. Space Settings → **Secrets** → add `SUPABASE_URL`, `SUPABASE_KEY`,
   `FRONTEND_ORIGIN`, `GROQ_API_KEY`.
4. Your API will be live at `https://<username>-<space-name>.hf.space`.
