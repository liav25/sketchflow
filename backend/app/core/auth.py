from __future__ import annotations

import time
from functools import lru_cache
from typing import Any, Dict, Optional

import httpx
from jose import jwt
from jose.exceptions import JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.logging_config import get_logger


logger = get_logger("sketchflow.auth")
security = HTTPBearer(auto_error=False)


def _jwks_url() -> str:
    base = settings.model_dump().get("SUPABASE_URL") or None  # type: ignore[attr-defined]
    # Settings might not expose SUPABASE_URL; fall back to env access
    import os
    base = base or os.getenv("SUPABASE_URL")
    if not base:
        raise RuntimeError("SUPABASE_URL is required for JWT verification")
    return base.rstrip("/") + "/auth/v1/.well-known/jwks.json"


_CACHE: Dict[str, Any] = {"jwks": None, "ts": 0.0}


def _get_jwks() -> Dict[str, Any]:
    now = time.time()
    if _CACHE["jwks"] and (now - float(_CACHE["ts"])) < 3600:
        return _CACHE["jwks"]
    url = _jwks_url()
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            jwks = resp.json()
            _CACHE["jwks"] = jwks
            _CACHE["ts"] = now
            return jwks
    except Exception as e:
        logger.exception(f"Failed to fetch JWKS from {url}: {e}")
        raise


def _issuer() -> str:
    import os
    base = os.getenv("SUPABASE_URL")
    if not base:
        raise RuntimeError("SUPABASE_URL is required for JWT verification")
    return base.rstrip("/") + "/auth/v1"


def verify_jwt(token: str) -> Dict[str, Any]:
    """Verify a Supabase JWT access token and return claims.

    - Verifies signature against JWKS
    - Verifies issuer and expiration
    - Accepts RS256
    """
    jwks = _get_jwks()
    try:
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=None,  # Supabase access tokens generally have aud="authenticated"; do not enforce
            issuer=_issuer(),
            options={
                "verify_aud": False,
            },
        )
        return claims
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    if not creds or not creds.scheme.lower() == "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        claims = verify_jwt(creds.credentials)
        return {
            "id": claims.get("sub"),
            "email": claims.get("email"),
            "claims": claims,
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    if not creds or not creds.scheme.lower() == "bearer":
        return None
    try:
        claims = verify_jwt(creds.credentials)
        return {
            "id": claims.get("sub"),
            "email": claims.get("email"),
            "claims": claims,
        }
    except Exception:
        return None

