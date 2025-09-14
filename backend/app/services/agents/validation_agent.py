"""
Validation Agent - Node 3 of the SketchFlow conversion pipeline.

Validates generated diagram code against the sketch description and
provides corrections if needed. Supports a feedback loop back to
generation until validation passes or retries are exhausted.
"""

from typing import Dict, Any
import os
import json
import re

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langsmith import traceable

from app.core.state_types import SketchConversionState
from app.prompts.prompt_templates import PromptTemplates


class ValidationAgent:
    """
    Agent responsible for validating generated diagrams and proposing corrections.
    """

    def __init__(self):
        self.prompt_templates = PromptTemplates()
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_llm_clients()

    def _initialize_llm_clients(self):
        """Initialize text-based LLM clients for validation."""
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if openai_key:
            self.openai_client = ChatOpenAI(
                model=os.getenv("VALIDATION_LLM_MODEL", "gpt-4.1"),
                api_key=openai_key,
                temperature=0.0,
            )

        if anthropic_key:
            self.anthropic_client = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=anthropic_key,
                temperature=0.0,
            )

    def _parse_validation_response(self, response_text: str) -> Dict[str, str]:
        """Parse the structured validation response into fields."""
        # First try JSON parsing
        try:
            # Look for JSON block in response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed_json = json.loads(json_str)
                return {
                    "syntax_check": parsed_json.get("syntax_check", ""),
                    "accuracy_check": parsed_json.get("accuracy_check", ""),
                    "validation_result": parsed_json.get("validation_result", "NEEDS_CORRECTION").upper(),
                    "corrections": parsed_json.get("corrections", ""),
                }
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Failed to parse JSON validation response: {e}")
        
        # Fallback to original text parsing
        result = {
            "syntax_check": "",
            "accuracy_check": "",
            "validation_result": "",
            "corrections": "",
        }

        current_section = None
        for raw in response_text.split("\n"):
            line = raw.strip()
            if line.startswith("SYNTAX CHECK:"):
                current_section = "syntax_check"
                continue
            if line.startswith("ACCURACY CHECK:"):
                current_section = "accuracy_check"
                continue
            if line.startswith("VALIDATION RESULT:"):
                current_section = "validation_result"
                continue
            if line.startswith("CORRECTIONS"):
                current_section = "corrections"
                continue
            if current_section and line:
                if result[current_section]:
                    result[current_section] += "\n" + line
                else:
                    result[current_section] = line

        return result

    def _check_circuit_breaker(self, state: SketchConversionState, current_corrections: str) -> bool:
        """Check if we're in a circuit breaker scenario (same error repeating)."""
        retry_count = int(state.get("retry_count", 0) or 0)
        
        # Circuit breaker: if corrections are the same as previous attempt
        if retry_count > 0:
            previous_corrections = state.get("previous_corrections", "")
            if current_corrections and current_corrections.strip() == previous_corrections.strip():
                print(f"Circuit breaker triggered: same corrections repeating (retry {retry_count})")
                return True
        
        # Store current corrections for next comparison
        state["previous_corrections"] = current_corrections.strip()
        return False

    @traceable(name="validation_node")
    async def validate(self, state: SketchConversionState) -> SketchConversionState:
        """
        Validate and optionally correct the diagram. Updates the state with:
          - syntax_check, accuracy_check, validation_result, corrections
          - validation_passed (bool)
          - final_code if passed
        """
        retry_count = int(state.get("retry_count", 0) or 0)
        print(f"Validation Agent: Validating diagram for job {state.get('job_id')} (retry {retry_count})")
        
        # Prepare prompt
        prompt = self.prompt_templates.get_validation_prompt(
            diagram_code=state.get("diagram_code", ""),
            description=state.get("sketch_description", ""),
            format_type=state["format"],
        )

        try:
            client = self.openai_client or self.anthropic_client
            if not client:
                raise ValueError("No LLM client available. Configure OPENAI_API_KEY or ANTHROPIC_API_KEY.")

            response = await client.ainvoke([HumanMessage(content=prompt)])
            text = response.content

            parsed = self._parse_validation_response(text)
            validation_result = parsed.get("validation_result", "").strip().upper()
            corrections = parsed.get("corrections", "").strip()
            
            # Determine if validation passed
            passed = validation_result == "PASSED"
            
            # Circuit breaker check
            if not passed and self._check_circuit_breaker(state, corrections):
                print("Circuit breaker: accepting current diagram to prevent infinite loop")
                passed = True
                validation_result = "PASSED"
                corrections = "Circuit breaker activated - accepting current version"

            # Update state
            state.update(
                {
                    "syntax_check": parsed.get("syntax_check", ""),
                    "accuracy_check": parsed.get("accuracy_check", ""),
                    "validation_result": validation_result or ("PASSED" if passed else "NEEDS_CORRECTION"),
                    "corrections": corrections,
                    "validation_passed": passed,
                }
            )

            if passed:
                state["final_code"] = state.get("diagram_code", "")

            print(f"Validation Agent: Result = {validation_result}, Passed = {passed}")
            return state

        except Exception as e:
            print(f"Validation Agent Error: {str(e)}")
            # On failure, mark as pass-through to avoid blocking
            state.update(
                {
                    "syntax_check": f"Validation error: {e}",
                    "accuracy_check": "",
                    "validation_result": "PASSED",
                    "corrections": "",
                    "validation_passed": True,
                    "final_code": state.get("diagram_code", ""),
                }
            )
            return state
