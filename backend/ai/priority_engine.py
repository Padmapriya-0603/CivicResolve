"""
Priority Reasoning and Rule Conflict Resolution Engine.
Resolves competing priority inferences through explicit formal precedence:
CRITICAL (4) > HIGH (3) > MEDIUM (2) > LOW (1).
Preserves complete conflict records and resolution rationale for the audit trace.
"""

from typing import List, Dict, Any, Tuple, Optional
from ai.knowledge_base import PRIORITY_PRECEDENCE


class PriorityEngine:
    """Manages priority determination, candidate collection, and precedence arbitration."""

    def __init__(self):
        self.precedence = PRIORITY_PRECEDENCE

    def resolve_priority(self, candidate_priorities: List[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Takes candidate conclusions from all fired priority rules:
        Each candidate: {
            "rule_id": str,
            "rule_name": str,
            "priority": str,
            "description": str
        }
        Returns:
            (selected_priority, conflict_record)
        """
        if not candidate_priorities:
            # Baseline deterministic fallback when no priority rule matched
            return "LOW", None

        if len(candidate_priorities) == 1:
            return candidate_priorities[0]["priority"], None

        # Multiple rules fired -> Rule Conflict!
        # Check if they produced different priority conclusions
        unique_priorities = {c["priority"] for c in candidate_priorities}

        if len(unique_priorities) == 1:
            # All fired rules agreed on the same priority
            return candidate_priorities[0]["priority"], None

        # True rule conflict: Sort candidates by explicit precedence
        sorted_candidates = sorted(
            candidate_priorities,
            key=lambda c: self.precedence.get(c["priority"].upper(), 0),
            reverse=True
        )

        winning_candidate = sorted_candidates[0]
        selected_priority = winning_candidate["priority"]

        # Build detailed conflict record
        conflict_record = {
            "conflict_type": "RULE_CONCLUSION_CONFLICT",
            "description": f"Multiple priority rules fired with differing conclusions: {', '.join([f'{c['rule_id']} ({c['priority']})' for c in candidate_priorities])}.",
            "conflicting_elements": [
                f"{c['rule_id']} ({c['rule_name']}): inferred priority '{c['priority']}'"
                for c in candidate_priorities
            ],
            "precedence_hierarchy": "CRITICAL > HIGH > MEDIUM > LOW",
            "resolution": f"Applied precedence hierarchy. Rule {winning_candidate['rule_id']} ('{winning_candidate['rule_name']}') overrides other rules with higher precedence ({selected_priority}).",
            "is_blocking": False
        }

        return selected_priority, conflict_record
