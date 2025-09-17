"""
Scene Understanding Agent - Agent 1 of the new 4-agent architecture.

Provides natural language description of what's in the image.
Single responsibility: Convert image to human-readable scene description.
"""

import base64
import os
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.llm_factory import get_task_optimized_model, TaskType
from app.prompts.prompt_templates import PromptTemplates
from app.core.logging_config import get_logger


class SceneUnderstandingAgent:
    """
    Agent 1: Scene Understanding
    
    Single Goal: Understand what's in the image at a high level
    Output: Natural language description only
    Model: Vision-capable model (GPT-4V/Claude Vision)
    """
    
    def __init__(self, *, model_override: str | None = None):
        self.prompt_templates = PromptTemplates()
        self.logger = get_logger("sketchflow.scene_understanding")
        
        # Use task-optimized model for vision tasks
        self.client, self.provider = get_task_optimized_model(
            TaskType.VISION,
            override_model=model_override
        )
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image file to base64 for vision LLM."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    @traceable(name="scene_understanding_agent")
    async def understand_scene(self, state: SketchConversionState) -> SketchConversionState:
        """
        Analyze the sketch image and provide natural language description.
        
        Args:
            state: Current state containing file path and user notes
            
        Returns:
            Updated state with scene_description
        """
        job_id = state.get('job_id', 'unknown')
        self.logger.info(f"scene_understanding_start job_id={job_id}")
        
        # Update processing path
        processing_path = state.get('processing_path', [])
        processing_path.append('scene_understanding')
        state['processing_path'] = processing_path
        
        # Get the scene understanding prompt
        prompt = self.prompt_templates.get_scene_understanding_prompt(
            user_notes=state.get('user_notes', '')
        )
        
        try:
            # Encode the image
            base64_image = self._encode_image(state['file_path'])
            
            # Create message with image
            if self.provider == "openai" or isinstance(self.client, ChatOpenAI):
                # OpenAI format
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                )
            else:
                # Anthropic format
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image", 
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                )
            
            # Get response from vision LLM
            response = await self.client.ainvoke([message])
            scene_description = response.content.strip()
            
            # Update state with scene description
            state['scene_description'] = scene_description
            
            self.logger.info(f"scene_understanding_complete job_id={job_id}")
            return state
            
        except Exception as e:
            self.logger.exception(f"scene_understanding_error job_id={job_id} error={e}")
            
            # Graceful degradation: use user notes as scene description
            fallback_description = (
                f"Unable to analyze image due to technical error. "
                f"User notes: {state.get('user_notes', 'No additional context provided.')}"
            )
            
            state['scene_description'] = fallback_description
            return state