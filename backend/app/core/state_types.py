"""
State type definitions for LangGraph agents.
"""

from typing import Optional
from typing_extensions import TypedDict


class SketchConversionState(TypedDict):
    """
    State for the sketch-to-diagram conversion workflow.
    
    This state is passed between all nodes in the LangGraph workflow.
    """
    
    # Input parameters
    file_path: str
    format: str  # "mermaid" or "drawio" 
    notes: str
    job_id: str
    
    # Vision Analysis Agent outputs
    sketch_description: Optional[str]
    identified_elements: Optional[str]
    structure_analysis: Optional[str] 
    generation_instructions: Optional[str]
    
    # Diagram Generation Agent outputs
    diagram_code: Optional[str]
    
    # Validation Agent outputs
    syntax_check: Optional[str]
    accuracy_check: Optional[str]
    validation_result: Optional[str]  # "PASSED" or "NEEDS_CORRECTION"
    corrections: Optional[str]
    validation_passed: Optional[bool]
    
    # Final outputs
    final_code: Optional[str]
    
    # Metadata
    retry_count: Optional[int]
    processing_time: Optional[str]
    agents_used: Optional[list]