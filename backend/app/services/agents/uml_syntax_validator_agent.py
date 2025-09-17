"""
UML Syntax Validator Agent

A dedicated validator for the UML generation path. Currently validates
PlantUML text (between @startuml and @enduml) and reuses the PlantUML
validator logic while keeping a distinct class for clarity and routing.
"""

from __future__ import annotations

from app.core.logging_config import get_logger
from app.services.agents.plantuml_syntax_validator_agent import (
    PlantUMLSyntaxValidatorAgent,
)


class UMLSyntaxValidatorAgent(PlantUMLSyntaxValidatorAgent):
    def __init__(self):
        super().__init__()
        # Override logger name for UML-specific traces
        self.logger = get_logger("sketchflow.validator.uml")

