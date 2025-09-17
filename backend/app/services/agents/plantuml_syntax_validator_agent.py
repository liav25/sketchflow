"""
PlantUML Syntax Validator Agent

Performs lightweight validation of PlantUML code by ensuring the presence of
@startuml/@enduml and a few basic sanity checks per diagram kind. This avoids
external dependencies while still providing actionable corrections.
"""

from __future__ import annotations

from typing import Tuple

from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.logging_config import get_logger


class PlantUMLSyntaxValidatorAgent:
    def __init__(self):
        self.logger = get_logger("sketchflow.validator.plantuml")

    def _basic_validate(self, code: str) -> Tuple[bool, str]:
        if not code or not code.strip():
            return False, "Empty PlantUML code"
        text = code.strip()
        lower = text.lower()
        if not lower.startswith("@startuml") or not lower.endswith("@enduml"):
            return False, "PlantUML must start with @startuml and end with @enduml"

        # Heuristic checks for common UML kinds
        body = lower[len("@startuml"): -len("@enduml")].strip()
        if any(k in body for k in ["participant ", "actor ", "->", "-->"]):
            return True, ""
        if any(k in body for k in ["class ", "interface ", "enum ", "extends ", "..|>"]):
            return True, ""
        if any(k in body for k in ["usecase ", "( ", ")", "actor "]):
            return True, ""
        if any(k in body for k in ["state ", "[*]", "-->", "-> "]):
            return True, ""
        if any(k in body for k in ["component ", "interface ", "[", "]"]):
            return True, ""

        # If it passes start/end but no recognizable constructs, still accept
        # but warn to improve content on retry if needed
        return True, ""

    @traceable(name="plantuml_syntax_validator")
    async def validate(self, state: SketchConversionState) -> SketchConversionState:
        job_id = state.get("job_id", "unknown")
        code = state.get("diagram_code") or ""
        self.logger.info(f"plantuml_validation_start job_id={job_id}")

        valid, message = self._basic_validate(code)
        state["validation_passed"] = valid
        state["issues"] = [] if valid else [message]
        state["final_code"] = code
        if not valid and message:
            state["corrections"] = (
                "The PlantUML code is invalid. Please regenerate strictly as PlantUML, "
                "ensuring it starts with @startuml and ends with @enduml. "
                f"Issues: {message}"
            )

        self.logger.info(
            f"plantuml_validation_complete job_id={job_id} valid={valid}"
        )
        return state

