"""
Describer Agent

Uses the VISION_LLM_MODEL to analyze the uploaded sketch image and produce:
- diagram_spec (JSON): structured description of the diagram
- scene_narrative (str): short natural language summary

No absolute positions are inferred; rely on orientation/grouping only.
"""

from __future__ import annotations

import base64
import os
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.llm_factory import get_chat_model
from app.prompts.prompt_templates import PromptTemplates
from app.core.logging_config import get_logger


class DescriberAgent:
    """
    Agent 1: Describer

    - Reads a sketch image and user notes
    - Outputs a structured diagram_spec (JSON) and a short scene_narrative
    - Uses the model specified by VISION_LLM_MODEL exclusively
    """

    def __init__(self):
        self.prompt_templates = PromptTemplates()
        self.logger = get_logger("sketchflow.describer")

        model = os.getenv("VISION_LLM_MODEL")
        if not model:
            raise ValueError("VISION_LLM_MODEL is not set; required for DescriberAgent")
        # Lower temperature to encourage faithful extraction
        self.client, self.provider = get_chat_model(model, temperature=0.1)

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    @traceable(name="describer_agent")
    async def describe(self, state: SketchConversionState) -> SketchConversionState:
        job_id = state.get("job_id", "unknown")
        self.logger.info(f"describer_start job_id={job_id}")

        processing_path = state.get("processing_path", []) or []
        processing_path.append("describer")
        state["processing_path"] = processing_path

        prompt = self.prompt_templates.get_describer_prompt(
            user_notes=state.get("user_notes", "")
        )

        try:
            base64_image = self._encode_image(state["file_path"])

            # Build message with vision content based on provider
            if self.provider == "openai" or isinstance(self.client, ChatOpenAI):
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ]
                )
            else:
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image,
                            },
                        },
                    ]
                )

            response = await self.client.ainvoke([message])
            text = response.content or ""

            # Parser: Expect JSON first line (or fenced), then narrative. Keep it simple:
            import json, re
            json_block = None
            # Prefer fenced JSON
            m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
            if m:
                json_block = m.group(1)
            else:
                # Attempt to capture first top-level JSON object
                start = text.find("{")
                if start != -1:
                    depth = 0
                    for i, ch in enumerate(text[start:], start):
                        if ch == "{":
                            depth += 1
                        elif ch == "}":
                            depth -= 1
                            if depth == 0:
                                json_block = text[start : i + 1]
                                break

            diagram_spec: Any = {}
            if json_block:
                try:
                    diagram_spec = json.loads(json_block)
                except Exception:
                    diagram_spec = {}

            # Narrative = remainder after the JSON block
            narrative = text
            if json_block:
                narrative = text.replace(json_block, "").strip()
                narrative = re.sub(r"```json|```", "", narrative).strip()

            state["diagram_spec"] = diagram_spec
            state["scene_narrative"] = narrative

            self.logger.info(f"describer_complete job_id={job_id}")
            return state
        except Exception as e:
            self.logger.exception(f"describer_error job_id={job_id} error={e}")
            # Fallback: minimal spec to keep pipeline alive
            state["diagram_spec"] = {
                "diagram_type": "flowchart",
                "orientation": "TD",
                "elements": [],
                "edges": [],
            }
            state["scene_narrative"] = state.get("user_notes", "")
            return state

