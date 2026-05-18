import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

_firebase_app: firebase_admin.App | None = None
_db: firestore.Client | None = None


def _resolve_service_account_path() -> Path:
    raw = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "./api/serviceAccountKey.json")
    p = Path(raw)
    if not p.is_absolute():
        p = (_PROJECT_ROOT / p).resolve()
    if not p.exists():
        fallback = _PROJECT_ROOT / "api" / "serviceAccountKey.json"
        if fallback.exists():
            p = fallback
    return p


def get_firebase_app() -> firebase_admin.App:
    global _firebase_app
    if _firebase_app is None:
        path = _resolve_service_account_path()
        if not path.exists():
            raise FileNotFoundError(
                f"Firebase service account not found at {path}. "
                "Set FIREBASE_SERVICE_ACCOUNT_PATH in .env."
            )
        cred = credentials.Certificate(str(path))
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def get_db() -> firestore.Client:
    global _db
    if _db is None:
        get_firebase_app()
        _db = firestore.client()
    return _db
