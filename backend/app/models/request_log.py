from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime, JSON, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# Determine table name based on environment
def get_table_name():
    try:
        from app.core.config import settings
        return "request_logs_dev" if settings.app_env == "development" else "request_logs"
    except ImportError:
        # Fallback to environment variable
        app_env = os.getenv("APP_ENV", "production")
        return "request_logs_dev" if app_env == "development" else "request_logs"

class RequestLog(Base):
    __tablename__ = get_table_name()

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Basic HTTP request info
    method: Mapped[str] = mapped_column(String(16))
    path: Mapped[str] = mapped_column(String(255), index=True)
    status_code: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer)

    # Conversion-specific tracking
    job_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    format: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    # User and request context
    client_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # File upload details
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Conversion details
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Error handling
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Comprehensive JSON storage for complete request/response data
    # Use JSONB on Postgres, JSON elsewhere
    request_data: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), nullable=True
    )
    response_data: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), nullable=True
    )
    extra: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), nullable=True
    )

