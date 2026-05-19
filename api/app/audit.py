from __future__ import annotations
import ipaddress
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4
from fastapi import Request
from google.cloud import firestore
from app.config import get_db

_logger = logging.getLogger("pesopulse.audit")

AUDIT_COLLECTION = "audit_logs"


def _client_ip(request: Optional[Request]) -> Optional[str]:
    if request is None:
        return None
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return None


def _redact_ip(ip: Optional[str]) -> Optional[str]:
    if not ip:
        return None
    try:
        parsed = ipaddress.ip_address(ip)
        if isinstance(parsed, ipaddress.IPv4Address):
            net = ipaddress.IPv4Network(f"{ip}/24", strict=False)
            return f"{net.network_address}/24"
        net = ipaddress.IPv6Network(f"{ip}/48", strict=False)
        return f"{net.network_address}/48"
    except ValueError:
        return None


def audit_log(
    actor_uid: str,
    action: str,
    target_owner_id: Optional[str] = None,
    target_doc_id: Optional[str] = None,
    request: Optional[Request] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Best-effort audit write. Never raises — auth events must not break business actions."""
    try:
        doc_id = uuid4().hex
        request_id = getattr(request.state, "request_id", None) if request else None
        entry: dict[str, Any] = {
            "id": doc_id,
            "actorUid": actor_uid,
            "action": action,
            "targetOwnerId": target_owner_id,
            "targetDocId": target_doc_id,
            "ip": _redact_ip(_client_ip(request)),
            "requestId": request_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "createdAt": firestore.SERVER_TIMESTAMP,
            "metadata": metadata or {},
        }
        get_db().collection(AUDIT_COLLECTION).document(doc_id).set(entry)
    except Exception:
        _logger.exception("audit_log_failed", extra={"action": action, "actor": actor_uid})
