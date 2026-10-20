"""
Conflict and Contradiction Detector for Classical AI.
Identifies:
1. Fact-level semantic contradictions (e.g., emergency=False but safety_risk=critical).
2. Domain incompatibilities (e.g., category-issue mismatch).
3. Rule conflicts (e.g., competing conclusions produced by different rules).
"""

from typing import Dict, Any, List
from utils.validators import is_valid_category_issue_pair


class ConflictDetector:
    """Detects and documents semantic, domain, and logical conflicts."""

    def __init__(self):
        pass

    def detect_fact_conflicts(self, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyzes input ground facts for semantic contradictions.
        Returns a list of structured conflict records.
        """
        conflicts = []

        category = facts.get("category", "")
        issue_type = facts.get("issue_type", "")
        emergency = facts.get("emergency", False)
        safety_risk = str(facts.get("safety_risk", "")).lower()
        duration_days = facts.get("duration_days")
        frequency = str(facts.get("frequency", "")).lower()
        severity = str(facts.get("severity", "")).lower()

        # Conflict 1: Category vs Issue Type Domain Mismatch
        if category and issue_type and not is_valid_category_issue_pair(category, issue_type):
            conflicts.append({
                "conflict_type": "DOMAIN_INCOMPATIBILITY",
                "description": f"Grievance category '{category}' does not support issue type '{issue_type}'.",
                "conflicting_elements": [f"category={category}", f"issue_type={issue_type}"],
                "resolution": "Decision blocked. Citizen must re-select valid category or issue.",
                "is_blocking": True
            })

        # Conflict 2: Immediate Danger = YES while Severity = LOW (Section 5)
        imm_danger = facts.get("immediate_danger")
        if (imm_danger == "YES" or emergency) and severity == "low":
            conflicts.append({
                "conflict_type": "VALIDATION_CONFLICT",
                "description": "Validation Conflict: Immediate danger is marked YES while the selected severity is LOW. Please review the complaint information.",
                "conflicting_elements": ["immediate_danger=YES", "severity=LOW"],
                "resolution": "Normal AI reasoning STOPPED. Requires revision or Administrative Review.",
                "is_blocking": True
            })

        # Conflict 2: Emergency=False while Safety Risk=Critical
        if emergency is False and safety_risk == "critical":
            conflicts.append({
                "conflict_type": "SEMANTIC_CONTRADICTION",
                "description": "Citizen marked 'emergency=False' but declared 'safety_risk=CRITICAL'.",
                "conflicting_elements": ["emergency=False", "safety_risk=CRITICAL"],
                "resolution": "Conservative Precedence: System elevates priority to CRITICAL based on safety hazard override.",
                "is_blocking": False
            })

        # Conflict 3: Continuous frequency with 0 duration
        if duration_days is not None and int(duration_days) == 0 and frequency == "continuous":
            conflicts.append({
                "conflict_type": "TEMPORAL_CONTRADICTION",
                "description": "Citizen marked duration as 0 days, yet specified frequency as 'CONTINUOUS'.",
                "conflicting_elements": ["duration_days=0", "frequency=CONTINUOUS"],
                "resolution": "Flagged for officer verification. Evaluated as day-of-onset.",
                "is_blocking": False
            })

        # Conflict 4: Low severity but Critical safety risk
        if severity == "low" and safety_risk == "critical":
            conflicts.append({
                "conflict_type": "SEVERITY_SAFETY_DIVERGENCE",
                "description": "Severity marked as LOW while safety risk is CRITICAL.",
                "conflicting_elements": ["severity=LOW", "safety_risk=CRITICAL"],
                "resolution": "Safety override: Safety risk takes precedence over reported severity.",
                "is_blocking": False
            })

        return conflicts
