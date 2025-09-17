"""
LangGraph workflow for the current 3-agent SketchFlow pipeline.

Architecture:
- describer_node: Vision describer creates structured diagram_spec + narrative
- diagram_generation_node: Format-specific generation (Mermaid/Draw.io)
- syntax_validation_node: Syntax validator ensures compile-ability (with retry guidance)

Linear flow with strict roles per agent.
"""

from __future__ import annotations

from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.state_types import SketchConversionState
from app.services.agents.describer_agent import DescriberAgent
from app.services.agents.mermaid_generation_agent import MermaidGenerationAgent
from app.services.agents.drawio_generation_agent import DrawioGenerationAgent
from app.services.agents.mermaid_syntax_validator_agent import MermaidSyntaxValidatorAgent
from app.services.agents.drawio_syntax_validator_agent import DrawioSyntaxValidatorAgent
import os
from app.core.logging_config import get_logger


class SketchConversionGraph:
    """
    Builds and runs the 3-agent conversion pipeline.

    Flow: Describer → Format-specific Generation → Syntax Validation
    """

    def __init__(self):
        self.describer_agent = DescriberAgent()
        self.mermaid_agent = MermaidGenerationAgent()
        self.drawio_agent = DrawioGenerationAgent()
        self.mermaid_validator = MermaidSyntaxValidatorAgent()
        self.drawio_validator = DrawioSyntaxValidatorAgent()
        # Back-compat: read GENERATION_MAX_RETRIES but treat value as max attempts
        # (i.e., number of generator passes including the first attempt).
        self.max_attempts = int(os.getenv("GENERATION_MAX_RETRIES", "2"))
        self.graph = self._build_graph()
        self.logger = get_logger("sketchflow.graph")

    def _build_graph(self):
        workflow = StateGraph(SketchConversionState)

        # Register the 3 agents in linear sequence
        workflow.add_node("describer_node", self.describer_agent.describe)
        workflow.add_node("diagram_generation_node", self._generate_diagram)
        workflow.add_node("syntax_validation_node", self._validate_diagram)

        # Pipeline with retry loop on validation failure
        workflow.set_entry_point("describer_node")
        workflow.add_edge("describer_node", "diagram_generation_node")
        workflow.add_edge("diagram_generation_node", "syntax_validation_node")

        # Conditional edge: return boolean for simpler mapping
        def _decide_next(state: SketchConversionState):
            passed = bool(state.get("validation_passed"))
            skipped = bool(state.get("validation_skipped"))
            attempt_count = int(state.get("attempt_count", 0) or 0)
            # End if valid, skipped, or attempts exhausted
            should_end = passed or skipped or attempt_count >= self.max_attempts
            # Debug log to trace decision
            try:
                job_id = state.get("job_id", "unknown")
                self.logger.info(
                    f"decide_next job_id={job_id} passed={passed} skipped={skipped} attempt_count={attempt_count} max_attempts={self.max_attempts} -> {'END' if should_end else 'RETRY'}"
                )
            except Exception:
                pass
            return should_end

        workflow.add_conditional_edges(
            "syntax_validation_node",
            _decide_next,
            {
                True: END,
                False: "diagram_generation_node",
            },
        )

        # Optional in-memory checkpointing
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    async def _generate_diagram(self, state: SketchConversionState) -> SketchConversionState:
        """Format-specific generation step writing raw `diagram_code`."""
        # Ensure processing path exists and record step
        processing_path = state.get("processing_path", []) or []

        # Debug visibility: confirm describer outputs are present
        try:
            has_spec = bool(state.get("diagram_spec"))
            narrative = state.get("scene_narrative", "") or ""
            notes = state.get("user_notes", "") or ""
            self.logger.debug(
                "generation_input has_spec=%s narrative_len=%d notes_len=%d job_id=%s",
                has_spec,
                len(narrative),
                len(notes),
                state.get("job_id", "unknown"),
            )
        except Exception:
            pass

        # Backward-compat for generators if needed (normalize describer outputs)
        state["sketch_description"] = state.get("scene_narrative", "")
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

        return new_state

    async def _validate_diagram(self, state: SketchConversionState) -> SketchConversionState:
        """Route to the appropriate validator based on target_format."""
        target = (state.get("target_format") or "mermaid").lower().strip()
        processing_path = state.get("processing_path", []) or []
        if target == "drawio":
            processing_path.append("syntax_validation_drawio")
            state["processing_path"] = processing_path
            return await self.drawio_validator.validate(state)
        else:
            processing_path.append("syntax_validation_mermaid")
            state["processing_path"] = processing_path
            return await self.mermaid_validator.validate(state)

    async def run(self, initial_state: SketchConversionState, thread_id: str | None = None) -> SketchConversionState:
        """
        Run the 3-agent pipeline with a normalized state.

        Args:
            initial_state: State with file_path, user_notes, target_format, job_id
            thread_id: Optional thread identifier for checkpointing

        Returns:
            Final state with scene_description and final_code
        """
        # Initialize processing path if not present
        if "processing_path" not in initial_state:
            initial_state["processing_path"] = []
        # Initialize attempt counter if not present (0-based)
        if "attempt_count" not in initial_state:
            initial_state["attempt_count"] = 0
            
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
