"""
Diagram Generation Agent - Node 2 of the SketchFlow conversion pipeline.

Generates diagram code (Mermaid or Draw.io) based on the vision analysis
and user specifications.
"""

import os
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.prompts.prompt_templates import PromptTemplates


class DiagramGenerationAgent:
    """
    Agent responsible for generating diagram code based on vision analysis
    and format specifications.
    """
    
    def __init__(self):
        self.prompt_templates = PromptTemplates()
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_llm_clients()
    
    def _initialize_llm_clients(self):
        """Initialize text-based LLM clients."""
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if openai_key:
            self.openai_client = ChatOpenAI(
                model=os.getenv("GENERATION_LLM_MODEL", "gpt-4.1"),
                api_key=openai_key,
                temperature=0.1
            )
        
        if anthropic_key:
            self.anthropic_client = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=anthropic_key,
                temperature=0.1
            )
    
    def _clean_diagram_code(self, code: str, format_type: str) -> str:
        """Clean and format the generated diagram code."""
        # Remove markdown code blocks if present
        code = code.strip()
        
        if code.startswith("```"):
            lines = code.split('\n')
            # Remove first line (```format_type)
            if len(lines) > 1:
                lines = lines[1:]
            # Remove last line if it's just ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = '\n'.join(lines)
        
        return code.strip()
    
    @traceable(name="diagram_generation_node")
    async def generate_diagram(self, state: SketchConversionState) -> SketchConversionState:
        """
        Generate diagram code based on vision analysis and format specification.
        
        Args:
            state: Current state containing vision analysis results
            
        Returns:
            Updated state with generated diagram code
        """
        print(f"Generation Agent: Creating {state['format']} diagram")
        
        # Get the diagram generation prompt
        prompt = self.prompt_templates.get_diagram_generation_prompt(
            description=state.get('sketch_description', ''),
            instructions=state.get('generation_instructions', ''),
            format_type=state['format']
        )
        
        try:
            # Choose LLM client (prefer OpenAI, fallback to Anthropic)
            client = self.openai_client or self.anthropic_client
            
            if not client:
                raise ValueError("No LLM client available. Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY.")
            
            # Create message
            message = HumanMessage(content=prompt)
            
            # Get response from LLM
            response = await client.ainvoke([message])
            diagram_code = response.content
            
            # Clean the generated code
            clean_code = self._clean_diagram_code(diagram_code, state['format'])
            
            # Update state with generated diagram code
            state.update({
                "diagram_code": clean_code
            })
            
            print(f"Generation Agent: Diagram generated for job {state['job_id']}")
            return state
            
        except Exception as e:
            print(f"Generation Agent Error: {str(e)}")
            # Return state with fallback diagram code
            fallback_code = self._generate_fallback_diagram(state['format'], state.get('notes', ''))
            state.update({
                "diagram_code": fallback_code
            })
            return state
    
    def _generate_fallback_diagram(self, format_type: str, notes: str) -> str:
        """Generate a simple fallback diagram when LLM generation fails."""
        if format_type == "mermaid":
            return f"""flowchart TD
    A[Start] --> B[{notes if notes else 'Process'}]
    B --> C[Decision]
    C -->|Yes| D[Success]
    C -->|No| E[Retry]
    E --> B
    D --> F[End]"""
        else:  # drawio
            return f"""<mxfile host="app.diagrams.net">
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
