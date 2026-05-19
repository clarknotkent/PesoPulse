import logging
import os
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import get_firebase_app
from app.routes import (
    audit as audit_routes,
    auth,
    budgets,
    categories,
    goals,
    notifications,
    receipts,
    recurring,
    sharing,
    stats,
    transactions,
)

get_firebase_app()

app = FastAPI(title="PesoPulse API", version="1.0.0")

_logger = logging.getLogger("pesopulse")


def _parse_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]


_SECURITY_HEADERS: dict[str, str] = {
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-site",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex
        request.state.request_id = request_id
        try:
            response = await call_next(request)
        except Exception:
            _logger.exception(
                "unhandled_exception",
                extra={"request_id": request_id, "path": request.url.path},
            )
            raise
        for key, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(key, value)
        response.headers["X-Request-Id"] = request_id
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-Id"],
    expose_headers=["X-Request-Id"],
    max_age=600,
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["receipts"])
app.include_router(sharing.router, prefix="/api/sharing", tags=["sharing"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])
app.include_router(recurring.router, prefix="/api/recurring", tags=["recurring"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(audit_routes.router, prefix="/api/audit", tags=["audit"])


@app.get("/api/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "service": "PesoPulse API"}
