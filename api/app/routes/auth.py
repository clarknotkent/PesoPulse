from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware import get_current_user
from app.config import get_db

router = APIRouter()


@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)) -> dict:
    uid: str = current_user.get("uid", "")
    db = get_db()
    user_doc = db.collection("users").document(uid).get()

    profile: dict = {"uid": uid, "email": current_user.get("email"), "name": current_user.get("name")}
    if user_doc.exists:
        profile.update(user_doc.to_dict())

    return profile


@router.post("/register")
async def register_user(current_user: dict = Depends(get_current_user)) -> dict:
    uid: str = current_user.get("uid", "")
    db = get_db()
    ref = db.collection("users").document(uid)

    if not ref.get().exists:
        existing_users = list(db.collection("users").get())
        if len(existing_users) >= 5:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Maximum 5 users allowed")
        ref.set({"uid": uid, "email": current_user.get("email"), "name": current_user.get("name")})

    return {"registered": True, "uid": uid}
