from datetime import date, datetime, timedelta
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

Frequency = Literal["daily", "weekly", "monthly", "yearly"]


class RecurringCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: str
    notes: Optional[str] = None
    frequency: Frequency
    startDate: str
    endDate: Optional[str] = None
    active: bool = True


class RecurringUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    frequency: Optional[Frequency] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    active: Optional[bool] = None


def _parse_iso(d: str) -> date:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date: {d}")


def _today_ph() -> date:
    return datetime.now(_PH_TZ).date()


def _next_due(prev: date, freq: Frequency) -> date:
    if freq == "daily":
        return prev + timedelta(days=1)
    if freq == "weekly":
        return prev + timedelta(days=7)
    if freq == "monthly":
        y = prev.year + (1 if prev.month == 12 else 0)
        m = 1 if prev.month == 12 else prev.month + 1
        day = min(prev.day, _days_in_month(y, m))
        return date(y, m, day)
    y = prev.year + 1
    day = prev.day
    if prev.month == 2 and prev.day == 29 and not _is_leap(y):
        day = 28
    return date(y, prev.month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1) - timedelta(days=1)).day


def _is_leap(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def materialize_recurring(owner_id: str) -> int:
    """Lazy auto-post. Returns count of txns created. Idempotent via lastPostedDate."""
    db = get_db()
    today = _today_ph()

    rules_docs = (
        db.collection("recurring_rules")
        .where(filter=FieldFilter("userId", "==", owner_id))
        .where(filter=FieldFilter("active", "==", True))
        .get()
    )

    created = 0
    for doc in rules_docs:
        rule = doc.to_dict()
        rule_id = rule["id"]
        freq: Frequency = rule["frequency"]
        start = _parse_iso(rule["startDate"])
        end = _parse_iso(rule["endDate"]) if rule.get("endDate") else None
        last_posted_s = rule.get("lastPostedDate")
        last_posted = _parse_iso(last_posted_s) if last_posted_s else None

        next_due = _next_due(last_posted, freq) if last_posted else start

        while next_due <= today and (end is None or next_due <= end):
            tx_id = str(uuid4())
            db.collection("transactions").document(tx_id).set({
                "id": tx_id,
                "userId": owner_id,
                "amount": float(rule["amount"]),
                "type": rule["type"],
                "date": next_due.strftime("%Y-%m-%d"),
                "category": rule["category"],
                "notes": rule.get("notes"),
                "recurringRuleId": rule_id,
                "createdAt": datetime.now(_PH_TZ).isoformat(),
            })
            created += 1
            last_posted = next_due
            next_due = _next_due(next_due, freq)

        if last_posted_s != (last_posted.strftime("%Y-%m-%d") if last_posted else None):
            db.collection("recurring_rules").document(rule_id).update({
                "lastPostedDate": last_posted.strftime("%Y-%m-%d") if last_posted else None,
            })

    return created


def upcoming_recurring(owner_id: str, days_ahead: int = 7) -> list[dict]:
    db = get_db()
    today = _today_ph()
    horizon = today + timedelta(days=days_ahead)

    rules_docs = (
        db.collection("recurring_rules")
        .where(filter=FieldFilter("userId", "==", owner_id))
        .where(filter=FieldFilter("active", "==", True))
        .get()
    )

    upcoming: list[dict] = []
    for doc in rules_docs:
        rule = doc.to_dict()
        freq: Frequency = rule["frequency"]
        start = _parse_iso(rule["startDate"])
        end = _parse_iso(rule["endDate"]) if rule.get("endDate") else None
        last_posted_s = rule.get("lastPostedDate")
        last_posted = _parse_iso(last_posted_s) if last_posted_s else None

        next_due = _next_due(last_posted, freq) if last_posted else start
        while next_due <= horizon and (end is None or next_due <= end):
            if next_due > today:
                upcoming.append({
                    "ruleId": rule["id"],
                    "amount": float(rule["amount"]),
                    "type": rule["type"],
                    "category": rule["category"],
                    "notes": rule.get("notes"),
                    "dueDate": next_due.strftime("%Y-%m-%d"),
                })
            next_due = _next_due(next_due, freq)

    upcoming.sort(key=lambda u: u["dueDate"])
    return upcoming


@router.get("/{owner_id}")
async def list_rules(
    owner_id: str,
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    await require_owner_or_viewer(owner_id, current_user)
    db = get_db()
    docs = (
        db.collection("recurring_rules")
        .where(filter=FieldFilter("userId", "==", owner_id))
        .get()
    )
    return [d.to_dict() for d in docs]


@router.get("/{owner_id}/upcoming")
async def upcoming(
    owner_id: str,
    days: int = 7,
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    await require_owner_or_viewer(owner_id, current_user)
    return upcoming_recurring(owner_id, days_ahead=days)


@router.post("/{owner_id}", status_code=status.HTTP_201_CREATED)
async def create_rule(
    owner_id: str,
    payload: RecurringCreate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    _parse_iso(payload.startDate)
    if payload.endDate:
        _parse_iso(payload.endDate)
    db = get_db()
    rule_id = str(uuid4())
    rule = {
        "id": rule_id,
        "userId": owner_id,
        "amount": payload.amount,
        "type": payload.type,
        "category": payload.category,
        "notes": payload.notes,
        "frequency": payload.frequency,
        "startDate": payload.startDate,
        "endDate": payload.endDate,
        "active": payload.active,
        "lastPostedDate": None,
        "createdAt": datetime.now(_PH_TZ).isoformat(),
    }
    db.collection("recurring_rules").document(rule_id).set(rule)
    return rule


@router.put("/{owner_id}/{rule_id}")
async def update_rule(
    owner_id: str,
    rule_id: str,
    payload: RecurringUpdate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    db = get_db()
    ref = db.collection("recurring_rules").document(rule_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get("userId") != owner_id:
        raise HTTPException(status_code=404, detail="Recurring rule not found")
    updates = payload.model_dump(exclude_unset=True)
    if "startDate" in updates:
        _parse_iso(updates["startDate"])
    if updates.get("endDate"):
        _parse_iso(updates["endDate"])
    ref.update(updates)
    return {**doc.to_dict(), **updates}


@router.delete("/{owner_id}/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    owner_id: str,
    rule_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    await require_owner(owner_id, current_user)
    db = get_db()
    ref = db.collection("recurring_rules").document(rule_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get("userId") != owner_id:
        raise HTTPException(status_code=404, detail="Recurring rule not found")
    ref.delete()
