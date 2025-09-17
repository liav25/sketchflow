"""
LangGraph workflow for a simplified 2-agent SketchFlow pipeline.

New Architecture:
- image_description_node: Translate image to natural language description
- diagram_generation_node: Generate final diagram (Mermaid/Draw.io)

Simple linear flow that matches requested agentic split.
"""

from __future__ import annotations

from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.state_types import SketchConversionState
from app.services.agents.scene_understanding_agent import SceneUnderstandingAgent
from app.services.agents.mermaid_generation_agent import MermaidGenerationAgent
from app.services.agents.drawio_generation_agent import DrawioGenerationAgent
from app.core.logging_config import get_logger


class SketchConversionGraph:
    """
    Builds and runs the simplified 2-agent conversion pipeline.

    Flow: Image Description → Format-specific Generation (Mermaid/Draw.io)
    """

    def __init__(self):
        self.scene_understanding_agent = SceneUnderstandingAgent()
        self.mermaid_agent = MermaidGenerationAgent()
        self.drawio_agent = DrawioGenerationAgent()
        self.graph = self._build_graph()
        self.logger = get_logger("sketchflow.graph")

    def _build_graph(self):
        workflow = StateGraph(SketchConversionState)

        # Register the 2 agents in linear sequence
        workflow.add_node("image_description_node", self.scene_understanding_agent.understand_scene)
        workflow.add_node("diagram_generation_node", self._generate_diagram)

        # Linear pipeline
        workflow.set_entry_point("image_description_node")
        workflow.add_edge("image_description_node", "diagram_generation_node")
        workflow.add_edge("diagram_generation_node", END)

        # Optional in-memory checkpointing
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    async def _generate_diagram(self, state: SketchConversionState) -> SketchConversionState:
        """
        Format-specific generation step. Uses Claude for generation agents,
        while the description step uses GPT-4.1 via SceneUnderstandingAgent.

        Prepares compatibility fields expected by generation agents and
        writes the final diagram into `final_diagram`.
        """
        # Ensure processing path exists and record step
        processing_path = state.get("processing_path", []) or []

        # Map scene description into the key expected by generation agents
        # and pass user notes as generation instructions.
        scene_desc = state.get("scene_description", "")
        state["sketch_description"] = scene_desc
        state["generation_instructions"] = state.get("user_notes", "")

        target = (state.get("target_format") or "mermaid").lower().strip()

        if target == "drawio":
            processing_path.append("diagram_generation_drawio")
            state["processing_path"] = processing_path
            new_state = await self.drawio_agent.generate_drawio_diagram(state)  # adds diagram_code
        else:
            # Default to mermaid
            processing_path.append("diagram_generation_mermaid")
            state["processing_path"] = processing_path
            new_state = await self.mermaid_agent.generate_mermaid_diagram(state)  # adds diagram_code

        # Normalize output into `final_diagram` expected by ConversionService
        final_code = new_state.get("diagram_code", "")
        new_state["final_diagram"] = final_code

        # Optionally set a basic confidence score if not present
        if "confidence_score" not in new_state:
            new_state["confidence_score"] = 0.7 if final_code else 0.3

        return new_state

    async def run(self, initial_state: SketchConversionState, thread_id: str | None = None) -> SketchConversionState:
        """
        Run the 2-agent pipeline with a simplified state.

        Args:
            initial_state: State with file_path, user_notes, target_format, job_id
            thread_id: Optional thread identifier for checkpointing

        Returns:
            Final state with scene_description and final_diagram
        """
        # Initialize processing path if not present
        if "processing_path" not in initial_state:
            initial_state["processing_path"] = []
            
        # LangGraph checkpointers require a configurable thread identifier
        tid = thread_id or initial_state.get("thread_id") or initial_state.get("job_id") or str(uuid4())
        # Keep thread id in state for traceability
        initial_state["thread_id"] = tid

        result = await self.graph.ainvoke(
            initial_state,
            config={
                "configurable": {
                    "thread_id": tid,
                }
            },
        )
        return result
