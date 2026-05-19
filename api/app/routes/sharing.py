from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from google.cloud.firestore_v1.base_query import FieldFilter
from app.config import get_db
from app.middleware import get_current_user, require_owner
from app.audit import audit_log

router = APIRouter()


class ShareGrant(BaseModel):
    viewerEmail: str


@router.get("/{owner_id}")
async def list_grants(
    owner_id: str,
    current_user: dict = Depends(get_current_user),
) -> list:
    await require_owner(owner_id, current_user)
    db = get_db()
    docs = db.collection("sharing_permissions").where(filter=FieldFilter("ownerId", "==", owner_id)).get()
    return [doc.to_dict() for doc in docs]


@router.post("/{owner_id}", status_code=status.HTTP_201_CREATED)
async def grant_access(
    request: Request,
    owner_id: str,
    payload: ShareGrant,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    db = get_db()

    try:
        viewer = firebase_auth.get_user_by_email(payload.viewerEmail)
    except firebase_auth.UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if viewer.uid == owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot share with yourself")

    existing = (
        db.collection("sharing_permissions")
        .where(filter=FieldFilter("ownerId", "==", owner_id))
        .where(filter=FieldFilter("viewerId", "==", viewer.uid))
        .limit(1)
        .get()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already has access")

    doc = {
        "id": str(uuid4()),
        "ownerId": owner_id,
        "viewerId": viewer.uid,
        "viewerEmail": payload.viewerEmail,
        "grantedAt": datetime.now(timezone.utc).isoformat(),
    }
    db.collection("sharing_permissions").document(doc["id"]).set(doc)
    audit_log(
        actor_uid=current_user.get("uid", ""),
        action="sharing.grant",
        target_owner_id=owner_id,
        target_doc_id=doc["id"],
        request=request,
        metadata={"viewerUid": viewer.uid, "viewerEmail": payload.viewerEmail},
    )
    return doc


@router.delete("/{owner_id}/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_access(
    request: Request,
    owner_id: str,
    permission_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    await require_owner(owner_id, current_user)
    db = get_db()

    ref = db.collection("sharing_permissions").document(permission_id)
    doc = ref.get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    if doc.to_dict().get("ownerId") != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    payload = doc.to_dict() or {}
    ref.delete()
    audit_log(
        actor_uid=current_user.get("uid", ""),
        action="sharing.revoke",
        target_owner_id=owner_id,
        target_doc_id=permission_id,
        request=request,
        metadata={"viewerUid": payload.get("viewerId"), "viewerEmail": payload.get("viewerEmail")},
    )
