"""
State type definitions for LangGraph agents.
"""

from typing import Optional, Union, List, Dict
from typing_extensions import TypedDict


class SketchConversionState(TypedDict, total=False):
    """
    State for the sketch-to-diagram conversion workflow (3-agent pipeline).

    Notes:
    - Uses `target_format` and `user_notes` (replacing legacy `format`/`notes`).
    - Tracks `attempt_count` (0-based) for generator attempts.
    - Carries validation details (`validation_passed`, `validation_skipped`, `issues`).
    """

    # Required inputs
    file_path: str
    target_format: str  # "mermaid", "drawio", or "uml"
    user_notes: str
    job_id: str

    # Describer outputs
    diagram_spec: Dict[str, object]
    scene_narrative: str

    # Normalized inputs for generators (back-compat mapping)
    sketch_description: str
    generation_instructions: str

    # Generation outputs
    diagram_code: str
    generation_error: str

    # Validation outputs
    validation_passed: bool
    validation_skipped: Union[bool, str]
    issues: List[str]
    corrections: str

    # Final output
    final_code: str

    # (Deprecated) Lucidchart publish outputs were removed

    # Control/metadata
    attempt_count: int  # 0-based number of generation attempts performed
    thread_id: str
    processing_path: List[str]
    processing_time: str
    agents_used: List[str]
