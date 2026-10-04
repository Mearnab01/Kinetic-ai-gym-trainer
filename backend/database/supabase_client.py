import os

from dotenv import load_dotenv
from supabase import create_client, Client
 
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set (see backend/.env.example). "
        "Use the anon/public key here, never the service-role key."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)