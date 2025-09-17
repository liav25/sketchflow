from typing import Dict, Any
from datetime import datetime
import asyncio


from app.services.graph_workflow import SketchConversionGraph
from app.core.config import settings
from app.core.logging_config import get_logger


class ConversionService:
    def __init__(self):
        self.logger = get_logger("sketchflow.conversion")
        # Configure LangSmith tracing if available
        import os
        if os.getenv("LANGSMITH_API_KEY") and not os.getenv("LANGCHAIN_TRACING_V2"):
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if os.getenv("LANGSMITH_API_KEY") and not os.getenv("LANGCHAIN_PROJECT"):
            os.environ["LANGCHAIN_PROJECT"] = "SketchFlow"

        self.graph = SketchConversionGraph()
    
    
    async def convert(self, file_path: str, format: str, notes: str, job_id: str) -> Dict[str, Any]:
        """Run the new 4-agent conversion pipeline using LangGraph."""
        # Dev mock: short-circuit the pipeline if enabled
        if settings.mock_mode:
            if settings.mock_latency_ms and settings.mock_latency_ms > 0:
                await asyncio.sleep(settings.mock_latency_ms / 1000.0)

            code = (
                f"""flowchart TD
    A[Start] --> B[{notes if notes else 'Process'}]
    B --> C[Decision]
    C -->|Yes| D[Success]
    C -->|No| E[Retry]
    E --> B
    D --> F[End]"""
                if format == "mermaid"
                else f"""<mxfile host="app.diagrams.net">
  <diagram name=\"Page-1\">
    <mxGraphModel dx=\"800\" dy=\"600\" grid=\"1\" gridSize=\"10\" guides=\"1\">
      <root>
        <mxCell id=\"0\"/>
        <mxCell id=\"1\" parent=\"0\"/>
        <mxCell id=\"2\" value=\"Start\" style=\"ellipse;whiteSpace=wrap;html=1;\" vertex=\"1\" parent=\"1\">
          <mxGeometry x=\"40\" y=\"40\" width=\"80\" height=\"40\" as=\"geometry\"/>
        </mxCell>
        <mxCell id=\"3\" value=\"{notes if notes else 'Process'}\" style=\"rounded=1;whiteSpace=wrap;html=1;\" vertex=\"1\" parent=\"1\">
          <mxGeometry x=\"160\" y=\"40\" width=\"120\" height=\"60\" as=\"geometry\"/>
        </mxCell>
        <mxCell id=\"4\" value=\"End\" style=\"ellipse;whiteSpace=wrap;html=1;\" vertex=\"1\" parent=\"1\">
          <mxGeometry x=\"320\" y=\"40\" width=\"80\" height=\"40\" as=\"geometry\"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
            )

            return {
                "format": format,
                "code": code,
                "job_id": job_id,
                "processing_time": datetime.now().isoformat(),
                "agents_used": ["mock"],
                "confidence_score": 0.9,
            }

        self.logger.info(f"Conversion pipeline start job_id={job_id} format={format}")

        # Initial state for new 4-agent graph
        state: Dict[str, Any] = {
            "file_path": file_path,
            "user_notes": notes,
            "target_format": format,
            "job_id": job_id,
        }

        # Execute the new 4-agent graph
        final_state = await self.graph.run(state)

        self.logger.info(f"Conversion pipeline completed job_id={job_id}")

        # Extract results from final state
        processing_path = final_state.get("processing_path", [])
        confidence_score = final_state.get("confidence_score", 0.5)
        final_diagram = final_state.get("final_diagram", "")

        # Return result in expected format
        return {
            "format": format,
            "code": final_diagram,
            "job_id": job_id,
            "processing_time": datetime.now().isoformat(),
            "agents_used": processing_path,
            "confidence_score": confidence_score,
        }
