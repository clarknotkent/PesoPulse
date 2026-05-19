from datetime import date, datetime, timedelta
from typing import Literal
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel, ConfigDict, Field

from app.config import get_db
from app.middleware import get_current_user, require_owner, require_owner_or_viewer

router = APIRouter()

_PH_TZ = ZoneInfo("Asia/Manila")
_TOTAL_KEY = "__total__"

Period = Literal["day", "week", "month"]


class BudgetUpsert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: float | None = Field(default=None, ge=0)
    categories: dict[str, float] | None = None


class BudgetCheckPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0)
    category: str
    date: str | None = None


def _today_ph() -> date:
    return datetime.now(_PH_TZ).date()


def _parse_iso(d: str) -> date:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date: {d}")


def _anchor_for(period: Period, d: date) -> str:
    """Canonical anchor string for the period containing date d."""
    if period == "day":
        return d.strftime("%Y-%m-%d")
    if period == "week":
        monday = d - timedelta(days=d.weekday())
        return monday.strftime("%Y-%m-%d")
    return d.replace(day=1).strftime("%Y-%m-%d")


def _resolve_anchor(period: Period, anchor: str | None) -> str:
    if anchor:
        return _anchor_for(period, _parse_iso(anchor))
    return _anchor_for(period, _today_ph())


def _period_bounds(period: Period, anchor: str) -> tuple[date, date]:
    a = _parse_iso(anchor)
    if period == "day":
        return a, a
    if period == "week":
        return a, a + timedelta(days=6)
    if a.month == 12:
        end = a.replace(year=a.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end = a.replace(month=a.month + 1, day=1) - timedelta(days=1)
    return a, end


def _next_anchor(period: Period, anchor: str) -> str:
    a = _parse_iso(anchor)
    if period == "day":
        return (a + timedelta(days=1)).strftime("%Y-%m-%d")
    if period == "week":
        return (a + timedelta(days=7)).strftime("%Y-%m-%d")
    if a.month == 12:
        nxt = a.replace(year=a.year + 1, month=1, day=1)
    else:
        nxt = a.replace(month=a.month + 1, day=1)
    return nxt.strftime("%Y-%m-%d")


def _anchors_between(start_anchor: str, end_anchor: str, period: Period) -> list[str]:
    out = [start_anchor]
    cur = start_anchor
    while cur < end_anchor:
        cur = _next_anchor(period, cur)
        out.append(cur)
        if len(out) > 520:
            break
    return out


def _doc_period_anchor(d: dict) -> tuple[Period, str]:
    """Backward-compat read: docs w/o `period` are monthly, `month` field = YYYY-MM."""
    if d.get("period") in ("week", "month"):
        return d["period"], d["anchor"]
    legacy_month = d.get("month")
    if legacy_month and len(legacy_month) == 7:
        return "month", f"{legacy_month}-01"
    if legacy_month and len(legacy_month) == 10:
        return "month", legacy_month
    return "month", _anchor_for("month", _today_ph())


def _all_budget_docs(owner_id: str) -> list[dict]:
    db = get_db()
    docs = db.collection("budgets").where(filter=FieldFilter("userId", "==", owner_id)).get()
    return [{**d.to_dict(), "_id": d.id} for d in docs]


def _all_txns(owner_id: str) -> list[dict]:
    db = get_db()
    docs = db.collection("transactions").where(filter=FieldFilter("userId", "==", owner_id)).get()
    return [d.to_dict() for d in docs]


def _txn_period_anchor(period: Period, txn_date: str) -> str:
    return _anchor_for(period, _parse_iso(txn_date))


def _compute_rollover(
    target_anchor: str,
    category: str,
    budget_by_anchor: dict[str, float],
    txns_by_anchor: dict[str, float],
    period: Period,
) -> dict:
    if not budget_by_anchor:
        spent = txns_by_anchor.get(target_anchor, 0.0)
        return {
            "category": category if category != _TOTAL_KEY else None,
            "limit": 0.0,
            "spent": round(spent, 2),
            "rollover": 0.0,
            "remaining": round(-spent, 2),
            "overspent": spent > 0,
        }

    start_anchor = min(budget_by_anchor.keys())
    if start_anchor > target_anchor:
        spent = txns_by_anchor.get(target_anchor, 0.0)
        return {
            "category": category if category != _TOTAL_KEY else None,
            "limit": 0.0,
            "spent": round(spent, 2),
            "rollover": 0.0,
            "remaining": round(-spent, 2),
            "overspent": spent > 0,
        }

    anchors = _anchors_between(start_anchor, target_anchor, period)

    carry = 0.0
    last_limit = 0.0
    last_spent = 0.0
    last_rollover_in = 0.0
    remaining = 0.0

    for i, a in enumerate(anchors):
        limit = budget_by_anchor.get(a, last_limit if i > 0 else 0.0)
        spent = txns_by_anchor.get(a, 0.0)
        available = limit + carry
        if a == target_anchor:
            last_limit = limit
            last_spent = spent
            last_rollover_in = carry
            remaining = available - spent
            break
        carry = max(0.0, available - spent)
        last_limit = limit

    return {
        "category": category if category != _TOTAL_KEY else None,
        "limit": round(last_limit, 2),
        "spent": round(last_spent, 2),
        "rollover": round(last_rollover_in, 2),
        "remaining": round(remaining, 2),
        "overspent": last_spent > (last_limit + last_rollover_in),
    }


def _build_budget_view(
    owner_id: str,
    period: Period,
    anchor: str,
    extra_amount: float = 0.0,
    extra_category: str | None = None,
) -> dict:
    docs = _all_budget_docs(owner_id)
    txns = [t for t in _all_txns(owner_id) if t.get("type") == "expense"]

    by_cat_budget: dict[str, dict[str, float]] = {}
    for d in docs:
        doc_period, doc_anchor = _doc_period_anchor(d)
        if doc_period != period:
            continue
        cat = d.get("category") or _TOTAL_KEY
        by_cat_budget.setdefault(cat, {})[doc_anchor] = float(d["limit"])

    by_cat_txn: dict[str, dict[str, float]] = {}
    total_by_anchor: dict[str, float] = {}
    for t in txns:
        date_s = t.get("date") or ""
        if not date_s:
            continue
        try:
            txn_anchor = _txn_period_anchor(period, date_s)
        except Exception:
            continue
        cat = t.get("category") or "Uncategorized"
        amt = float(t.get("amount", 0))
        by_cat_txn.setdefault(cat, {}).setdefault(txn_anchor, 0.0)
        by_cat_txn[cat][txn_anchor] += amt
        total_by_anchor.setdefault(txn_anchor, 0.0)
        total_by_anchor[txn_anchor] += amt

    if extra_amount > 0 and extra_category:
        by_cat_txn.setdefault(extra_category, {}).setdefault(anchor, 0.0)
        by_cat_txn[extra_category][anchor] += extra_amount
        total_by_anchor.setdefault(anchor, 0.0)
        total_by_anchor[anchor] += extra_amount

    total_view = _compute_rollover(
        anchor,
        _TOTAL_KEY,
        by_cat_budget.get(_TOTAL_KEY, {}),
        total_by_anchor,
        period,
    )

    all_cats = set(by_cat_budget.keys()) | set(by_cat_txn.keys())
    all_cats.discard(_TOTAL_KEY)

    category_views = []
    for cat in sorted(all_cats):
        v = _compute_rollover(
            anchor,
            cat,
            by_cat_budget.get(cat, {}),
            by_cat_txn.get(cat, {}),
            period,
        )
        if v["limit"] > 0 or v["spent"] > 0:
            category_views.append(v)

    start, end = _period_bounds(period, anchor)
    return {
        "period": period,
        "anchor": anchor,
        "range": {"from": start.strftime("%Y-%m-%d"), "to": end.strftime("%Y-%m-%d")},
        "total": total_view,
        "categories": category_views,
    }


@router.get("/{owner_id}")
async def get_budgets(
    owner_id: str,
    period: Period = Query("month"),
    anchor: str | None = Query(None),
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner_or_viewer(owner_id, current_user)
    resolved = _resolve_anchor(period, anchor)
    return _build_budget_view(owner_id, period, resolved)


@router.put("/{owner_id}")
async def upsert_budgets(
    owner_id: str,
    payload: BudgetUpsert,
    period: Period = Query("month"),
    anchor: str | None = Query(None),
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    resolved = _resolve_anchor(period, anchor)
    db = get_db()

    existing_docs = _all_budget_docs(owner_id)
    existing_map: dict[str, str] = {}
    for d in existing_docs:
        doc_period, doc_anchor = _doc_period_anchor(d)
        if doc_period != period or doc_anchor != resolved:
            continue
        cat_key = d.get("category") or _TOTAL_KEY
        existing_map[cat_key] = d["_id"]

    def _set(category_key: str | None, limit: float) -> None:
        key = category_key if category_key is not None else _TOTAL_KEY
        if key in existing_map:
            ref = db.collection("budgets").document(existing_map[key])
            if limit <= 0:
                ref.delete()
            else:
                ref.update({"limit": float(limit)})
        else:
            if limit <= 0:
                return
            doc_id = str(uuid4())
            db.collection("budgets").document(doc_id).set(
                {
                    "id": doc_id,
                    "userId": owner_id,
                    "period": period,
                    "anchor": resolved,
                    "category": None if category_key is None else category_key,
                    "limit": float(limit),
                    "createdAt": datetime.now(_PH_TZ).isoformat(),
                }
            )

    if payload.total is not None:
        _set(None, payload.total)

    if payload.categories:
        for cat, limit in payload.categories.items():
            _set(cat, float(limit))

    return _build_budget_view(owner_id, period, resolved)


@router.post("/{owner_id}/check")
async def check_overspend(
    owner_id: str,
    payload: BudgetCheckPayload,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    txn_date = payload.date or _today_ph().strftime("%Y-%m-%d")
    breaches: list[dict] = []

    for period in ("day", "week", "month"):
        anchor = _txn_period_anchor(period, txn_date)
        view = _build_budget_view(
            owner_id,
            period,
            anchor,
            extra_amount=payload.amount,
            extra_category=payload.category,
        )
        cat_view = next(
            (c for c in view["categories"] if c["category"] == payload.category),
            None,
        )
        if cat_view and cat_view["overspent"]:
            breaches.append(
                {
                    "period": period,
                    "scope": "category",
                    "category": payload.category,
                    "limit": cat_view["limit"],
                    "rollover": cat_view["rollover"],
                    "spent": cat_view["spent"],
                    "remaining": cat_view["remaining"],
                }
            )
        if view["total"]["overspent"] and view["total"]["limit"] > 0:
            breaches.append(
                {
                    "period": period,
                    "scope": "total",
                    "category": None,
                    "limit": view["total"]["limit"],
                    "rollover": view["total"]["rollover"],
                    "spent": view["total"]["spent"],
                    "remaining": view["total"]["remaining"],
                }
            )

    return {"wouldOverspend": len(breaches) > 0, "breaches": breaches}
