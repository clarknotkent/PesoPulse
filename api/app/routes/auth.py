from fastapi import APIRouter, Depends, HTTPException, Request, status
from firebase_admin import auth as fb_auth
from pydantic import BaseModel
from email_validator import EmailNotValidError, validate_email
from app.middleware import get_current_user
from app.config import get_db
from app.audit import audit_log

router = APIRouter()

MAX_USERS = 5


class RegisterResponse(BaseModel):
    registered: bool
    uid: str


@router.get("/me")
async def get_current_user_profile(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> dict:
    uid: str = current_user.get("uid", "")
    db = get_db()
    user_doc = db.collection("users").document(uid).get()

    profile: dict = {
        "uid": uid,
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "emailVerified": current_user.get("email_verified", False),
    }
    if user_doc.exists:
        profile.update(user_doc.to_dict())

    return profile


@router.post("/register", response_model=RegisterResponse)
async def register_user(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> RegisterResponse:
    uid: str = current_user.get("uid", "")
    email = current_user.get("email")
    if email:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid_email",
            )

    db = get_db()
    ref = db.collection("users").document(uid)
    snapshot = ref.get()

    if not snapshot.exists:
        existing = list(db.collection("users").stream())
        if len(existing) >= MAX_USERS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="user_cap_reached",
            )
        ref.set({
            "uid": uid,
            "email": email,
            "name": current_user.get("name"),
            "emailVerifiedAt": None,
        })
        audit_log(
            actor_uid=uid,
            action="auth.register",
            target_owner_id=uid,
            target_doc_id=uid,
            request=request,
            metadata={"email": email},
        )

    return RegisterResponse(registered=True, uid=uid)


@router.post("/revoke-tokens", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_tokens(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> None:
    uid: str = current_user.get("uid", "")
    try:
        fb_auth.revoke_refresh_tokens(uid)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="revoke_failed",
        )
    audit_log(
        actor_uid=uid,
        action="auth.revoke_tokens",
        target_owner_id=uid,
        target_doc_id=uid,
        request=request,
    )
    return None
