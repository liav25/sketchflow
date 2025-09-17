"""
Mermaid Syntax Validator Agent

Validates Mermaid code by invoking mermaid-cli (mmdc). If validation fails,
collects the CLI error output and attaches it as corrections so the generation
agent can retry with concrete guidance.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from typing import List

from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.logging_config import get_logger


class MermaidSyntaxValidatorAgent:
    def __init__(self):
        self.logger = get_logger("sketchflow.validator.mermaid")
        # Allow overriding the mermaid-cli binary via env var
        self.mmdc_bin = os.getenv("MMDC_BIN", "mmdc")
        # Optional timeout for the CLI invocation (seconds)
        try:
            self.mmdc_timeout = int(os.getenv("MMDC_TIMEOUT_SEC", "30"))
        except Exception:
            self.mmdc_timeout = 30

    def _run_mmdc(self, code: str) -> tuple[bool, str]:
        if not code.strip():
            return False, "Empty Mermaid code"

        # Render to a temporary SVG to trigger syntax checking
        with tempfile.TemporaryDirectory() as td:
            in_path = os.path.join(td, "diagram.mmd")
            out_path = os.path.join(td, "diagram.svg")
            with open(in_path, "w", encoding="utf-8") as f:
                f.write(code)

            try:
                # NOTE: mmdc renders files using Puppeteer/Chromium and may be slow
                # We capture stderr for detailed error messages
                proc = subprocess.run(
                    [self.mmdc_bin, "-i", in_path, "-o", out_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    text=True,
                    timeout=self.mmdc_timeout,
                )
            except FileNotFoundError:
                return False, (
                    "mermaid-cli (mmdc) not found. Install with `npm install -g @mermaid-js/mermaid-cli` "
                    "and ensure it is in PATH, or set MMDC_BIN."
                )
            except subprocess.TimeoutExpired:
                return False, (
                    f"mermaid-cli (mmdc) timed out after {self.mmdc_timeout}s. "
                    "Consider simplifying the diagram or increasing MMDC_TIMEOUT_SEC."
                )

            if proc.returncode == 0:
                return True, ""
            else:
                # mmdc typically writes parse/compile errors to stderr
                err = (proc.stderr or proc.stdout or "Mermaid CLI validation failed").strip()
                # Keep message concise
                return False, err[:2000]

    @traceable(name="mermaid_syntax_validator")
    async def validate(self, state: SketchConversionState) -> SketchConversionState:
        job_id = state.get("job_id", "unknown")
        code = state.get("diagram_code") or ""
        self.logger.info(f"mermaid_validation_start job_id={job_id}")

        valid, message = self._run_mmdc(code)
        # If mermaid-cli is unavailable, skip validation but do not block the pipeline
        if not valid and message.lower().startswith("mermaid-cli (mmdc) not found"):
            state["validation_passed"] = True
            state["validation_skipped"] = "mmdc_missing"
            state["issues"] = [message]
            state["final_code"] = code
        else:
            state["validation_passed"] = valid
            state["issues"] = [] if valid else [message]
            state["final_code"] = code if valid else code
            # Provide generator-friendly corrections when invalid
            if not valid and message:
                state["corrections"] = (
                    "The Mermaid code failed to compile with mermaid-cli. "
                    "Please fix the issues reported by the compiler below and regenerate strictly: \n\n"
                    f"{message}"
                )

        self.logger.info(
            f"mermaid_validation_complete job_id={job_id} valid={valid}"
        )
        return state
