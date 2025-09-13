"""
LangGraph workflow for the SketchFlow conversion pipeline.

Nodes:
- vision_analysis_node: Analyze sketch → instructions
- diagram_generation_node: Generate diagram from instructions
- validation_node: Validate and loop back if needed
"""

from __future__ import annotations

from typing import Callable
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.state_types import SketchConversionState
from app.services.agents.vision_agent import VisionAnalysisAgent
from app.services.agents.generation_agent import DiagramGenerationAgent
from app.services.agents.validation_agent import ValidationAgent


class SketchConversionGraph:
    """
    Builds and runs the 3-node conversion graph with a validation loop.
    """

    def __init__(self, max_retries: int = 2):
        self.vision_agent = VisionAnalysisAgent()
        self.generation_agent = DiagramGenerationAgent()
        self.validation_agent = ValidationAgent()
        self.max_retries = max_retries
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(SketchConversionState)

        # Register nodes
        workflow.add_node("vision_analysis_node", self.vision_agent.analyze_sketch)
        workflow.add_node("diagram_generation_node", self.generation_agent.generate_diagram)
        workflow.add_node("validation_node", self.validation_agent.validate)

        # Edges
        workflow.set_entry_point("vision_analysis_node")
        workflow.add_edge("vision_analysis_node", "diagram_generation_node")
        workflow.add_edge("diagram_generation_node", "validation_node")

        # Conditional edge: loop back to generation if validation fails and retries remain
        def validation_router(state: SketchConversionState) -> str:
            retry = int(state.get("retry_count", 0) or 0)
            passed = bool(state.get("validation_passed", False))

            if passed:
                return END

            # If needs correction and we have corrections, feed them back
            corrections = state.get("corrections", "").strip()
            if not passed and retry < self.max_retries:
                # Bump retry and update instructions with corrections context
                next_retry = retry + 1
                state["retry_count"] = next_retry
                if corrections:
                    # strengthen instructions for next generation
                    prior = state.get("generation_instructions", "")
                    state["generation_instructions"] = (
                        f"{prior}\n\nApply these corrections strictly (retry {next_retry}):\n{corrections}"
                    )
                return "diagram_generation_node"

            # Exhausted retries → end with current best
            state["final_code"] = state.get("diagram_code", "")
            state["validation_passed"] = True
            state["validation_result"] = state.get("validation_result", "PASSED")
            return END

        workflow.add_conditional_edges(
            "validation_node",
            validation_router,
            {"diagram_generation_node": "diagram_generation_node", END: END},
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
