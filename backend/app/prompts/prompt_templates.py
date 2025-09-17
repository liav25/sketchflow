"""
Simplified prompt template management for the new 4-agent architecture.
"""

from typing import Dict, Any
from string import Template


class PromptTemplates:
    """
    Simplified prompt templates for the new multi-perspective agent system.
    Each template is focused, short, and has a single clear purpose.
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

    # ===== NEW 4-AGENT ARCHITECTURE PROMPTS =====
    
    def get_scene_understanding_prompt(self, user_notes: str) -> str:
        """Agent 1: Scene Understanding - Natural language description only."""
        template = self._get_scene_understanding_template()
        return self.format_prompt(template, user_notes=user_notes)
    
    def get_structure_analysis_prompt(self, scene_description: str, user_notes: str) -> str:
        """Agent 2: Structure Analysis - Abstract patterns and relationships."""
        template = self._get_structure_analysis_template()
        return self.format_prompt(template, scene_description=scene_description, user_notes=user_notes)
    
    def get_multi_format_generation_prompt(
        self, scene_description: str, structural_analysis: str, target_format: str
    ) -> str:
        """Agent 3: Multi-Format Generation - Multiple diagram candidates."""
        template = self._get_multi_format_generation_template()
        return self.format_prompt(
            template,
            scene_description=scene_description,
            structural_analysis=structural_analysis,
            target_format=target_format
        )
    
    def get_synthesis_prompt(
        self, 
        scene_description: str, 
        structural_analysis: str, 
        candidates: str, 
        target_format: str
    ) -> str:
        """Agent 4: Synthesis - Select and refine the best candidate."""
        template = self._get_synthesis_template()
        return self.format_prompt(
            template,
            scene_description=scene_description,
            structural_analysis=structural_analysis,
            candidates=candidates,
            target_format=target_format
        )
    
    # ===== SIMPLIFIED PROMPT TEMPLATES =====
    
    def _get_scene_understanding_template(self) -> str:
        """Agent 1: Simple scene understanding prompt (30 lines vs old 150+)."""
        return """You are analyzing a hand-drawn sketch or diagram. 

Describe what you see in natural language, as if explaining to a colleague:

- What type of diagram is this? (flowchart, network, org chart, sequence, etc.)
- How many main elements are there?
- How are they connected or related?
- What seems to be the main flow or purpose?
- Any text labels you can read?
- Overall layout (left-to-right, top-to-bottom, circular, etc.)?

Keep it conversational and natural. Don't try to be precise about coordinates or formatting.
Focus on what you actually see, not what you think it should be.

User notes: "$user_notes"

Respond with a clear, natural description of the scene."""

    def _get_structure_analysis_template(self) -> str:
        """Agent 2: Abstract structure analysis prompt."""
        return """Based on this scene description and user notes, identify the abstract structure:

SCENE DESCRIPTION:
$scene_description

USER NOTES:
$user_notes

Analyze and output:

1. **Element Types**: What kinds of elements are there? (start, process, decision, end, data, etc.)

2. **Connection Patterns**: How do elements connect? (linear sequence, branching, loops, parallel paths, etc.)

3. **Suggested Diagram Type**: What diagram type best fits this structure? (flowchart, sequence diagram, network diagram, etc.)

4. **Key Relationships**: What are the most important connections or groupings?

5. **Flow Direction**: What's the primary direction of information/process flow?

Be concise and focus on the logical structure, not visual details.
Think about the underlying relationships and patterns."""

    def _get_multi_format_generation_template(self) -> str:
        """Agent 3: Generate multiple diagram candidates."""
        return """You are an expert diagram generator. Create 2-3 different approaches for representing this structure.

SCENE DESCRIPTION:
$scene_description

STRUCTURAL ANALYSIS:
$structural_analysis

TARGET FORMAT: $target_format

Generate 2-3 different $target_format diagrams that represent this structure. For each approach:

1. **Approach 1**: [Brief description of this approach]
[Diagram code here]

2. **Approach 2**: [Brief description of this approach]  
[Diagram code here]

3. **Approach 3** (if applicable): [Brief description of this approach]
[Diagram code here]

For Mermaid: Use appropriate diagram types (flowchart TD/LR, sequenceDiagram, etc.)
For Draw.io: Generate valid XML starting with <mxfile>

Keep each approach distinct - try different layouts, styles, or emphasis.
Include only valid diagram code with no markdown or explanations in the code blocks."""

    def _get_synthesis_template(self) -> str:
        """Agent 4: Select and refine the best approach."""
        return """You are an expert at selecting and refining diagram solutions.

SCENE DESCRIPTION:
$scene_description

STRUCTURAL ANALYSIS:
$structural_analysis

CANDIDATE APPROACHES:
$candidates

TARGET FORMAT: $target_format

Your task:
1. Review all the candidate approaches
2. Select the one that best represents the original sketch
3. Refine and polish it for final output

Consider:
- Accuracy to the original sketch
- Clarity and readability  
- Appropriate use of the target format
- Completeness of information

Output the final refined $target_format diagram code only.
No explanations, no markdown, just the polished diagram code."""

    # ===== FORMAT-SPECIFIC GENERATION PROMPTS =====

    def get_mermaid_generation_prompt(self, description: str, instructions: str, suggested_type: str) -> str:
        """Prompt for Mermaid generation agent (code-only output)."""
        template = """You generate clean, valid Mermaid diagrams.

SKETCH DESCRIPTION:
$description

ADDITIONAL INSTRUCTIONS (optional):
$instructions

REQUIREMENTS:
- Use this diagram type by default unless clearly inappropriate: $suggested_type
- Output Mermaid code only (no markdown fences, no commentary)
- Prefer readable identifiers and concise labels
- Ensure syntactic correctness for Mermaid renderers

Return only the Mermaid diagram code."""
        return self.format_prompt(template, description=description, instructions=instructions, suggested_type=suggested_type)

    def get_drawio_generation_prompt(self, description: str, instructions: str, style_hints: dict[str, object]) -> str:
        """Prompt for Draw.io generation agent (valid <mxfile> XML only)."""
        # Extract style hints with conservative defaults
        style = (style_hints or {}).get("style", "flowchart")
        default_shape = (style_hints or {}).get("default_shape", "rounded=1;whiteSpace=wrap;html=1;")
        connector_style = (style_hints or {}).get("connector_style", "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;")

        template = """You generate valid Draw.io XML diagrams (diagrams.net).

SKETCH DESCRIPTION:
$description

ADDITIONAL INSTRUCTIONS (optional):
$instructions

STYLE HINTS:
- Overall style: $style
- Default vertex style: $default_shape
- Default connector style: $connector_style

REQUIREMENTS:
- Output valid XML starting with <mxfile> and including <diagram> and <mxGraphModel>
- Include at least one vertex and appropriate edges
- Do not include markdown fences or explanations
- Prefer simple geometry and positions; keep readable labels

Return only the Draw.io XML starting with <mxfile>."""
        return self.format_prompt(
            template,
            description=description,
            instructions=instructions,
            style=str(style),
            default_shape=str(default_shape),
            connector_style=str(connector_style),
        )
