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