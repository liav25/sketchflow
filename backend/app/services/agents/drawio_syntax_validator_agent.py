"""
Draw.io Syntax Validator Agent

Uses an LLM (default gpt-4.1) to validate draw.io (diagrams.net) XML output.
The validator checks structure against docs expectations and returns actionable
corrections when invalid.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List
import json

from langsmith import traceable
from langchain_core.messages import HumanMessage

from app.core.state_types import SketchConversionState
from app.core.llm_factory import get_chat_model
from app.core.logging_config import get_logger


DRAWIO_VALIDATION_PROMPT = (
    "You are a strict validator for draw.io (diagrams.net) XML files. "
    "Validate the user's XML against the expected structure. The minimum valid structure: "
    "<mxfile><diagram><mxGraphModel><root><mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/> ... </root></mxGraphModel></diagram></mxfile>. "
    "Rules:\n"
    "- Root element MUST be <mxfile>\n"
    "- MUST contain a <diagram> child\n"
    "- Inside <diagram>, MUST contain <mxGraphModel>\n"
    "- Inside <mxGraphModel>, MUST contain <root>\n"
    "- Inside <root>, MUST contain at least two <mxCell> elements: id=\"0\" and id=\"1\" (layer)\n"
    "- At least one vertex cell should exist (mxCell vertex=\"1\") to avoid empty graphs\n"
    "- Attributes should be properly quoted; XML must be well-formed\n\n"
    "Return ONLY a JSON object with: {\"valid\": boolean, \"issues\": string[], \"normalized_xml\": string|null}. "
    "If invalid, populate 'issues' with concise, concrete messages that a generator can fix."
)


class DrawioSyntaxValidatorAgent:
    def __init__(self):
        self.logger = get_logger("sketchflow.validator.drawio")
        model = os.getenv("VALIDATION_LLM_MODEL", "gpt-4.1")
        # Lower temperature for determinism
        self.client, _ = get_chat_model(model, temperature=0.1)

    def _build_message(self, xml_code: str) -> HumanMessage:
        # Keep prompt compact; the XML goes as content after instructions
        prompt = DRAWIO_VALIDATION_PROMPT + "\n\n<XML>\n" + xml_code + "\n</XML>"
        return HumanMessage(content=prompt)

    def _parse_json(self, text: str) -> Dict[str, Any]:
        # Extract first JSON object from the text
        start = text.find("{")
        if start == -1:
            return {"valid": False, "issues": ["No JSON in validator response"], "normalized_xml": None}
        depth = 0
        end = -1
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        raw = text[start:end] if end != -1 else text[start:]
        try:
            return json.loads(raw)
        except Exception:
            return {"valid": False, "issues": ["Validator JSON parse error"], "normalized_xml": None}

    @traceable(name="drawio_syntax_validator")
    async def validate(self, state: SketchConversionState) -> SketchConversionState:
        job_id = state.get("job_id", "unknown")
        xml_code = state.get("diagram_code") or ""
        self.logger.info(f"drawio_validation_start job_id={job_id}")

        if not xml_code.strip():
            state["validation_passed"] = False
            state["issues"] = ["Empty XML code"]
            state["final_code"] = ""
            state["corrections"] = (
                "The Draw.io XML is empty. Please regenerate valid draw.io XML starting with <mxfile>."
            )
            return state

        message = self._build_message(xml_code)
        try:
            response = await self.client.ainvoke([message])
            content = response.content or ""
        except Exception as e:
            # If LLM validation fails, fall back to simple structural message
            state["validation_passed"] = False
            state["issues"] = [f"Validator error: {e}"]
            state["final_code"] = xml_code
            state["corrections"] = (
                "Draw.io validator failed to run. Ensure XML includes <mxfile><diagram><mxGraphModel><root> with basic cells 0 and 1, and at least one vertex."
            )
            return state

        parsed = self._parse_json(content)
        valid = bool(parsed.get("valid"))
        issues: List[str] = parsed.get("issues") or []
        normalized = parsed.get("normalized_xml") or None

        state["validation_passed"] = valid
        state["issues"] = issues
        state["final_code"] = (normalized or xml_code) if valid else xml_code
        if not valid and issues:
            state["corrections"] = (
                "The Draw.io XML failed validation. Please fix the following issues and regenerate strictly:"\
                + "\n- " + "\n- ".join(issues[:20])
            )

        self.logger.info(f"drawio_validation_complete job_id={job_id} valid={valid}")
        return state

