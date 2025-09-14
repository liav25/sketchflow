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

        self.graph = SketchConversionGraph(max_retries=2)
    
    async def _vision_analysis_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Agent 1: Analyze the sketch image and extract structure"""
        self.logger.debug(f"Vision analysis (mock) start format={state['format']}")
        
        # Mock analysis - just return format and notes
        state["analysis"] = {
            "format": state["format"],
            "notes": state["notes"],
            "elements": ["box1", "box2", "connection"],
            "timestamp": datetime.now().isoformat()
        }
        return state
    
    async def _diagram_generation_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Agent 2: Generate diagram code based on analysis"""
        format_type = state["analysis"]["format"]
        notes = state["analysis"]["notes"]
        
        self.logger.debug(f"Generation start format={format_type}")
        
        if format_type == "mermaid":
            # Simple Mermaid flowchart
            code = f"""flowchart TD
    A[Start] --> B[{notes if notes else 'Process'}]
    B --> C[Decision]
    C -->|Yes| D[Success]
    C -->|No| E[Retry]
    E --> B
    D --> F[End]"""
        else:  # drawio
            # Simple Draw.io XML
            code = f"""<mxfile host="app.diagrams.net">
  <diagram name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Start" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="80" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="{notes if notes else 'Process'}" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="160" y="40" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="End" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="320" y="40" width="80" height="40" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
        
        state["generated_code"] = code
        return state
    
    async def _validation_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Agent 3: Validate and correct the generated diagram"""
        self.logger.debug("Validation start")
        
        # Simple validation - just pass through for now
        state["validated_code"] = state["generated_code"]
        state["validation_status"] = "passed"
        
        return state
    
    async def convert(self, file_path: str, format: str, notes: str, job_id: str) -> Dict[str, Any]:
        """Run the 3-agent conversion pipeline using LangGraph with validation loop."""
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
            }

        self.logger.info(f"Conversion pipeline start job_id={job_id} format={format}")

        # Initial state for graph
        state: Dict[str, Any] = {
            "file_path": file_path,
            "format": format,
            "notes": notes,
            "job_id": job_id,
            "retry_count": 0,
        }

        # Execute graph
        final_state = await self.graph.run(state)

        self.logger.info(f"Conversion pipeline completed job_id={job_id}")

        # Return result
        return {
            "format": format,
            "code": final_state.get("final_code") or final_state.get("diagram_code", ""),
            "job_id": job_id,
            "processing_time": datetime.now().isoformat(),
            "agents_used": ["vision", "generation", "validation"],
        }
