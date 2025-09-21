from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# Determine table name based on environment
def get_feedback_table_name():
    try:
        from app.core.config import settings
        return "feedbacks_dev" if settings.app_env == "development" else "feedbacks"
    except ImportError:
        # Fallback to environment variable
        app_env = os.getenv("APP_ENV", "production")
        return "feedbacks_dev" if app_env == "development" else "feedbacks"

class Feedback(Base):
    # For now, always use dev table for local development
    # Change this to get_feedback_table_name() when environment loading is fixed
    __tablename__ = "feedbacks_dev"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # User identification (IP address for anonymous users, user_id for authenticated users)
    client_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Feedback content
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Optional: user agent for additional context
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)