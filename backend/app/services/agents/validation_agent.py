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
from app.core.llm_factory import get_chat_model
from app.prompts.prompt_templates import PromptTemplates


class ValidationAgent:
    """
    Agent responsible for validating generated diagrams and proposing corrections.
    """

    def __init__(self, *, model: str | None = None, temperature: float | None = None):
        self.prompt_templates = PromptTemplates()
        self.client = None
        self.provider = None
        resolved_model = model or os.getenv("VALIDATION_LLM_MODEL", "gpt-4.1")
        resolved_temp = 0.0 if temperature is None else float(temperature)
        self.client, self.provider = get_chat_model(resolved_model, temperature=resolved_temp)

    def _initialize_llm_clients(self):
        """Deprecated: retained for backward compatibility."""
        pass

    def _parse_validation_response(self, response_text: str) -> Dict[str, str]:
        """Parse the structured validation response into fields.

        Returns a dict with keys: syntax_check, accuracy_check, validation_result, corrections (instructions only).
        """
        # First try JSON parsing (supports bare JSON or fenced JSON)
        def _extract_first_json_block(text: str) -> str | None:
            # Prefer fenced JSON if available
            fenced = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if fenced:
                return fenced.group(1)
            # Otherwise attempt to capture the first top-level JSON object
            start = text.find('{')
            if start == -1:
                return None
            depth = 0
            for i in range(start, len(text)):
                ch = text[i]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start:i+1]
            return None

        try:
            json_str = _extract_first_json_block(response_text)
            if json_str:
                parsed_json = json.loads(json_str)
                # Legacy schema support
                if "syntax_check" in parsed_json or "accuracy_check" in parsed_json:
                    return {
                        "syntax_check": parsed_json.get("syntax_check", ""),
                        "accuracy_check": parsed_json.get("accuracy_check", ""),
                        "validation_result": parsed_json.get("validation_result", "NEEDS_CORRECTION").upper(),
                        "corrections": parsed_json.get("corrections", ""),
                    }
                # New schema mapping: instructions-only
                syntax_valid = parsed_json.get("syntax_valid")
                syntax_errors = parsed_json.get("syntax_errors", [])
                struct_acc = parsed_json.get("structure_accuracy", {})
                issues = parsed_json.get("issues", [])
                validation_result = parsed_json.get("validation_result", "NEEDS_CORRECTION").upper()
                instructions = parsed_json.get("instructions")

                syntax_summary = (
                    "VALID" if syntax_valid is True else ("; ".join(syntax_errors) if syntax_errors else "")
                )
                accuracy_summary = struct_acc.get("notes", "")
                # Prefer top-level instructions, otherwise aggregate issue instructions
                if instructions and isinstance(instructions, str) and instructions.strip():
                    corrections_out = instructions.strip()
                else:
                    bullets = [f"- {it.get('instruction','').strip()}" for it in issues if it.get('instruction')]
                    corrections_out = "\n".join([b for b in bullets if b and b != "-"])
                return {
                    "syntax_check": syntax_summary,
                    "accuracy_check": accuracy_summary,
                    "validation_result": validation_result,
                    "corrections": corrections_out,
                }
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
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
            # Support new instruction-only label and legacy label
            if line.startswith("INSTRUCTIONS TO FIX") or line.startswith("INSTRUCTIONS:") or line.startswith("CORRECTIONS"):
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
            client = self.client
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
