"""
Synthesis Agent - Agent 4 of the new 4-agent architecture.

Selects and refines the best diagram candidate.
Single responsibility: Choose the best approach and polish it.
"""

import os
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState, DiagramCandidate
from app.core.llm_factory import get_task_optimized_model, TaskType
from app.prompts.prompt_templates import PromptTemplates
from app.core.logging_config import get_logger


class SynthesisAgent:
    """
    Agent 4: Synthesis & Refinement
    
    Single Goal: Select and polish the best candidate
    Input: All candidates + original requirements
    Output: Final polished diagram
    Model: Reasoning model (Claude Sonnet for synthesis)
    """
    
    def __init__(self, *, model_override: str | None = None):
        self.prompt_templates = PromptTemplates()
        self.logger = get_logger("sketchflow.synthesis")
        
        # Use task-optimized model for synthesis tasks
        self.client, self.provider = get_task_optimized_model(
            TaskType.SYNTHESIS,
            override_model=model_override
        )
    
    def _format_candidates_for_prompt(self, candidates: List[DiagramCandidate]) -> str:
        """Format the candidates list for the prompt."""
        if not candidates:
            return "No candidates available."
        
        formatted_candidates = []
        for i, candidate in enumerate(candidates, 1):
            formatted_candidates.append(f"""
**Candidate {i}**: {candidate.style_approach}
Confidence: {candidate.confidence_score:.1f}
Reasoning: {candidate.reasoning}

Code:
{candidate.code}
""")
        
        return "\n".join(formatted_candidates)
    
    def _calculate_overall_confidence(self, candidates: List[DiagramCandidate], selected_code: str) -> float:
        """Calculate overall confidence score for the final result."""
        if not candidates:
            return 0.3  # Low confidence for fallback
        
        # Find the candidate that matches the selected code (or closest match)
        best_match = None
        best_match_score = 0.0
        
        for candidate in candidates:
            # Simple similarity check (could be improved)
            if candidate.code.strip() == selected_code.strip():
                best_match = candidate
                break
            elif len(candidate.code) > 0 and len(selected_code) > 0:
                # Basic similarity based on length and common content
                common_chars = sum(1 for a, b in zip(candidate.code, selected_code) if a == b)
                similarity = common_chars / max(len(candidate.code), len(selected_code))
                if similarity > best_match_score:
                    best_match = candidate
                    best_match_score = similarity
        
        if best_match:
            return best_match.confidence_score
        else:
            # Average confidence from all candidates
            avg_confidence = sum(c.confidence_score for c in candidates) / len(candidates)
            return avg_confidence * 0.8  # Slight penalty for synthesis process
    
    @traceable(name="synthesis_agent")
    async def synthesize_final_diagram(self, state: SketchConversionState) -> SketchConversionState:
        """
        Select and refine the best diagram candidate.
        
        Args:
            state: Current state containing all previous agent outputs
            
        Returns:
            Updated state with final_diagram and confidence_score
        """
        job_id = state.get('job_id', 'unknown')
        self.logger.info(f"synthesis_start job_id={job_id}")
        
        # Update processing path
        processing_path = state.get('processing_path', [])
        processing_path.append('synthesis')
        state['processing_path'] = processing_path
        
        candidates = state.get('diagram_candidates', [])
        
        # If no candidates available, create a fallback
        if not candidates:
            self.logger.warning(f"No candidates available for synthesis job_id={job_id}")
            
            # Create a basic fallback diagram
            target_format = state.get('target_format', 'mermaid')
            if target_format.lower() == 'mermaid':
                fallback_code = """flowchart TD
    A[Start] --> B[Process]
    B --> C[End]"""
            else:
                fallback_code = """<mxfile host="app.diagrams.net">
  <diagram name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Process" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="160" y="40" width="120" height="60" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
            
            state['final_diagram'] = fallback_code
            state['confidence_score'] = 0.3
            return state
        
        # If only one candidate, use it directly
        if len(candidates) == 1:
            self.logger.info(f"Single candidate available, using directly job_id={job_id}")
            state['final_diagram'] = candidates[0].code
            state['confidence_score'] = candidates[0].confidence_score
            return state
        
        # Multiple candidates - use LLM to select and refine
        candidates_text = self._format_candidates_for_prompt(candidates)
        
        prompt = self.prompt_templates.get_synthesis_prompt(
            scene_description=state.get('scene_description', ''),
            structural_analysis=state.get('structural_analysis', ''),
            candidates=candidates_text,
            target_format=state.get('target_format', 'mermaid')
        )
        
        try:
            # Create message
            message = HumanMessage(content=prompt)
            
            # Get response from synthesis LLM
            response = await self.client.ainvoke([message])
            final_diagram = response.content.strip()
            
            # Calculate confidence based on candidates and selection
            confidence = self._calculate_overall_confidence(candidates, final_diagram)
            
            # Update state with final result
            state['final_diagram'] = final_diagram
            state['confidence_score'] = confidence
            
            self.logger.info(f"synthesis_complete job_id={job_id} confidence={confidence:.2f}")
            return state
            
        except Exception as e:
            self.logger.exception(f"synthesis_error job_id={job_id} error={e}")
            
            # Graceful degradation: use the first candidate
            fallback_candidate = candidates[0] if candidates else None
            if fallback_candidate:
                state['final_diagram'] = fallback_candidate.code
                state['confidence_score'] = fallback_candidate.confidence_score * 0.7  # Penalty for fallback
            else:
                # Ultimate fallback
                target_format = state.get('target_format', 'mermaid')
                state['final_diagram'] = "flowchart TD\n    A[Error] --> B[Please try again]" if target_format.lower() == 'mermaid' else "<mxfile><diagram><mxGraphModel><root><mxCell id='0'/><mxCell id='1' parent='0'/></root></mxGraphModel></diagram></mxfile>"
                state['confidence_score'] = 0.2
            
            return state