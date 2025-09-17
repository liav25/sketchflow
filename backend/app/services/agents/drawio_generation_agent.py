"""
Draw.io Generation Agent - Specialized agent for Draw.io diagram generation.

Generates Draw.io XML diagram code based on the vision analysis with Draw.io-specific
optimizations, validation, and fallback handling.
"""

import os
from typing import Dict, Any, List
import re
import xml.etree.ElementTree as ET

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.core.llm_factory import get_chat_model
from app.prompts.prompt_templates import PromptTemplates


class DrawioGenerationAgent:
    """
    Agent specialized for generating Draw.io XML diagram code with format-specific
    optimizations and validation.
    """
    
    def __init__(self, *, model: str | None = None, temperature: float | None = None):
        self.prompt_templates = PromptTemplates()
        self.client = None
        self.provider = None
        resolved_model = model or os.getenv("GENERATION_LLM_MODEL", "gpt-4.1")
        resolved_temp = 0.1 if temperature is None else float(temperature)
        self.client, self.provider = get_chat_model(resolved_model, temperature=resolved_temp)
    
    def _clean_drawio_code(self, code: str) -> str:
        """Clean and normalize Draw.io XML code returned by an LLM.

        Handles common issues:
        - Fenced code blocks (```xml / ```drawio)
        - Leading/trailing commentary around the XML
        - HTML entity escaping (e.g., &lt;mxfile&gt;)
        - Extra XML prolog – we require output to start at <mxfile>
        """
        import html

        txt = (code or "").strip()

        # Strip fenced code blocks
        if txt.startswith("```"):
            lines = txt.split("\n")
            if len(lines) > 1:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            txt = "\n".join(lines)

        txt = txt.strip()

        # Unescape common HTML entities if the model escaped XML
        if "&lt;mxfile" in txt or "&lt;/mxfile" in txt:
            txt = html.unescape(txt)

        # Remove any XML prolog and leading text before <mxfile>
        mx_start = txt.find("<mxfile")
        mx_end = txt.rfind("</mxfile>")
        if mx_start != -1 and mx_end != -1:
            # Include closing tag fully
            mx_end = mx_end + len("</mxfile>")
            txt = txt[mx_start:mx_end]

        return txt.strip()
    
    def _validate_drawio_xml(self, xml_code: str) -> tuple[bool, str]:
        """Validate Draw.io XML syntax and structure."""
        if not xml_code.strip():
            return False, "Empty XML code"
        
        try:
            # Parse XML to check for syntax errors
            root = ET.fromstring(xml_code)
            
            # Check for required Draw.io structure
            if root.tag != 'mxfile':
                return False, "Root element must be 'mxfile'"
            
            # Check for diagram element
            diagram = root.find('diagram')
            if diagram is None:
                return False, "Missing 'diagram' element"
            
            # Check for mxGraphModel
            graph_model = diagram.find('mxGraphModel')
            if graph_model is None:
                return False, "Missing 'mxGraphModel' element"
            
            # Check for root cells
            root_elem = graph_model.find('root')
            if root_elem is None:
                return False, "Missing 'root' element in mxGraphModel"
            
            # Check for basic cell structure
            cells = root_elem.findall('mxCell')
            if len(cells) < 2:  # At least root cell (id="0") and layer cell (id="1")
                return False, "Missing basic cell structure"

            # Ensure at least one vertex exists to avoid empty docs
            has_vertex = any(c.get('vertex') == '1' for c in cells)
            if not has_vertex:
                return False, "No vertex cells found"
            
            return True, ""
            
        except ET.ParseError as e:
            return False, f"XML parsing error: {str(e)}"
        except Exception as e:
            return False, f"XML validation error: {str(e)}"
    
    def _detect_diagram_style(self, description: str, instructions: str) -> Dict[str, Any]:
        """Detect the most appropriate Draw.io diagram style and layout."""
        content = (description + " " + instructions).lower()
        
        # Flowchart style
        if any(word in content for word in ['flow', 'process', 'decision', 'workflow']):
            return {
                'style': 'flowchart',
                'default_shape': 'rounded=1;whiteSpace=wrap;html=1;',
                'decision_shape': 'rhombus;whiteSpace=wrap;html=1;',
                'start_end_shape': 'ellipse;whiteSpace=wrap;html=1;'
            }
        
        # Organizational chart style
        if any(word in content for word in ['org', 'hierarchy', 'structure', 'organization']):
            return {
                'style': 'org_chart',
                'default_shape': 'rounded=0;whiteSpace=wrap;html=1;',
                'connector_style': 'orthogonalEdgeStyle',
                'layout': 'hierarchical'
            }
        
        # Network diagram style
        if any(word in content for word in ['network', 'server', 'connection', 'infrastructure']):
            return {
                'style': 'network',
                'default_shape': 'rounded=0;whiteSpace=wrap;html=1;',
                'server_shape': 'shape=cube;whiteSpace=wrap;html=1;',
                'network_shape': 'ellipse;shape=cloud;whiteSpace=wrap;html=1;'
            }
        
        # Default style
        return {
            'style': 'general',
            'default_shape': 'rounded=1;whiteSpace=wrap;html=1;',
            'connector_style': 'orthogonalEdgeStyle'
        }
    
    def _generate_drawio_fallback(self, description: str, notes: str) -> str:
        """Generate a Draw.io-specific fallback diagram."""
        # Determine layout based on content
        content = (description + " " + notes).lower()
        
        if 'network' in content or 'server' in content:
            return '''<mxfile host="app.diagrams.net">
  <diagram name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Client" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="80" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Server" style="shape=cube;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="240" y="80" width="120" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="5" value="''' + (notes[:50] if notes else 'Network Connection') + '''" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;" vertex="1" parent="1">
          <mxGeometry x="140" y="40" width="120" height="30" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
        
        # Default flowchart fallback
        return '''<mxfile host="app.diagrams.net">
  <diagram name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Start" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="160" y="40" width="80" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="''' + (notes[:30] if notes else 'Process') + '''" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="140" y="120" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="Decision" style="rhombus;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="160" y="220" width="80" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="5" value="End" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="160" y="340" width="80" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="3" target="4">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="8" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="4" target="5">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

    @traceable(name="drawio_generation_node")
    async def generate_drawio_diagram(self, state: SketchConversionState) -> SketchConversionState:
        """
        Generate Draw.io XML diagram code based on vision analysis.
        
        Args:
            state: Current state containing vision analysis results
            
        Returns:
            Updated state with generated Draw.io XML diagram code
        """
        retry_count = int(state.get("retry_count", 0) or 0)
        print(f"Draw.io Generation Agent: Creating Draw.io diagram for job {state['job_id']} (retry {retry_count})")
        
        # Detect diagram style preferences
        diagram_style = self._detect_diagram_style(
            state.get('sketch_description', ''),
            state.get('generation_instructions', '')
        )
        
        # Handle retry logic and corrections similar to Mermaid agent
        base_instructions = state.get('generation_instructions', '')
        corrections = state.get('corrections', '').strip()
        if retry_count > 0 and corrections:
            enhanced_instructions = f"{base_instructions}\n\nApply these validation instructions strictly (retry {retry_count + 1}):\n{corrections}"
        else:
            enhanced_instructions = base_instructions

        # Increment retry count for the loop
        state["retry_count"] = retry_count + 1

        # Get the Draw.io-specific generation prompt
        prompt = self.prompt_templates.get_drawio_generation_prompt(
            description=state.get('sketch_description', ''),
            instructions=enhanced_instructions,
            style_hints=diagram_style
        )
        
        try:
            # Use the single configured client
            client = self.client
            if not client:
                raise ValueError("No LLM client available. Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY.")
            
            # Create message
            message = HumanMessage(content=prompt)
            
            # Get response from LLM
            response = await client.ainvoke([message])
            diagram_code = response.content
            
            # Clean the generated code
            clean_code = self._clean_drawio_code(diagram_code)
            
            # Validate Draw.io XML
            is_valid, error_msg = self._validate_drawio_xml(clean_code)
            if not is_valid:
                print(f"Draw.io Generation Agent: XML validation failed - {error_msg}")
                clean_code = self._generate_drawio_fallback(
                    state.get('sketch_description', ''),
                    state.get('notes', '')
                )
            
            # Update state with generated diagram code
            state.update({
                "diagram_code": clean_code
            })
            
            print(f"Draw.io Generation Agent: Draw.io diagram generated successfully for job {state['job_id']}")
            return state
            
        except Exception as e:
            print(f"Draw.io Generation Agent Error: {str(e)}")
            # Return state with fallback Draw.io diagram
            fallback_code = self._generate_drawio_fallback(
                state.get('sketch_description', ''),
                state.get('notes', '')
            )
            state.update({
                "diagram_code": fallback_code
            })
            return state
