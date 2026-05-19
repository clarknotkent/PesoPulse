from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _user_or_ip_key(request: Request) -> str:
    uid = getattr(request.state, "uid", None)
    if uid:
        return f"user:{uid}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=_user_or_ip_key, headers_enabled=True)


def ip_key(request: Request) -> str:
    return f"ip:{get_remote_address(request)}"


def attach_uid(request: Request, uid: str) -> None:
    request.state.uid = uid


__all__: list[str] = ["attach_uid", "ip_key", "limiter"]
