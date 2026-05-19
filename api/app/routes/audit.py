from fastapi import APIRouter, Depends, Query
from google.cloud.firestore_v1.base_query import FieldFilter

from app.config import get_db
from app.middleware import get_current_user, require_owner

router = APIRouter()


@router.get("/{owner_id}")
async def list_audit_log(
    owner_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    await require_owner(owner_id, current_user)

    db = get_db()
    docs = (
        db.collection("audit_logs")
        .where(filter=FieldFilter("targetOwnerId", "==", owner_id))
        .order_by("ts", direction="DESCENDING")
        .limit(limit)
        .get()
    )
    return [d.to_dict() for d in docs]
