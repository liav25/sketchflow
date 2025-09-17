"""
Structure Analysis Agent - Agent 2 of the new 4-agent architecture.

Identifies abstract patterns and relationships in the described scene.
Single responsibility: Convert scene description to structural understanding.
"""

import os
from typing import Dict, Any

from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.llm_factory import get_task_optimized_model, TaskType
from app.prompts.prompt_templates import PromptTemplates
from app.core.logging_config import get_logger


class StructureAnalysisAgent:
    """
    Agent 2: Structure Analysis
    
    Single Goal: Identify abstract patterns and relationships
    Input: Scene description + user notes
    Output: Abstract structural representation
    Model: Reasoning model (Claude Sonnet or GPT-4)
    """
    
    def __init__(self, *, model_override: str | None = None):
        self.prompt_templates = PromptTemplates()
        self.logger = get_logger("sketchflow.structure_analysis")
        
        # Use task-optimized model for reasoning tasks
        self.client, self.provider = get_task_optimized_model(
            TaskType.REASONING,
            override_model=model_override
        )
    
    @traceable(name="structure_analysis_agent")
    async def analyze_structure(self, state: SketchConversionState) -> SketchConversionState:
        """
        Analyze the scene description to identify abstract structure and patterns.
        
        Args:
            state: Current state containing scene_description and user_notes
            
        Returns:
            Updated state with structural_analysis
        """
        job_id = state.get('job_id', 'unknown')
        self.logger.info(f"structure_analysis_start job_id={job_id}")
        
        # Update processing path
        processing_path = state.get('processing_path', [])
        processing_path.append('structure_analysis')
        state['processing_path'] = processing_path
        
        # Get the structure analysis prompt
        prompt = self.prompt_templates.get_structure_analysis_prompt(
            scene_description=state.get('scene_description', ''),
            user_notes=state.get('user_notes', '')
        )
        
        try:
            # Create message
            message = HumanMessage(content=prompt)
            
            # Get response from reasoning LLM
            response = await self.client.ainvoke([message])
            structural_analysis = response.content.strip()
            
            # Update state with structural analysis
            state['structural_analysis'] = structural_analysis
            
            self.logger.info(f"structure_analysis_complete job_id={job_id}")
            return state
            
        except Exception as e:
            self.logger.exception(f"structure_analysis_error job_id={job_id} error={e}")
            
            # Graceful degradation: create basic structural analysis
            scene_desc = state.get('scene_description', '')
            user_notes = state.get('user_notes', '')
            
            fallback_analysis = f"""
**Element Types**: Process steps and connections (inferred from description)

**Connection Patterns**: Sequential flow with possible decision points

**Suggested Diagram Type**: Flowchart (best guess based on available information)

**Key Relationships**: Elements appear to be connected in a logical sequence

**Flow Direction**: Top-to-bottom or left-to-right (standard flowchart layout)

Note: This analysis was generated as a fallback due to processing error.
Original scene: {scene_desc[:100]}...
User context: {user_notes}
"""
            
            state['structural_analysis'] = fallback_analysis.strip()
            return state