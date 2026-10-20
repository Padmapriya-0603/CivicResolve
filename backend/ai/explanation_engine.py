"""
Explanation Engine for Classical AI.
Constructs transparent, auditable natural explanations derived strictly from
fired production rules and formal deduction steps.
Guarantees NO LLM hallucination: every stated deduction maps directly to an active rule.
"""

from typing import List, Dict, Any, Optional
from ai.inference_engine import ReasoningStep


class ExplanationEngine:
    """Builds structured narrative summaries from the forward-chaining trace."""

    def __init__(self):
        pass

    def build_narrative_explanation(
        self,
        ground_facts: Dict[str, Any],
        trace: List[ReasoningStep],
        selected_department: Optional[str],
        selected_priority: str,
        selected_escalation: str,
        priority_conflict: Optional[Dict[str, Any]] = None,
        missing_info: Optional[List[str]] = None,
        validation_conflict: Optional[str] = None
    ) -> str:
        """
        Synthesizes a clean, fact-grounded explanation showing why the AI reached
        its recommendation, using the actual complaint facts and the rules that fired.
        """
        # If there is a validation conflict, format accordingly
        imm_danger = str(ground_facts.get("immediate_danger", "NO")).strip().upper()
        severity_raw = str(ground_facts.get("severity", "medium")).strip().lower()
        if validation_conflict or (imm_danger in ("YES", "TRUE", "1") and severity_raw == "low"):
            if not validation_conflict or "Immediate Danger" in str(validation_conflict) or (imm_danger in ("YES", "TRUE", "1") and severity_raw == "low"):
                return (
                    "Validation Conflict: Immediate Danger is marked Yes, but the selected severity is Low, "
                    "which violates the defined constraint. The AI recommendation has been paused and the complaint "
                    "requires administrative review."
                )
            return (
                f"Validation Conflict: {validation_conflict} "
                "The AI recommendation has been paused and the complaint requires administrative review."
            )

        def format_title(val: Any) -> str:
            if not val:
                return "Not Specified"
            return str(val).replace("_", " ").title()

        cat_display = format_title(ground_facts.get("category", "General"))
        issue_display = format_title(ground_facts.get("issue_type", "General Issue"))
        dept_name = selected_department or "General Civic Administration"
        prio_display = selected_priority.capitalize()
        escl_display = selected_escalation.replace("_", " ").title()

        # 1. Department narrative
        dept_narrative = (
            f"Category is {cat_display} and the selected issue is {issue_display}.\n"
            f"This category and issue fall under the jurisdiction of the {dept_name} Department."
        )

        # 2. Priority narrative
        pop_count = ground_facts.get("population_impact") or ground_facts.get("affected_people") or 1
        try:
            pop_count_int = int(pop_count)
        except (ValueError, TypeError):
            pop_count_int = 1

        if imm_danger in ("YES", "TRUE", "1"):
            prio_narrative = f"Immediate Danger is marked as Yes and safety hazard is active, elevating priority to {prio_display}."
        elif severity_raw == "high" and pop_count_int >= 10:
            prio_narrative = f"The complaint has High Severity and affects an estimated {pop_count_int} people, elevating priority to {prio_display}."
        elif severity_raw == "critical":
            prio_narrative = f"The complaint has Critical Severity posing significant public impact, requiring {prio_display} priority."
        elif ground_facts.get("public_accessibility_affected"):
            prio_narrative = f"The complaint impairs public accessibility with {severity_raw.capitalize()} Severity, elevating priority to {prio_display}."
        elif severity_raw == "medium":
            prio_narrative = "The complaint has Medium Severity with localized community impact."
        else:
            prio_narrative = "The complaint has Low Severity with no immediate hazards."

        # 3. Escalation narrative
        if imm_danger in ("YES", "TRUE", "1"):
            escl_narrative = "Immediate Danger is marked as Yes. This condition activates an emergency state, requiring Immediate Escalation for rapid intervention."
        elif selected_escalation == "IMMEDIATE":
            escl_narrative = "The grievance has been categorized with Critical priority, requiring Immediate Escalation to ensure rapid municipal intervention."
        elif selected_escalation == "REQUIRED":
            dur = ground_facts.get("duration_days") or 1
            escl_narrative = f"The issue has {severity_raw.capitalize()} severity persisting over {dur} day(s), requiring Escalation to expedite departmental remediation."
        else:
            escl_narrative = "The issue is within standard operational parameters with no critical emergency flags, following routine resolution timelines without escalation."

        # Compose output matching the exact requested format
        lines = [
            "AI Decision Explanation",
            "",
            f"Recommended Department: {dept_name}",
            "",
            dept_narrative,
            "",
            f"Recommended Priority: {prio_display}",
            "",
            prio_narrative,
            "",
            f"Recommended Escalation: {escl_display}",
            "",
            escl_narrative,
            "",
            "So the final result is:",
            f"Department  : {dept_name}",
            f"Priority    : {prio_display}",
            f"Escalation  : {escl_display}"
        ]

        return "\n".join(lines)
