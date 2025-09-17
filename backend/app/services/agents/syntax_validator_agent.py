"""
Syntax Validator Agent

Validates Mermaid or Draw.io code for compile-ability. Performs at most one
syntax-only auto-fix attempt (no redesign) and returns final_code regardless.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import List

from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.logging_config import get_logger


class SyntaxValidatorAgent:
    def __init__(self):
        self.logger = get_logger("sketchflow.syntax_validator")

    # -------- Mermaid --------
    def _is_mermaid_valid(self, code: str) -> tuple[bool, List[str]]:
        issues: List[str] = []
        txt = (code or "").strip()
        if not txt:
            issues.append("Empty diagram code")
            return False, issues

        # No markdown fences
        if txt.startswith("```") or txt.endswith("```"):
            issues.append("Contains markdown fences")

        first_line = txt.splitlines()[0].strip() if txt.splitlines() else ""
        valid_starts = (
            "flowchart ",
            "graph ",
            "sequenceDiagram",
            "classDiagram",
            "stateDiagram",
            "stateDiagram-v2",
            "erDiagram",
            "gantt",
            "pie",
            "gitgraph",
        )
        if not any(first_line.startswith(v) for v in valid_starts):
            issues.append("Missing or invalid Mermaid header")

        # Quick reference checks: if arrow used, assume flowchart semantics
        # Count subgraph blocks roughly
        opens = len(re.findall(r"^\s*subgraph\b", txt, re.MULTILINE))
        closes = len(re.findall(r"^\s*end\s*$", txt, re.MULTILINE))
        if closes < opens:
            issues.append("Unclosed subgraph blocks")

        # Basic edge/node presence
        if "--" in txt or "-->" in txt or "->>" in txt:
            pass
        # Minimal acceptance; deeper syntax requires renderer
        return (len(issues) == 0), issues

    def _fix_mermaid_once(self, code: str, orientation_hint: str | None) -> str:
        txt = (code or "").strip()
        # Strip fences
        if txt.startswith("```"):
            lines = txt.splitlines()
            lines = lines[1:] if len(lines) > 1 else []
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            txt = "\n".join(lines).strip()

        # Ensure header
        lines = txt.splitlines()
        if lines:
            first = lines[0].strip()
        else:
            first = ""
        if not first or not re.match(r"^(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|stateDiagram-v2|erDiagram|gantt|pie|gitgraph)\b", first):
            # Default to flowchart with orientation hint
            orient = (orientation_hint or "TD").strip().upper()
            if orient not in {"TD", "LR", "BT", "RL"}:
                orient = "TD"
            header = f"flowchart {orient}"
            txt = header + ("\n" + txt if txt else "")

        # Balance subgraph/ end
        opens = len(re.findall(r"^\s*subgraph\b", txt, re.MULTILINE))
        closes = len(re.findall(r"^\s*end\s*$", txt, re.MULTILINE))
        if closes < opens:
            txt = txt.rstrip() + "\n" + "\n".join(["end"] * (opens - closes))

        return txt.strip()

    # -------- Draw.io --------
    def _is_drawio_valid(self, xml: str) -> tuple[bool, List[str]]:
        issues: List[str] = []
        txt = (xml or "").strip()
        if not txt:
            issues.append("Empty XML code")
            return False, issues
        try:
            root = ET.fromstring(txt)
        except ET.ParseError as e:
            return False, [f"XML parse error: {e}"]

        if root.tag != "mxfile":
            issues.append("Root element must be 'mxfile'")
            return False, issues
        diagram = root.find("diagram")
        if diagram is None:
            issues.append("Missing 'diagram' element")
        gm = diagram.find("mxGraphModel") if diagram is not None else None
        if gm is None:
            issues.append("Missing 'mxGraphModel' element")
        root_elem = gm.find("root") if gm is not None else None
        if root_elem is None:
            issues.append("Missing 'root' element")
        if root_elem is not None:
            cells = root_elem.findall("mxCell")
            if len(cells) < 2:
                issues.append("Missing basic cells '0' and '1'")
            else:
                # at least one vertex
                if not any(c.get("vertex") == "1" for c in cells):
                    issues.append("No vertex cells found")
        return (len(issues) == 0), issues

    def _clean_drawio_code(self, code: str) -> str:
        import html
        txt = (code or "").strip()
        if txt.startswith("```"):
            lines = txt.splitlines()
            if len(lines) > 1:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            txt = "\n".join(lines)
        txt = txt.strip()
        if "&lt;mxfile" in txt or "&lt;/mxfile" in txt:
            txt = html.unescape(txt)
        # Trim to mxfile boundaries if present
        s = txt.find("<mxfile")
        e = txt.rfind("</mxfile>")
        if s != -1 and e != -1:
            e = e + len("</mxfile>")
            txt = txt[s:e]
        return txt.strip()

    def _wrap_basic_drawio(self, inner: str | None = None) -> str:
        # Very conservative wrapper around content when structure missing
        base = (
            "<mxfile><diagram><mxGraphModel><root>"
            "<mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/>"
            "</root></mxGraphModel></diagram></mxfile>"
        )
        return base if not inner else inner

    @traceable(name="syntax_validator_agent")
    async def validate(self, state: SketchConversionState) -> SketchConversionState:
        job_id = state.get("job_id", "unknown")
        target = (state.get("target_format") or state.get("format") or "mermaid").lower()
        code = state.get("diagram_code") or ""

        self.logger.info(f"syntax_validation_start job_id={job_id} format={target}")

        processing_path = state.get("processing_path", []) or []
        processing_path.append("syntax_validator")
        state["processing_path"] = processing_path

        issues: List[str] = []
        valid = False
        final_code = code

        if target == "drawio":
            valid, issues = self._is_drawio_valid(final_code)
            if not valid:
                # Single auto-fix attempt
                cleaned = self._clean_drawio_code(final_code)
                # If still not a proper wrapper, keep cleaned
                final_code = cleaned or self._wrap_basic_drawio()
                valid2, issues2 = self._is_drawio_valid(final_code)
                valid = valid2
                if not valid2:
                    issues.extend([i for i in issues2 if i not in issues])
        else:
            # default mermaid
            valid, issues = self._is_mermaid_valid(final_code)
            if not valid:
                # Single auto-fix attempt using orientation hint from spec
                orient = None
                spec = state.get("diagram_spec") or {}
                if isinstance(spec, dict):
                    orient = spec.get("orientation")
                final_code = self._fix_mermaid_once(final_code, orient)
                valid2, issues2 = self._is_mermaid_valid(final_code)
                valid = valid2
                if not valid2:
                    issues.extend([i for i in issues2 if i not in issues])

        state["validation_passed"] = valid
        state["issues"] = issues
        state["final_code"] = final_code
        self.logger.info(
            f"syntax_validation_complete job_id={job_id} valid={valid} issues={len(issues)}"
        )
        return state
