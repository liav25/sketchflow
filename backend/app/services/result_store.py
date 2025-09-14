from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.config import settings


RESULTS_DIR = os.path.join(settings.storage_path, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


@dataclass
class ConversionRecord:
    job_id: str
    format: str
    notes: str
    code: str
    owner_user_id: Optional[str]
    created_at: str


def _path(job_id: str) -> str:
    return os.path.join(RESULTS_DIR, f"{job_id}.json")


def save_result(record: ConversionRecord) -> None:
    p = _path(record.job_id)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(asdict(record), f)


def load_result(job_id: str) -> Optional[Dict[str, Any]]:
    p = _path(job_id)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

