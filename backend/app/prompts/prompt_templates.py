"""
Centralized prompt template management system for SketchFlow AI agents.
"""

from typing import Dict, Any
from string import Template


class PromptTemplates:
    """
    Centralized prompt template management with variable substitution.
    """
    
    def __init__(self):
        pass
    
    def format_prompt(self, template: str, **kwargs) -> str:
        """
        Format a prompt template with provided variables.
        
        Args:
            template: The template string with $variable placeholders
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted prompt string
        """
        return Template(template).safe_substitute(**kwargs)
    
    def get_vision_analysis_prompt(self, notes: str = "", format_type: str = "mermaid") -> str:
        """Get the vision analysis prompt with variables."""
        template = self._get_vision_template()
        return self.format_prompt(
            template,
            user_notes=notes,
            target_format=format_type
        )
    
    def get_diagram_generation_prompt(self, description: str, instructions: str, format_type: str) -> str:
        """Get the diagram generation prompt with variables."""
        template = self._get_generation_template()
        return self.format_prompt(
            template,
            sketch_description=description,
            generation_instructions=instructions,
            target_format=format_type
        )
    
    def get_mermaid_generation_prompt(self, description: str, instructions: str, suggested_type: str = "flowchart TD") -> str:
        """Get the Mermaid-specific generation prompt with variables."""
        template = self._get_mermaid_generation_template()
        return self.format_prompt(
            template,
            sketch_description=description,
            generation_instructions=instructions,
            suggested_diagram_type=suggested_type
        )
    
    def get_drawio_generation_prompt(self, description: str, instructions: str, style_hints: dict) -> str:
        """Get the Draw.io-specific generation prompt with variables."""
        template = self._get_drawio_generation_template()
        return self.format_prompt(
            template,
            sketch_description=description,
            generation_instructions=instructions,
            style_hints=str(style_hints),
            default_shape=style_hints.get('default_shape', 'rounded=1;whiteSpace=wrap;html=1;')
        )
    
    def get_validation_prompt(self, diagram_code: str, description: str, format_type: str) -> str:
        """Get the validation prompt with variables."""
        template = self._get_validation_template()
        return self.format_prompt(
            template,
            diagram_code=diagram_code,
            sketch_description=description,
            target_format=format_type
        )
    
    def _get_vision_template(self) -> str:
        """Vision analysis prompt template."""
        return """You are an expert at analyzing hand-drawn sketches and diagrams. Your task is to:

1. Carefully analyze the provided sketch image
2. Identify all visual elements (shapes, connections, text, arrows, etc.)
3. Understand the overall structure and relationships
4. Create detailed instructions for generating a $target_format diagram

User provided notes: "$user_notes"

Please provide your analysis in this exact format:

SKETCH DESCRIPTION:
[Detailed description of what you see in the sketch - include all shapes, text, connections, layout]

IDENTIFIED ELEMENTS:
[List all distinct elements: boxes, circles, arrows, text labels, etc.]

STRUCTURE ANALYSIS:
[Describe the overall flow, hierarchy, or organization of the elements]

GENERATION INSTRUCTIONS:
[Specific, detailed instructions for creating a $target_format diagram that accurately represents this sketch]

Be thorough and precise - your analysis will be used to generate the final diagram."""

    def _get_generation_template(self) -> str:
        """Diagram generation prompt template."""
        return """You are an expert at creating $target_format diagrams. Based on the sketch analysis provided, generate the appropriate diagram code.

SKETCH DESCRIPTION:
$sketch_description

GENERATION INSTRUCTIONS:
$generation_instructions

TARGET FORMAT: $target_format

Generate valid $target_format code that accurately represents the analyzed sketch. 

For Mermaid diagrams:
- Use appropriate diagram type (flowchart, sequence, etc.)
- Include proper node IDs and connections
- Add labels and styling as needed

For Draw.io diagrams:
- Generate valid XML format
- Include proper mxCell elements
- Set appropriate coordinates and styling

IMPORTANT: Only return the diagram code, no explanations or markdown formatting."""

    def _get_validation_template(self) -> str:
        """Validation prompt template.""" 
        return """You are an expert at validating and correcting $target_format diagrams. Your task is to:

1. Analyze the generated diagram code for syntax errors
2. Check if it accurately represents the original sketch description
3. Suggest improvements or corrections if needed

ORIGINAL SKETCH DESCRIPTION:
$sketch_description

GENERATED DIAGRAM CODE:
$diagram_code

TARGET FORMAT: $target_format

Please provide your validation in this exact format:

SYNTAX CHECK:
[Check for syntax errors, invalid elements, or formatting issues]

ACCURACY CHECK:
[Verify if the diagram accurately represents the original sketch]

VALIDATION RESULT:
[Either "PASSED" if no issues found, or "NEEDS_CORRECTION" if issues exist]

CORRECTIONS (if needed):
[Provide corrected diagram code if NEEDS_CORRECTION, otherwise "None required"]

Be thorough in your validation - accuracy and proper syntax are critical."""

    def _get_mermaid_generation_template(self) -> str:
        """Mermaid-specific generation prompt template."""
        return """You are an expert at creating Mermaid diagrams. Based on the sketch analysis provided, generate accurate Mermaid diagram code.

SKETCH DESCRIPTION:
$sketch_description

GENERATION INSTRUCTIONS:
$generation_instructions

SUGGESTED DIAGRAM TYPE: $suggested_diagram_type

Create a valid Mermaid diagram that accurately represents the analyzed sketch. Follow these Mermaid-specific guidelines:

**Diagram Types:**
- flowchart TD/LR: For process flows, decision trees, workflows
- sequenceDiagram: For interactions between actors/systems
- classDiagram: For class relationships and structure
- stateDiagram-v2: For state machines and transitions
- erDiagram: For entity relationships
- gantt: For project timelines
- pie: For data visualization

**Mermaid Syntax Rules:**
- Use clear, descriptive node IDs (A, B, C... or meaningful names)
- Include proper connections with arrows (-->, ---, ->>)
- Add labels to connections when needed
- Use appropriate shapes for different node types
- Include styling when it enhances clarity

**Best Practices:**
- Start with the suggested diagram type: $suggested_diagram_type
- Use meaningful node labels that reflect the sketch content
- Ensure proper flow direction and logical connections
- Include decision points as diamond shapes when applicable
- Add subgraphs for grouping related elements when appropriate

IMPORTANT: Return ONLY the Mermaid diagram code, no explanations or markdown formatting."""

    def _get_drawio_generation_template(self) -> str:
        """Draw.io-specific generation prompt template."""
        return """You are an expert at creating Draw.io (diagrams.net) XML diagrams. Based on the sketch analysis provided, generate accurate Draw.io XML code.

SKETCH DESCRIPTION:
$sketch_description

GENERATION INSTRUCTIONS:
$generation_instructions

STYLE HINTS: $style_hints
DEFAULT SHAPE STYLE: $default_shape

Create a valid Draw.io XML diagram that accurately represents the analyzed sketch. Follow these Draw.io-specific guidelines:

**XML Structure Requirements:**
- Root element must be <mxfile host="app.diagrams.net">
- Include <diagram name="Page-1"> element
- Use <mxGraphModel> with proper dimensions (dx="800" dy="600" grid="1" gridSize="10")
- Include root cells with id="0" and id="1"
- Use proper mxCell elements for all shapes and connections

**Shape Guidelines:**
- Rectangle: style="rounded=0;whiteSpace=wrap;html=1;"
- Rounded Rectangle: style="rounded=1;whiteSpace=wrap;html=1;"
- Ellipse/Circle: style="ellipse;whiteSpace=wrap;html=1;"
- Diamond (Decision): style="rhombus;whiteSpace=wrap;html=1;"
- Process: Use default shape style: $default_shape

**Positioning:**
- Use logical coordinates with proper spacing (minimum 40-60 units between elements)
- Standard shape sizes: width="120" height="60" for rectangles
- Adjust sizes based on text content length
- Center elements properly within the canvas

**Connections:**
- Use edge elements with source and target attributes
- Style: style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
- Add labels to edges when specified in the sketch

**Best Practices:**
- Use vertex="1" for shapes and edge="1" for connections
- Include parent="1" for all elements
- Use meaningful values for shape labels
- Ensure proper XML formatting and escaping

IMPORTANT: Return ONLY the Draw.io XML code, no explanations or markdown formatting."""