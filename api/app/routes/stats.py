from datetime import date, datetime, timedelta
from typing import Literal, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from google.cloud.firestore_v1.base_query import FieldFilter

from app.config import get_db
from app.middleware import get_current_user, require_owner_or_viewer
from app.routes.notifications import maybe_send_digest

router = APIRouter()

_PH_TZ = ZoneInfo("Asia/Manila")

Period = Literal["week", "month", "year"]


def _parse_iso(d: str) -> date:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date: {d}")


def _today_ph() -> date:
    return datetime.now(_PH_TZ).date()


def _period_bounds(period: Period, anchor: date) -> tuple[date, date]:
    if period == "week":
        weekday = anchor.weekday()
        start = anchor - timedelta(days=weekday)
        end = start + timedelta(days=6)
    elif period == "month":
        start = anchor.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
    else:
        start = anchor.replace(month=1, day=1)
        end = anchor.replace(month=12, day=31)
    return start, end


def _prev_period_anchor(period: Period, anchor: date) -> date:
    if period == "week":
        return anchor - timedelta(days=7)
    if period == "month":
        if anchor.month == 1:
            return anchor.replace(year=anchor.year - 1, month=12)
        return anchor.replace(month=anchor.month - 1)
    return anchor.replace(year=anchor.year - 1)


def _fetch_txns(owner_id: str, start: date, end: date) -> list[dict]:
    db = get_db()
    start_s = start.strftime("%Y-%m-%d")
    end_s = end.strftime("%Y-%m-%d")
    docs = (
        db.collection("transactions")
        .where(filter=FieldFilter("userId", "==", owner_id))
        .get()
    )
    return [
        d.to_dict()
        for d in docs
        if start_s <= d.to_dict().get("date", "") <= end_s
    ]


def _totals(txns: list[dict]) -> dict:
    income = sum(t["amount"] for t in txns if t["type"] == "income")
    expense = sum(t["amount"] for t in txns if t["type"] == "expense")
    net = income - expense
    savings_rate = (net / income * 100.0) if income > 0 else 0.0
    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "net": round(net, 2),
        "savingsRate": round(savings_rate, 2),
    }


@router.get("/{owner_id}/all-time")
async def all_time(
    owner_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner_or_viewer(owner_id, current_user)
    db = get_db()
    docs = (
        db.collection("transactions")
        .where(filter=FieldFilter("userId", "==", owner_id))
        .get()
    )
    txns = [d.to_dict() for d in docs]
    income = sum(t["amount"] for t in txns if t.get("type") == "income")
    expense = sum(t["amount"] for t in txns if t.get("type") == "expense")
    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "net": round(income - expense, 2),
    }


@router.get("/{owner_id}/summary")
async def summary(
    owner_id: str,
    period: Period = Query("month"),
    anchor: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner_or_viewer(owner_id, current_user)
    anchor_date = _parse_iso(anchor) if anchor else _today_ph()
    start, end = _period_bounds(period, anchor_date)
    txns = _fetch_txns(owner_id, start, end)
    current = _totals(txns)

    prev_anchor = _prev_period_anchor(period, anchor_date)
    prev_start, prev_end = _period_bounds(period, prev_anchor)
    prev_txns = _fetch_txns(owner_id, prev_start, prev_end)
    prev = _totals(prev_txns)

    delta = {
        "income": round(current["income"] - prev["income"], 2),
        "expense": round(current["expense"] - prev["expense"], 2),
        "net": round(current["net"] - prev["net"], 2),
    }

    if current_user.get("uid") == owner_id:
        try:
            maybe_send_digest(owner_id, current, period)
        except Exception:
            pass

    return {
        **current,
        "deltaVsPrev": delta,
        "range": {"from": start.strftime("%Y-%m-%d"), "to": end.strftime("%Y-%m-%d")},
    }


@router.get("/{owner_id}/categories")
async def categories_breakdown(
    owner_id: str,
    period: Period = Query("month"),
    anchor: Optional[str] = Query(None),
    type: Literal["income", "expense"] = Query("expense"),
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    await require_owner_or_viewer(owner_id, current_user)
    anchor_date = _parse_iso(anchor) if anchor else _today_ph()
    start, end = _period_bounds(period, anchor_date)
    txns = [t for t in _fetch_txns(owner_id, start, end) if t["type"] == type]

    totals: dict[str, float] = {}
    for t in txns:
        cat = t.get("category", "Uncategorized")
        totals[cat] = totals.get(cat, 0.0) + t["amount"]

    grand = sum(totals.values()) or 1.0
    rows = [
        {"category": cat, "total": round(amt, 2), "pct": round(amt / grand * 100.0, 2)}
        for cat, amt in totals.items()
    ]
    rows.sort(key=lambda r: r["total"], reverse=True)
    return rows


@router.get("/{owner_id}/trend")
async def trend(
    owner_id: str,
    period: Period = Query("month"),
    anchor: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    await require_owner_or_viewer(owner_id, current_user)
    anchor_date = _parse_iso(anchor) if anchor else _today_ph()
    start, end = _period_bounds(period, anchor_date)
    txns = _fetch_txns(owner_id, start, end)

    buckets: dict[str, dict] = {}

    if period in ("week", "month"):
        cursor = start
        while cursor <= end:
            key = cursor.strftime("%Y-%m-%d")
            buckets[key] = {"bucket": key, "income": 0.0, "expense": 0.0}
            cursor += timedelta(days=1)
        for t in txns:
            key = t["date"]
            if key in buckets:
                buckets[key][t["type"]] += t["amount"]
    else:
        for month in range(1, 13):
            key = f"{anchor_date.year}-{month:02d}"
            buckets[key] = {"bucket": key, "income": 0.0, "expense": 0.0}
        for t in txns:
            key = t["date"][:7]
            if key in buckets:
                buckets[key][t["type"]] += t["amount"]

    return [
        {
            "bucket": b["bucket"],
            "income": round(b["income"], 2),
            "expense": round(b["expense"], 2),
        }
        for b in buckets.values()
    ]
