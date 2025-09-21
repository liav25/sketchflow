from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _make_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine.

    - Honors Supabase "direct" URLs (postgresql://...).
    - Upgrades to `postgresql+asyncpg://` for async usage.
    - Handles TLS for asyncpg with env-driven modes to avoid sslmode issues.
    """
    import os
    import ssl
    from urllib.parse import urlparse
    from typing import Any, Dict

    url = settings.model_dump().get("database_url") or None
    if not url:
        url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./storage/sketchflow.db")

    # Upgrade to asyncpg when a plain PostgreSQL URL is provided.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        url = "postgresql+asyncpg://" + url[len("postgresql://") :]

    # TLS handling for asyncpg
    connect_args: Dict[str, Any] = {}
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        use_asyncpg = parsed.scheme.lower().startswith("postgresql+asyncpg")

        # Determine SSL mode
        # Modes: disable | require | verify-ca | verify-full
        # - require: encrypt but don't verify cert (dev-friendly)
        # - verify-ca/full: verify with CA; use DATABASE_SSL_ROOT_CERT if provided
        ssl_mode = (os.getenv("DATABASE_SSL_MODE") or ("require" if host.endswith("supabase.co") else "")).strip().lower()

        if use_asyncpg and ssl_mode:
            if ssl_mode == "disable":
                pass  # no TLS
            elif ssl_mode == "require":
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                connect_args["ssl"] = ctx
            elif ssl_mode in ("verify-ca", "verify-full"):
                ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
                cafile = os.getenv("DATABASE_SSL_ROOT_CERT")
                if cafile:
                    try:
                        ctx.load_verify_locations(cafile=cafile)
                    except Exception:
                        # If provided path is invalid, fall back to system roots
                        pass
                ctx.check_hostname = ssl_mode == "verify-full"
                ctx.verify_mode = ssl.CERT_REQUIRED
                connect_args["ssl"] = ctx
            else:
                # Fallback: require encryption without verification
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                connect_args["ssl"] = ctx
        elif use_asyncpg and host.endswith("supabase.co"):
            # Default for Supabase if no explicit mode set: require encryption, no verify
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx
    except Exception:
        pass

    return create_async_engine(url, echo=False, future=True, connect_args=connect_args)


engine: AsyncEngine = _make_engine()
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
