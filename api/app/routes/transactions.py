from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel, ConfigDict, Field

from app.config import get_db
from app.middleware import get_current_user, require_owner, require_owner_or_viewer

router = APIRouter()

_PH_TZ = ZoneInfo("Asia/Manila")


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: str
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    notes: Optional[str] = None


@router.get("/{owner_id}")
async def list_transactions(
    owner_id: str, current_user: dict = Depends(get_current_user)
) -> list[dict]:
    await require_owner_or_viewer(owner_id, current_user)
    db = get_db()
    docs = (
        db.collection("transactions")
        .where(filter=FieldFilter("userId", "==", owner_id))
        .order_by("date", direction="DESCENDING")
        .get()
    )
    return [doc.to_dict() for doc in docs]


@router.post("/{owner_id}", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    owner_id: str,
    payload: TransactionCreate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    db = get_db()
    doc_id = str(uuid4())
    now_utc = datetime.now(timezone.utc)
    transaction: dict = {
        "id": doc_id,
        "userId": owner_id,
        "amount": payload.amount,
        "type": payload.type,
        "date": now_utc.astimezone(_PH_TZ).strftime("%Y-%m-%d"),
        "category": payload.category,
        "notes": payload.notes,
        "createdAt": now_utc.isoformat(),
    }
    db.collection("transactions").document(doc_id).set(transaction)
    return transaction


@router.put("/{owner_id}/{transaction_id}")
async def update_transaction(
    owner_id: str,
    transaction_id: str,
    payload: TransactionUpdate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    db = get_db()
    ref = db.collection("transactions").document(transaction_id)
    doc = ref.get()

    if not doc.exists or doc.to_dict().get("userId") != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    updates = payload.model_dump(exclude_unset=True)
    ref.update(updates)
    return {**doc.to_dict(), **updates}


@router.delete("/{owner_id}/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    owner_id: str,
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    await require_owner(owner_id, current_user)
    db = get_db()
    ref = db.collection("transactions").document(transaction_id)
    doc = ref.get()

    if not doc.exists or doc.to_dict().get("userId") != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    ref.delete()
