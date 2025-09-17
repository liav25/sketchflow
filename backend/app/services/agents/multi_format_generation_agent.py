"""
Multi-Format Generation Agent - Agent 3 of the new 4-agent architecture.

Generates multiple diagram candidates in different approaches.
Single responsibility: Create 2-3 diagram options for the target format.
"""

import os
import re
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState, DiagramCandidate
from app.core.llm_factory import get_task_optimized_model, TaskType
from app.prompts.prompt_templates import PromptTemplates
from app.core.logging_config import get_logger


class MultiFormatGenerationAgent:
    """
    Agent 3: Multi-Format Generation
    
    Single Goal: Generate multiple diagram candidates
    Input: Scene + structure descriptions
    Output: 2-3 diagram candidates in different formats/styles
    Model: Code generation model
    """
    
    def __init__(self, *, model_override: str | None = None):
        self.prompt_templates = PromptTemplates()
        self.logger = get_logger("sketchflow.multi_format_generation")
        
        # Use task-optimized model for code generation
        self.client, self.provider = get_task_optimized_model(
            TaskType.CODE_GENERATION,
            override_model=model_override
        )
    
    def _parse_candidates_from_response(self, response_text: str, target_format: str) -> List[DiagramCandidate]:
        """Parse multiple diagram candidates from the LLM response."""
        candidates = []
        
        # Split the response by "Approach X:" patterns
        approach_pattern = r'\*\*Approach\s+(\d+)\*\*[:\s]*([^\n]*)'
        approaches = re.split(approach_pattern, response_text, flags=re.IGNORECASE)
        
        # Skip the first element (text before first approach)
        i = 1
        while i < len(approaches) - 1:
            try:
                approach_num = approaches[i]
                approach_desc = approaches[i + 1].strip()
                approach_content = approaches[i + 2] if i + 2 < len(approaches) else ""
                
                # Extract the diagram code from the content
                code = self._extract_diagram_code(approach_content, target_format)
                
                if code:
                    candidate = DiagramCandidate(
                        format=target_format,
                        code=code,
                        style_approach=approach_desc or f"Approach {approach_num}",
                        confidence_score=0.8,  # Default confidence
                        reasoning=f"Generated as approach {approach_num}: {approach_desc}"
                    )
                    candidates.append(candidate)
                
                i += 3  # Move to next approach
            except (IndexError, ValueError) as e:
                self.logger.warning(f"Failed to parse approach {i//3 + 1}: {e}")
                i += 3
        
        return candidates
    
    def _extract_diagram_code(self, content: str, target_format: str) -> str:
        """Extract clean diagram code from response content."""
        if target_format.lower() == "mermaid":
            # Look for Mermaid diagram code
            patterns = [
                r'```mermaid\s*(.*?)\s*```',
                r'```\s*(flowchart[^\n]*(?:\n(?!```).*)*)',
                r'```\s*(sequenceDiagram[^\n]*(?:\n(?!```).*)*)',
                r'```\s*(classDiagram[^\n]*(?:\n(?!```).*)*)',
                r'(flowchart\s+[^\n]*(?:\n(?!Approach).*)*)',
                r'(sequenceDiagram[^\n]*(?:\n(?!Approach).*)*)',
                r'(classDiagram[^\n]*(?:\n(?!Approach).*)*)'
            ]
        else:  # drawio
            # Look for Draw.io XML
            patterns = [
                r'```xml\s*(.*?)\s*```',
                r'```\s*(<mxfile.*?</mxfile>)',
                r'(<mxfile.*?</mxfile>)'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                if code:
                    return code
        
        # Fallback: try to find any code-like content
        lines = content.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Start collecting if we see diagram keywords
            if any(keyword in stripped.lower() for keyword in 
                   ['flowchart', 'sequencediagram', 'classdiagram', '<mxfile', 'graph']):
                in_code = True
                code_lines.append(stripped)
            elif in_code and not stripped.startswith(('*', '#', 'Approach')):
                code_lines.append(stripped)
            elif in_code and stripped.startswith(('*', '#', 'Approach')):
                break
        
        return '\n'.join(code_lines) if code_lines else ""
    
    def _generate_fallback_candidates(self, target_format: str, scene_desc: str, struct_analysis: str) -> List[DiagramCandidate]:
        """Generate fallback candidates when parsing fails."""
        candidates = []
        
        if target_format.lower() == "mermaid":
            # Simple Mermaid flowchart
            code = """flowchart TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Success]
    C -->|No| E[Retry]
    E --> B
    D --> F[End]"""
        else:  # drawio
            # Simple Draw.io XML
            code = """<mxfile host="app.diagrams.net">
  <diagram name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Start" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="80" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Process" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="160" y="40" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="End" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="320" y="40" width="80" height="40" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
        
        candidate = DiagramCandidate(
            format=target_format,
            code=code,
            style_approach="Fallback approach",
            confidence_score=0.5,
            reasoning="Generated as fallback when primary generation failed"
        )
        candidates.append(candidate)
        
        return candidates
    
    @traceable(name="multi_format_generation_agent")
    async def generate_candidates(self, state: SketchConversionState) -> SketchConversionState:
        """
        Generate multiple diagram candidates based on scene and structure analysis.
        
        Args:
            state: Current state containing scene_description and structural_analysis
            
        Returns:
            Updated state with diagram_candidates
        """
        job_id = state.get('job_id', 'unknown')
        target_format = state.get('target_format', 'mermaid')
        
        self.logger.info(f"multi_format_generation_start job_id={job_id} format={target_format}")
        
        # Update processing path
        processing_path = state.get('processing_path', [])
        processing_path.append('multi_format_generation')
        state['processing_path'] = processing_path
        
        # Get the multi-format generation prompt
        prompt = self.prompt_templates.get_multi_format_generation_prompt(
            scene_description=state.get('scene_description', ''),
            structural_analysis=state.get('structural_analysis', ''),
            target_format=target_format
        )
        
        try:
            # Create message
            message = HumanMessage(content=prompt)
            
            # Get response from code generation LLM
            response = await self.client.ainvoke([message])
            response_text = response.content
            
            # Parse candidates from response
            candidates = self._parse_candidates_from_response(response_text, target_format)
            
            # If no candidates were parsed, generate fallbacks
            if not candidates:
                self.logger.warning(f"No candidates parsed from response, generating fallbacks job_id={job_id}")
                candidates = self._generate_fallback_candidates(
                    target_format,
                    state.get('scene_description', ''),
                    state.get('structural_analysis', '')
                )
            
            # Update state with candidates
            state['diagram_candidates'] = candidates
            
            self.logger.info(f"multi_format_generation_complete job_id={job_id} candidates_count={len(candidates)}")
            return state
            
        except Exception as e:
            self.logger.exception(f"multi_format_generation_error job_id={job_id} error={e}")
            
            # Graceful degradation: generate fallback candidates
            candidates = self._generate_fallback_candidates(
                target_format,
                state.get('scene_description', ''),
                state.get('structural_analysis', '')
            )
            
            state['diagram_candidates'] = candidates
            return state