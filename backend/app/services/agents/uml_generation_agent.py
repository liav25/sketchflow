"""
UML Generation Agent (PlantUML)

Generates PlantUML code for UML diagrams (class, sequence, use case, activity,
state, component). The pipeline's "uml" target produces PlantUML
text instead of Draw.io XML.

Notes:
- Output is plain PlantUML text between @startuml and @enduml.
- Validation is performed by a lightweight PlantUML validator.
"""

from __future__ import annotations

import os
from typing import Dict, Any
import xml.etree.ElementTree as ET

from langsmith import traceable
from langchain_core.messages import HumanMessage

from app.core.state_types import SketchConversionState
from app.core.llm_factory import get_chat_model
from app.prompts.prompt_templates import PromptTemplates


class UMLGenerationAgent:
    def __init__(self, *, model: str | None = None, temperature: float | None = None):
        self.prompt_templates = PromptTemplates()
        resolved_model = model or os.getenv("GENERATION_LLM_MODEL", "gpt-4.1")
        resolved_temp = 0.1 if temperature is None else float(temperature)
        self.client, self.provider = get_chat_model(resolved_model, temperature=resolved_temp)

    def _clean_plantuml(self, code: str) -> str:
        txt = (code or "").strip()
        # Strip fenced code blocks
        if txt.startswith("```"):
            lines = txt.split("\n")
            if len(lines) > 1:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            txt = "\n".join(lines)
        txt = txt.strip()
        # Extract between @startuml and @enduml if present anywhere
        start = txt.lower().find("@startuml")
        end = txt.lower().rfind("@enduml")
        if start != -1 and end != -1:
            end = end + len("@enduml")
            txt = txt[start:end]
        return txt.strip()

    def _basic_plantuml_ok(self, text: str) -> bool:
        t = (text or "").strip().lower()
        return t.startswith("@startuml") and t.endswith("@enduml")

    def _detect_uml_kind(self, description: str, instructions: str) -> str:
        text = (description + " " + instructions).lower()
        if any(k in text for k in ["sequence", "lifeline", "actor", "message"]):
            return "sequence"
        if any(k in text for k in ["use case", "usecase", "actor", "goal"]):
            return "usecase"
        if any(k in text for k in ["class", "inheritance", "attribute", "method"]):
            return "class"
        if any(k in text for k in ["state", "transition", "entry", "exit"]):
            return "state"
        if any(k in text for k in ["activity", "flow", "action", "decision"]):
            return "activity"
        if any(k in text for k in ["component", "interface", "port", "provided"]):
            return "component"
        return "class"

    @traceable(name="uml_generation_node")
    async def generate_uml_drawio(self, state: SketchConversionState) -> SketchConversionState:
        attempt = int(state.get("attempt_count", 0) or 0)
        state["attempt_count"] = attempt + 1

        description = state.get("sketch_description", "")
        base_instructions = state.get("generation_instructions", "")
        corrections = (state.get("corrections", "") or "").strip()
        if attempt > 0 and corrections:
            instructions = f"{base_instructions}\n\nApply these validation instructions strictly (attempt {attempt+1}):\n{corrections}"
        else:
            instructions = base_instructions

        diagram_spec = state.get("diagram_spec") or None
        uml_kind = self._detect_uml_kind(description, instructions)

        # Build prompt (now generates PlantUML)
        if diagram_spec:
            prompt = self.prompt_templates.get_uml_plantuml_generation_prompt_from_spec(diagram_spec, uml_kind)
        else:
            prompt = self.prompt_templates.get_uml_plantuml_generation_prompt(
                description=description,
                instructions=instructions,
                uml_kind=uml_kind,
            )

        try:
            if not self.client:
                raise ValueError("No LLM client available. Configure OPENAI_API_KEY or ANTHROPIC_API_KEY.")
            message = HumanMessage(content=prompt)
            resp = await self.client.ainvoke([message])
            puml = self._clean_plantuml(resp.content or "")
            if not self._basic_plantuml_ok(puml):
                # leave as-is; validator will guide retry
                pass
            state["diagram_code"] = puml
            return state
        except Exception as e:
            state["diagram_code"] = ""
            state["generation_error"] = str(e)
            return state
