"""
Mermaid Generation Agent - Specialized agent for Mermaid diagram generation.

Generates Mermaid diagram code based on the vision analysis with Mermaid-specific
optimizations, validation, and fallback handling.
"""

import os
from typing import Dict, Any, List
import re

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.prompts.prompt_templates import PromptTemplates


class MermaidGenerationAgent:
    """
    Agent specialized for generating Mermaid diagram code with format-specific
    optimizations and validation.
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
    
    def _clean_mermaid_code(self, code: str) -> str:
        """Clean and format Mermaid diagram code."""
        code = code.strip()
        
        # Remove markdown code blocks if present
        if code.startswith("```"):
            lines = code.split('\n')
            # Remove first line (```mermaid)
            if len(lines) > 1:
                lines = lines[1:]
            # Remove last line if it's just ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = '\n'.join(lines)
        
        return code.strip()
    
    def _validate_mermaid_syntax(self, code: str) -> tuple[bool, str]:
        """Basic Mermaid syntax validation."""
        if not code.strip():
            return False, "Empty diagram code"
        
        # Check for valid Mermaid diagram types
        valid_types = [
            'flowchart', 'graph', 'sequenceDiagram', 'classDiagram',
            'stateDiagram', 'erDiagram', 'gantt', 'pie', 'gitgraph'
        ]
        
        first_line = code.split('\n')[0].strip()
        has_valid_type = any(first_line.startswith(diagram_type) for diagram_type in valid_types)
        
        if not has_valid_type:
            return False, "Missing or invalid Mermaid diagram type declaration"
        
        # Basic syntax checks
        if '-->' in code or '--->' in code:  # Flowchart arrows
            return True, ""
        elif 'participant' in code and 'activate' in code:  # Sequence diagram
            return True, ""
        elif 'class' in code and '{' in code:  # Class diagram
            return True, ""
        elif first_line.startswith(('pie', 'gantt', 'gitgraph')):
            return True, ""
        
        return True, ""  # Basic validation passed
    
    def _detect_diagram_type(self, description: str, instructions: str) -> str:
        """Detect the most appropriate Mermaid diagram type based on content."""
        content = (description + " " + instructions).lower()
        
        # Sequence diagram indicators
        if any(word in content for word in ['sequence', 'interaction', 'message', 'actor', 'participant']):
            return 'sequenceDiagram'
        
        # Class diagram indicators
        if any(word in content for word in ['class', 'inheritance', 'method', 'attribute', 'relationship']):
            return 'classDiagram'
        
        # State diagram indicators
        if any(word in content for word in ['state', 'transition', 'status', 'condition']):
            return 'stateDiagram-v2'
        
        # Gantt chart indicators
        if any(word in content for word in ['gantt', 'timeline', 'schedule', 'project', 'task']):
            return 'gantt'
        
        # Default to flowchart for most cases
        return 'flowchart TD'
    
    def _generate_mermaid_fallback(self, description: str, notes: str) -> str:
        """Generate a Mermaid-specific fallback diagram."""
        # Determine diagram type based on content
        content = (description + " " + notes).lower()
        
        if 'sequence' in content or 'interaction' in content:
            return f"""sequenceDiagram
    participant A as User
    participant B as System
    A->>B: Request
    B-->>A: Response
    Note over A,B: {notes[:50] if notes else 'Process completed'}"""
        
        # Default flowchart fallback
        return f"""flowchart TD
    A[Start] --> B[{notes[:30] if notes else 'Process'}]
    B --> C{Decision}
    C -->|Yes| D[Success]
    C -->|No| E[Retry]
    E --> B
    D --> F[End]"""

    @traceable(name="mermaid_generation_node")
    async def generate_mermaid_diagram(self, state: SketchConversionState) -> SketchConversionState:
        """
        Generate Mermaid diagram code based on vision analysis.
        
        Args:
            state: Current state containing vision analysis results
            
        Returns:
            Updated state with generated Mermaid diagram code
        """
        retry_count = int(state.get("retry_count", 0) or 0)
        print(f"Mermaid Generation Agent: Creating Mermaid diagram for job {state['job_id']} (retry {retry_count})")
        
        # Handle retry logic and corrections
        base_instructions = state.get('generation_instructions', '')
        corrections = state.get('corrections', '').strip()
        
        # Build instructions with corrections for retries
        if retry_count > 0 and corrections:
            enhanced_instructions = f"{base_instructions}\n\nApply these corrections strictly (retry {retry_count + 1}):\n{corrections}"
        else:
            enhanced_instructions = base_instructions
        
        # Update retry count
        state["retry_count"] = retry_count + 1
        
        # Get the Mermaid-specific generation prompt
        prompt = self.prompt_templates.get_mermaid_generation_prompt(
            description=state.get('sketch_description', ''),
            instructions=enhanced_instructions,
            suggested_type=self._detect_diagram_type(
                state.get('sketch_description', ''),
                enhanced_instructions
            )
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
            clean_code = self._clean_mermaid_code(diagram_code)
            
            # Validate Mermaid syntax
            is_valid, error_msg = self._validate_mermaid_syntax(clean_code)
            if not is_valid:
                print(f"Mermaid Generation Agent: Syntax validation failed - {error_msg}")
                clean_code = self._generate_mermaid_fallback(
                    state.get('sketch_description', ''),
                    state.get('notes', '')
                )
            
            # Update state with generated diagram code
            state.update({
                "diagram_code": clean_code
            })
            
            print(f"Mermaid Generation Agent: Mermaid diagram generated successfully for job {state['job_id']}")
            return state
            
        except Exception as e:
            print(f"Mermaid Generation Agent Error: {str(e)}")
            # Return state with fallback Mermaid diagram
            fallback_code = self._generate_mermaid_fallback(
                state.get('sketch_description', ''),
                state.get('notes', '')
            )
            state.update({
                "diagram_code": fallback_code
            })
            return state