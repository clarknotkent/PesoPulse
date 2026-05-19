from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel

from app.config import get_db
from app.middleware import get_current_user, require_owner

router = APIRouter()

SYSTEM_DEFAULTS: list[dict] = [
    {"id": "sys_food", "name": "Food", "icon": "🍔", "type": "expense", "isSystem": True},
    {"id": "sys_utilities", "name": "Utilities", "icon": "💡", "type": "expense", "isSystem": True},
    {"id": "sys_transport", "name": "Transport", "icon": "🚌", "type": "expense", "isSystem": True},
    {"id": "sys_allowance", "name": "Allowance", "icon": "💸", "type": "income", "isSystem": True},
    {"id": "sys_salary", "name": "Salary", "icon": "💼", "type": "income", "isSystem": True},
]


class CategoryCreate(BaseModel):
    name: str
    icon: str
    type: Literal["income", "expense"]


@router.get("/{owner_id}")
async def list_categories(owner_id: str, current_user: dict = Depends(get_current_user)) -> list[dict]:
    db = get_db()
    docs = db.collection("categories").where(filter=FieldFilter("userId", "==", owner_id)).get()
    custom: list[dict] = [{**doc.to_dict(), "isSystem": False} for doc in docs]
    return SYSTEM_DEFAULTS + custom


@router.post("/{owner_id}", status_code=status.HTTP_201_CREATED)
async def create_category(
    owner_id: str,
    payload: CategoryCreate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    db = get_db()
    doc_id = str(uuid4())
    category: dict = {
        "id": doc_id,
        "userId": owner_id,
        "name": payload.name,
        "icon": payload.icon,
        "type": payload.type,
    }
    db.collection("categories").document(doc_id).set(category)
    return {**category, "isSystem": False}


@router.delete("/{owner_id}/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    owner_id: str,
    category_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    await require_owner(owner_id, current_user)
    db = get_db()
    ref = db.collection("categories").document(category_id)
    doc = ref.get()

    if not doc.exists or doc.to_dict().get("userId") != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    ref.delete()
