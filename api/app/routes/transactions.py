from datetime import date as date_cls, datetime, timezone
from typing import Literal, Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import get_db
from app.middleware import get_current_user, require_owner, require_owner_or_viewer
from app.routes.recurring import materialize_recurring
from app.routes.budgets import _build_budget_view, _txn_period_anchor
from app.routes.notifications import send_overspend_push

router = APIRouter()

_PH_TZ = ZoneInfo("Asia/Manila")


def _validate_iso_date(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value
    try:
        date_cls.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("date must be ISO YYYY-MM-DD") from exc
    return value


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: str
    notes: Optional[str] = None
    date: Optional[str] = None

    @field_validator("date")
    @classmethod
    def _check_date(cls, v: Optional[str]) -> Optional[str]:
        return _validate_iso_date(v)


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[str] = None

    @field_validator("date")
    @classmethod
    def _check_date(cls, v: Optional[str]) -> Optional[str]:
        return _validate_iso_date(v)


@router.get("/{owner_id}")
async def list_transactions(
    owner_id: str,
    from_: Optional[str] = Query(default=None, alias="from"),
    to: Optional[str] = None,
    type: Optional[Literal["income", "expense"]] = None,
    category: Optional[str] = None,
    minAmount: Optional[float] = None,
    maxAmount: Optional[float] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    await require_owner_or_viewer(owner_id, current_user)

    if current_user.get("uid") == owner_id:
        try:
            materialize_recurring(owner_id)
        except Exception:
            pass

    db = get_db()
    docs = (
        db.collection("transactions")
        .where(filter=FieldFilter("userId", "==", owner_id))
        .order_by("date", direction="DESCENDING")
        .get()
    )
    rows = [doc.to_dict() for doc in docs]

    if from_:
        rows = [r for r in rows if (r.get("date") or "") >= from_]
    if to:
        rows = [r for r in rows if (r.get("date") or "") <= to]
    if type:
        rows = [r for r in rows if r.get("type") == type]
    if category:
        rows = [r for r in rows if r.get("category") == category]
    if minAmount is not None:
        rows = [r for r in rows if float(r.get("amount", 0)) >= minAmount]
    if maxAmount is not None:
        rows = [r for r in rows if float(r.get("amount", 0)) <= maxAmount]
    if search:
        needle = search.lower()
        rows = [
            r for r in rows
            if needle in (r.get("notes") or "").lower()
            or needle in (r.get("category") or "").lower()
        ]
    return rows


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
    today_ph = now_utc.astimezone(_PH_TZ).strftime("%Y-%m-%d")
    resolved_date = payload.date or today_ph
    transaction: dict = {
        "id": doc_id,
        "userId": owner_id,
        "amount": payload.amount,
        "type": payload.type,
        "date": resolved_date,
        "category": payload.category,
        "notes": payload.notes,
        "createdAt": now_utc.isoformat(),
    }
    db.collection("transactions").document(doc_id).set(transaction)

    if payload.type == "expense" and resolved_date == today_ph:
        try:
            for period in ("day", "week", "month"):
                anchor = _txn_period_anchor(period, transaction["date"])
                view = _build_budget_view(owner_id, period, anchor)
                cat_view = next((c for c in view["categories"] if c["category"] == payload.category), None)
                period_label = {"day": "daily", "week": "weekly", "month": "monthly"}[period]
                if cat_view and cat_view["overspent"]:
                    send_overspend_push(
                        owner_id,
                        f"{payload.category} ({period_label})",
                        cat_view["spent"],
                        cat_view["limit"] + cat_view["rollover"],
                    )
                elif view["total"]["overspent"] and view["total"]["limit"] > 0:
                    send_overspend_push(
                        owner_id,
                        f"total {period_label} budget",
                        view["total"]["spent"],
                        view["total"]["limit"] + view["total"]["rollover"],
                    )
        except Exception:
            pass

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
