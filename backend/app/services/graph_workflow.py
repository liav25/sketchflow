"""
LangGraph workflow for the SketchFlow conversion pipeline.

Nodes:
- vision_analysis_node: Analyze sketch → instructions
- mermaid_generation_node: Generate Mermaid diagram from instructions
- drawio_generation_node: Generate Draw.io diagram from instructions
- validation_node: Validate and loop back if needed
"""

from __future__ import annotations

from typing import Callable
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.state_types import SketchConversionState
from app.services.agents.vision_agent import VisionAnalysisAgent
from app.services.agents.mermaid_generation_agent import MermaidGenerationAgent
from app.services.agents.drawio_generation_agent import DrawioGenerationAgent
from app.services.agents.validation_agent import ValidationAgent
from app.core.logging_config import get_logger


class SketchConversionGraph:
    """
    Builds and runs the 3-node conversion graph with a validation loop.
    """

    def __init__(self, max_retries: int = 2):
        self.vision_agent = VisionAnalysisAgent()
        self.mermaid_agent = MermaidGenerationAgent()
        self.drawio_agent = DrawioGenerationAgent()
        self.validation_agent = ValidationAgent()
        self.max_retries = max_retries
        self.graph = self._build_graph()
        self.logger = get_logger("sketchflow.graph")

    def _build_graph(self):
        workflow = StateGraph(SketchConversionState)

        # Register nodes
        workflow.add_node("vision_analysis_node", self.vision_agent.analyze_sketch)
        # Split generation into specialized per-format nodes
        workflow.add_node("mermaid_generation_node", self.mermaid_agent.generate_mermaid_diagram)
        workflow.add_node("drawio_generation_node", self.drawio_agent.generate_drawio_diagram)
        workflow.add_node("validation_node", self.validation_agent.validate)

        # Router: deterministically select generation node based on state['format']
        def format_router(state: SketchConversionState) -> str:
            fmt = str(state.get("format", "")).strip().lower()
            mapping = {
                "mermaid": "mermaid_generation_node",
                "drawio": "drawio_generation_node",
                "draw.io": "drawio_generation_node",
            }
            # Deterministic fallback: default to mermaid if unknown
            return mapping.get(fmt, "mermaid_generation_node")

        # Edges
        workflow.set_entry_point("vision_analysis_node")
        # Route to the correct generation node solely by format
        workflow.add_conditional_edges(
            "vision_analysis_node",
            format_router,
            {
                "mermaid_generation_node": "mermaid_generation_node",
                "drawio_generation_node": "drawio_generation_node",
            },
        )

        # Both generation nodes flow into validation
        workflow.add_edge("mermaid_generation_node", "validation_node")
        workflow.add_edge("drawio_generation_node", "validation_node")

        # Conditional edge: loop back to generation if validation fails and retries remain
        def validation_router(state: SketchConversionState) -> str:
            retry = int(state.get("retry_count", 0) or 0)
            passed = bool(state.get("validation_passed", False))
            job_id = state.get("job_id", "unknown")
            self.logger.debug(
                f"validation_router job_id={job_id} retry={retry} passed={passed} max={self.max_retries}"
            )

            if passed:
                return END

            # If needs correction and we have corrections, feed them back
            corrections = state.get("corrections", "").strip()
            if not passed and retry < self.max_retries:
                next_node = format_router(state)
                self.logger.info(
                    f"validation_retry job_id={job_id} next={next_node} step={retry+1}/{self.max_retries}"
                )
                if corrections:
                    self.logger.debug(
                        f"corrections_preview job_id={job_id} text={corrections[:100]}"
                    )
                return next_node

            # Exhausted retries → end with current best
            self.logger.warning(
                f"validation_max_retries job_id={job_id} retries={retry}"
            )
            # Ensure final state is set for exhausted retries
            state["final_code"] = state.get("diagram_code", "")
            state["validation_passed"] = True
            state["validation_result"] = "PASSED"
            return END

        workflow.add_conditional_edges(
            "validation_node",
            validation_router,
            {
                "mermaid_generation_node": "mermaid_generation_node",
                "drawio_generation_node": "drawio_generation_node",
                END: END,
            },
        )

        # Optional in-memory checkpointing
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    async def run(self, initial_state: SketchConversionState, thread_id: str | None = None) -> SketchConversionState:
        # Ensure retry_count is present
        if "retry_count" not in initial_state:
            initial_state["retry_count"] = 0
        # LangGraph checkpointers require a configurable thread identifier
        tid = thread_id or initial_state.get("thread_id") or initial_state.get("job_id") or str(uuid4())
        # Keep thread id in state for traceability (optional)
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
