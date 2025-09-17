"""
Prompt template management for the current SketchFlow pipeline.
"""

from typing import Dict, Any
from string import Template


class PromptTemplates:
    """
    Simplified prompt templates for the current pipeline.
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

    # ===== Describer prompt =====

    def get_describer_prompt(self, user_notes: str) -> str:
        """Describer agent prompt: produce JSON spec then a short narrative.

        The model must output a top-level JSON object first (no preface), matching the schema:
        {
          "diagram_type": "flowchart|sequence|state|class|er|gantt|pie|gitgraph|network|org|custom",
          "orientation": "TD|LR|BT|RL",
          "elements": [
            {"id": "...", "label": "...", "type": "start|process|decision|actor|db|queue|state|class|entity|note|group|swimlane|cloud|other", "group": "group-1?", "style": {"fillColor": "#RRGGBB?", "strokeColor": "#RRGGBB?", "textColor": "#RRGGBB?", "rounded": true, "dashed": false}}
          ],
          "edges": [
            {"source": "id", "target": "id", "label": "?", "style": {"dotted": false, "bold": false}, "direction": "uni|bi"}
          ],
          "groups": [{"id": "...", "label": "...", "type": "group|swimlane", "orientation": "TD|LR|BT|RL"}],
          "notes": "...",
          "colors_used": ["#RRGGBB", "#..."]
        }

        Do not include absolute coordinates. Use orientation and grouping only.
        After the JSON, add a short natural language summary of the scene.
        """
        template = self._get_describer_template()
        return self.format_prompt(template, user_notes=user_notes)
    
    # (Removed legacy multi-candidate and synthesis prompts)
    
    # ===== Legacy 4-agent templates removed =====

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

    def get_mermaid_generation_prompt_from_spec(self, diagram_spec: dict[str, object]) -> str:
        """Prompt for Mermaid generator from structured spec (code-only)."""
        template = """You translate a structured diagram specification into valid Mermaid code.

SPEC (JSON):
$spec

REQUIREMENTS:
- Use the specified diagram_type and orientation when applicable
- Map element types to appropriate Mermaid shapes and styling
- Use subgraphs for groups or swimlanes
- Apply colors using `style id fill:#hex,stroke:#hex,color:#hex` where provided
- Output Mermaid code only (no markdown fences, no commentary)

Return only the Mermaid diagram code."""
        import json
        spec_str = json.dumps(diagram_spec, ensure_ascii=False)
        return self.format_prompt(template, spec=spec_str)

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

    def get_drawio_generation_prompt_from_spec(self, diagram_spec: dict[str, object]) -> str:
        """Prompt for Draw.io generator from structured spec (valid <mxfile> XML only)."""
        template = """You translate a structured diagram specification into valid Draw.io (diagrams.net) XML.

SPEC (JSON):
$spec

REQUIREMENTS:
- Output valid XML starting with <mxfile>, including <diagram> and <mxGraphModel>
- Use auto-layout friendly geometry; avoid detailed absolute positioning
- Encode colors/styles via `style` (fillColor, strokeColor, fontColor, rounded)
- Use orthogonal connector style for edges
- Output XML only (no markdown fences, no commentary)

Return only the Draw.io XML starting with <mxfile>."""
        import json
        spec_str = json.dumps(diagram_spec, ensure_ascii=False)
        return self.format_prompt(template, spec=spec_str)

    def _get_describer_template(self) -> str:
        return """You are a precise vision describer for hand-drawn or sketched diagrams.

GOAL:
1) Output a JSON object that matches the required schema exactly (no preface, no markdown)
2) Then output a short human summary paragraph

Rules:
- Use orientation and grouping; do not infer absolute coordinates
- If unsure about a field, use a sensible default or \"unknown\"
- Incorporate user notes as hints but do not hallucinate missing structure

USER NOTES (optional):
$user_notes

Now analyze the image and provide the JSON spec followed by a short narrative."""
