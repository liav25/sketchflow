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
from app.prompts.prompt_templates import PromptTemplates
from app.core.logging_config import get_logger


class VisionAnalysisAgent:
    """
    Agent responsible for analyzing sketch images and generating
    detailed descriptions and instructions for diagram generation.
    """
    
    def __init__(self):
        self.prompt_templates = PromptTemplates()
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_llm_clients()
        self.logger = get_logger("sketchflow.vision")
    
    def _initialize_llm_clients(self):
        """Initialize vision-capable LLM clients."""
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if openai_key:
            self.openai_client = ChatOpenAI(
                model=os.getenv("VISION_LLM_MODEL", "gpt-4.1"),  # configurable
                api_key=openai_key,
                temperature=0.1
            )
        
        if anthropic_key:
            self.anthropic_client = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",  # Claude-3 with vision
                api_key=anthropic_key,
                temperature=0.1
            )
    
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
            
            # Choose LLM client (prefer OpenAI GPT-4V, fallback to Claude)
            client = self.openai_client or self.anthropic_client
            
            if not client:
                raise ValueError("No vision-capable LLM client available. Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY.")
            
            # Create message with image
            if isinstance(client, ChatOpenAI):
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
