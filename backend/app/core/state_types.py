"""
Simplified state type definitions for the new 4-agent architecture.
"""

from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict
from dataclasses import dataclass


@dataclass
class DiagramCandidate:
    """A potential diagram solution with metadata."""
    format: str  # "mermaid" or "drawio"
    code: str
    style_approach: str  # "flowchart", "sequence", "network", etc.
    confidence_score: float  # 0.0 to 1.0
    reasoning: str  # Why this approach was chosen


class SketchConversionState(TypedDict):
    """
    Simplified state for the new 4-agent multi-perspective workflow.
    
    Each agent adds exactly one field to build understanding progressively.
    """
    
    # Core inputs
    file_path: str
    user_notes: str
    target_format: str  # "mermaid" or "drawio"
    job_id: str
    
    # Progressive understanding (each agent adds one)
    scene_description: Optional[str]  # Agent 1: Natural language scene description
    structural_analysis: Optional[str]  # Agent 2: Abstract structure and relationships
    diagram_candidates: Optional[List[DiagramCandidate]]  # Agent 3: Multiple diagram options
    final_diagram: Optional[str]  # Agent 4: Selected and refined final diagram
    
    # Metadata
    confidence_score: Optional[float]  # Overall confidence in the result
    processing_path: Optional[List[str]]  # Which agents ran and in what order
    thread_id: Optional[str]  # For LangGraph checkpointing