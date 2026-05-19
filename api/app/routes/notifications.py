from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, status
from firebase_admin import messaging
from pydantic import BaseModel, ConfigDict

from app.config import get_db
from app.middleware import get_current_user, require_owner

router = APIRouter()

_PH_TZ = ZoneInfo("Asia/Manila")


class TokenRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fcmToken: str
    platform: str | None = "web"


def _tokens_collection(owner_id: str):
    db = get_db()
    return db.collection("users").document(owner_id).collection("fcm_tokens")


def get_user_tokens(owner_id: str) -> list[str]:
    docs = _tokens_collection(owner_id).get()
    return [d.to_dict().get("fcmToken") for d in docs if d.to_dict().get("fcmToken")]


def _send(tokens: list[str], title: str, body: str, data: dict | None = None) -> int:
    if not tokens:
        return 0
    try:
        msg = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
        )
        resp = messaging.send_each_for_multicast(msg)
        return resp.success_count
    except Exception:
        return 0


def send_overspend_push(owner_id: str, category: str, spent: float, limit: float) -> int:
    tokens = get_user_tokens(owner_id)
    title = f"Over budget on {category}"
    body = f"₱{spent:.0f} / ₱{limit:.0f}"
    return _send(tokens, title, body, {"type": "overspend", "category": category})


def send_digest_push(owner_id: str, kind: str, income: float, expense: float, period_label: str) -> int:
    tokens = get_user_tokens(owner_id)
    net = income - expense
    sign = "" if net >= 0 else "-"
    title = f"{kind.capitalize()} digest · {period_label}"
    body = f"Spent ₱{expense:.0f} · Income ₱{income:.0f} · Net {sign}₱{abs(net):.0f}"
    return _send(tokens, title, body, {"type": "digest", "kind": kind})


def maybe_send_digest(owner_id: str, summary_today: dict, period: str) -> None:
    """Lazy digest trigger called on stats summary GET.
    period = 'week' or 'month'.
    """
    if period not in ("week", "month"):
        return
    db = get_db()
    today = datetime.now(_PH_TZ).date()

    if period == "week" and today.weekday() != 0:
        return
    if period == "month" and today.day != 1:
        return

    user_ref = db.collection("users").document(owner_id)
    user_doc = user_ref.get()
    user_data = user_doc.to_dict() if user_doc.exists else {}
    last_sent = user_data.get("lastDigestSent", {}) if user_data else {}

    key = "weekly" if period == "week" else "monthly"
    today_s = today.strftime("%Y-%m-%d")
    if last_sent.get(key) == today_s:
        return

    if period == "week":
        end_d = today - timedelta(days=1)
        start_d = end_d - timedelta(days=6)
        label = f"{start_d.strftime('%b %d')}–{end_d.strftime('%b %d')}"
    else:
        if today.month == 1:
            prev_year = today.year - 1
            prev_month = 12
        else:
            prev_year = today.year
            prev_month = today.month - 1
        label = datetime(prev_year, prev_month, 1).strftime("%B %Y")

    send_digest_push(
        owner_id,
        kind=key.rstrip("ly"),
        income=summary_today.get("income", 0.0),
        expense=summary_today.get("expense", 0.0),
        period_label=label,
    )

    last_sent[key] = today_s
    user_ref.set({"lastDigestSent": last_sent}, merge=True)


@router.post("/{owner_id}/register", status_code=status.HTTP_201_CREATED)
async def register_token(
    owner_id: str,
    payload: TokenRegister,
    current_user: dict = Depends(get_current_user),
) -> dict:
    await require_owner(owner_id, current_user)
    safe_id = payload.fcmToken.replace("/", "_").replace(":", "_")[:200]
    _tokens_collection(owner_id).document(safe_id).set(
        {
            "fcmToken": payload.fcmToken,
            "platform": payload.platform,
            "registeredAt": datetime.now(_PH_TZ).isoformat(),
        }
    )
    return {"ok": True}


@router.delete("/{owner_id}/token/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_token(
    owner_id: str,
    token: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    await require_owner(owner_id, current_user)
    safe_id = token.replace("/", "_").replace(":", "_")[:200]
    ref = _tokens_collection(owner_id).document(safe_id)
    if ref.get().exists:
        ref.delete()
