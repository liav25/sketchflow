"""
Lucidchart Publish Agent

Creates a Lucidchart document from Draw.io (diagrams.net) XML and optionally
returns an embed URL for previewing.

This agent is a thin integration layer. It is disabled by default and activates
only if environment variables are provided:

- LUCID_API_IMPORT_URL: Full URL of an endpoint that accepts an import request
  to create a Lucidchart document from Draw.io XML. This can be a proxy you
  host that talks to Lucid's API, or a direct Lucid endpoint if available to you.
- LUCID_API_TOKEN: Bearer token for calling the import endpoint.

Expected (example) JSON response fields when successful:
- documentId or document_id
- embedUrl or embed_url

If these fields are present, the agent stores them in the state as
`lucid_document_id` and `lucid_embed_url`.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import httpx
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.logging_config import get_logger


class LucidchartPublishAgent:
    def __init__(self):
        self.logger = get_logger("sketchflow.lucid.publish")
        self.import_url = os.getenv("LUCID_API_IMPORT_URL", "").strip()
        self.api_token = os.getenv("LUCID_API_TOKEN", "").strip()

    def _is_configured(self) -> bool:
        return bool(self.import_url and self.api_token)

    @traceable(name="lucid_publish_node")
    async def publish(self, state: SketchConversionState) -> SketchConversionState:
        job_id = state.get("job_id", "unknown")
        processing_path = state.get("processing_path", []) or []

        # Ensure we only run for lucidchart target
        target = (state.get("target_format") or "").lower().strip()
        if target != "lucidchart":
            # No-op for other formats
            processing_path.append("lucid_publish_skipped_wrong_target")
            state["processing_path"] = processing_path
            return state

        xml_code = state.get("final_code") or state.get("diagram_code") or ""
        if not xml_code.strip():
            processing_path.append("lucid_publish_skipped_no_xml")
            state["processing_path"] = processing_path
            state["lucid_publish_skipped"] = "no_xml"
            return state

        # If the code is PlantUML, skip publish (import expects Draw.io XML)
        lower = xml_code.strip().lower()
        if lower.startswith("@startuml") and lower.endswith("@enduml"):
            processing_path.append("lucid_publish_skipped_plantuml")
            state["processing_path"] = processing_path
            state["lucid_publish_skipped"] = "plantuml_not_supported"
            return state

        if not self._is_configured():
            # Credentials missing; skip gracefully
            self.logger.info("Lucid publish skipped: missing credentials or import URL")
            processing_path.append("lucid_publish_skipped_missing_config")
            state["processing_path"] = processing_path
            state["lucid_publish_skipped"] = "missing_config"
            return state

        # Attempt to import the Draw.io XML via provided endpoint
        name = f"SketchFlow {job_id}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "format": "drawio",
            "data": xml_code,
            "name": name,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(self.import_url, json=payload, headers=headers)
                if resp.status_code >= 200 and resp.status_code < 300:
                    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    doc_id = data.get("documentId") or data.get("document_id")
                    embed_url = data.get("embedUrl") or data.get("embed_url")

                    state["lucid_document_id"] = doc_id or ""
                    state["lucid_embed_url"] = embed_url or ""
                    processing_path.append("lucid_publish")
                    state["processing_path"] = processing_path
                    self.logger.info(
                        f"lucid_publish_complete job_id={job_id} status=ok doc_id={doc_id}"
                    )
                    return state
                else:
                    self.logger.warning(
                        f"Lucid import failed job_id={job_id} status={resp.status_code}: {resp.text[:200]}"
                    )
                    state["lucid_publish_error"] = f"HTTP {resp.status_code}"
                    processing_path.append("lucid_publish_failed")
                    state["processing_path"] = processing_path
                    return state
        except Exception as e:
            self.logger.exception(f"Lucid import exception job_id={job_id} err={e}")
            state["lucid_publish_error"] = str(e)
            processing_path.append("lucid_publish_exception")
            state["processing_path"] = processing_path
            return state
