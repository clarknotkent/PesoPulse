from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from google.cloud.firestore_v1.base_query import FieldFilter
from app.config import get_db

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    try:
        decoded: dict = auth.verify_id_token(credentials.credentials)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def require_owner(target_owner_id: str, current_user: dict) -> None:
    if current_user.get("uid") != target_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mutation forbidden: you are not the owner",
        )


async def require_owner_or_viewer(
    target_owner_id: str, current_user: dict
) -> None:
    uid: str = current_user.get("uid", "")
    if uid == target_owner_id:
        return

    db = get_db()
    results = (
        db.collection("sharing_permissions")
        .where(filter=FieldFilter("ownerId", "==", target_owner_id))
        .where(filter=FieldFilter("viewerId", "==", uid))
        .limit(1)
        .get()
    )
    if results:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )
