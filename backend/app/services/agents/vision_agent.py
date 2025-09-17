"""
Vision Analysis Agent - Node 1 of the SketchFlow conversion pipeline.

Analyzes uploaded sketch images using vision-capable LLMs and extracts
structural information for diagram generation.
"""

import base64
import os
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.llm_factory import get_chat_model
from app.prompts.prompt_templates import PromptTemplates
from app.core.logging_config import get_logger


class VisionAnalysisAgent:
    """
    Agent responsible for analyzing sketch images and generating
    detailed descriptions and instructions for diagram generation.
    """
    
    def __init__(self, *, model: str | None = None, temperature: float | None = None):
        self.prompt_templates = PromptTemplates()
        self.client = None
        self.provider = None
        self.logger = get_logger("sketchflow.vision")
        # Resolve model and temperature from args or env
        resolved_model = model or os.getenv("VISION_LLM_MODEL", "gpt-4.1")
        resolved_temp = 0.1 if temperature is None else float(temperature)
        # Initialize a single client based on model
        self.client, self.provider = get_chat_model(resolved_model, temperature=resolved_temp)

    
    def _encode_image(self, image_path: str) -> str:
        """Encode image file to base64 for vision LLM."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, str]:
        """Parse the structured response from the vision LLM."""
        result = {
            "sketch_description": "",
            "identified_elements": "",
            "structure_analysis": "",
            "generation_instructions": ""
        }
        
        current_section = None
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("SKETCH DESCRIPTION:"):
                current_section = "sketch_description"
                continue
            elif line.startswith("IDENTIFIED ELEMENTS:"):
                current_section = "identified_elements"
                continue
            elif line.startswith("STRUCTURE ANALYSIS:"):
                current_section = "structure_analysis"
                continue
            elif line.startswith("GENERATION INSTRUCTIONS:"):
                current_section = "generation_instructions"
                continue
            
            if current_section and line:
                if result[current_section]:
                    result[current_section] += "\n" + line
                else:
                    result[current_section] = line
        
        return result
    
    @traceable(name="vision_analysis_node")
    async def analyze_sketch(self, state: SketchConversionState) -> SketchConversionState:
        """
        Analyze the uploaded sketch image and generate description + instructions.
        
        Args:
            state: Current state containing file path, format, and notes
            
        Returns:
            Updated state with vision analysis results
        """
        self.logger.info(f"vision_start job_id={state.get('job_id','?')} format={state['format']}")
        
        # Get the vision analysis prompt
        prompt = self.prompt_templates.get_vision_analysis_prompt(
            notes=state['notes'],
            format_type=state['format']
        )
        
        try:
            # Encode the image
            base64_image = self._encode_image(state['file_path'])
            
            # Use the single configured client
            client = self.client
            if not client:
                raise ValueError("No vision-capable LLM client available. Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY.")
            
            # Create message with image
            if self.provider == "openai" or isinstance(client, ChatOpenAI):
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
            response = await client.ainvoke([message])
            response_text = response.content
            
            # Parse the structured response
            analysis_results = self._parse_analysis_response(response_text)
            
            # Update state with analysis results
            state.update({
                "sketch_description": analysis_results["sketch_description"],
                "identified_elements": analysis_results["identified_elements"],
                "structure_analysis": analysis_results["structure_analysis"],
                "generation_instructions": analysis_results["generation_instructions"]
            })
            
            self.logger.info(f"vision_complete job_id={state['job_id']}")
            return state
            
        except Exception as e:
            self.logger.exception(f"vision_error job_id={state.get('job_id','?')} error={e}")
            # Return state with error information
            state.update({
                "sketch_description": f"Error during vision analysis: {str(e)}",
                "identified_elements": "",
                "structure_analysis": "",
                "generation_instructions": f"Generate a simple {state['format']} diagram based on the notes: {state['notes']}"
            })
            return state
