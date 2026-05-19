from datetime import date, datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel, ConfigDict, Field

from app.config import get_db
from app.middleware import get_current_user, require_owner, require_owner_or_viewer

router = APIRouter()

_PH_TZ = ZoneInfo("Asia/Manila")


class GoalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    target: float = Field(gt=0)
    deadline: str
    category: str
    startDate: str | None = None


class GoalUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    target: float | None = Field(default=None, gt=0)
    deadline: str | None = None
    category: str | None = None
    startDate: str | None = None


def _parse_iso(d: str) -> date:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date: {d}")


def _today_ph() -> date:
    return datetime.now(_PH_TZ).date()


def _compute_progress(owner_id: str, goal: dict) -> dict:
    db = get_db()
    start = goal.get("startDate") or goal.get("createdAt", "")[:10]
    deadline = goal["deadline"]

    docs = (
        db.collection("transactions")
        .where(filter=FieldFilter("userId", "==", owner_id))
        .where(filter=FieldFilter("category", "==", goal["category"]))
        .get()
    )

    progress = 0.0
    for d in docs:
        t = d.to_dict()
        if t.get("type") != "income":
            continue
        date_s = t.get("date", "")
        if start <= date_s <= deadline:
            progress += float(t.get("amount", 0))

    target = float(goal["target"])
    pct = (progress / target * 100.0) if target > 0 else 0.0
    today = _today_ph()
    deadline_d = _parse_iso(deadline)
    days_left = max(0, (deadline_d - today).days)

    return {
        **goal,
        "progress": round(progress, 2),
        "pctComplete": round(pct, 2),
        "daysLeft": days_left,
    }


@router.get("/{owner_id}")
async def list_goals(
    owner_id: str,
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    await require_owner_or_viewer(owner_id, current_user)
    db = get_db()
    docs = db.collection("goals").where(filter=FieldFilter("userId", "==", owner_id)).get()
    return [_compute_progress(owner_id, d.to_dict()) for d in docs]


@router.post("/{owner_id}", status_code=status.HTTP_201_CREATED)
async def create_goal(
    owner_id: str,
    payload: GoalCreate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    _parse_iso(payload.deadline)
    if payload.startDate:
        _parse_iso(payload.startDate)
    db = get_db()
    goal_id = str(uuid4())
    today = _today_ph().strftime("%Y-%m-%d")
    goal = {
        "id": goal_id,
        "userId": owner_id,
        "name": payload.name,
        "target": payload.target,
        "deadline": payload.deadline,
        "category": payload.category,
        "startDate": payload.startDate or today,
        "createdAt": datetime.now(_PH_TZ).isoformat(),
    }
    db.collection("goals").document(goal_id).set(goal)
    return _compute_progress(owner_id, goal)


@router.put("/{owner_id}/{goal_id}")
async def update_goal(
    owner_id: str,
    goal_id: str,
    payload: GoalUpdate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    db = get_db()
    ref = db.collection("goals").document(goal_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get("userId") != owner_id:
        raise HTTPException(status_code=404, detail="Goal not found")
    updates = payload.model_dump(exclude_unset=True)
    if "deadline" in updates:
        _parse_iso(updates["deadline"])
    if updates.get("startDate"):
        _parse_iso(updates["startDate"])
    ref.update(updates)
    return _compute_progress(owner_id, {**doc.to_dict(), **updates})


@router.delete("/{owner_id}/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    owner_id: str,
    goal_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    await require_owner(owner_id, current_user)
    db = get_db()
    ref = db.collection("goals").document(goal_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get("userId") != owner_id:
        raise HTTPException(status_code=404, detail="Goal not found")
    ref.delete()
