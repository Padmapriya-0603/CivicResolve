"""
Constraint Satisfaction and Input Validation utilities for Public Grievance AI.
Implements domain integrity constraints, category-issue taxonomy validation,
and semantic contradiction detection.
"""

from typing import Dict, List, Optional, Tuple, Any

# Valid Category-to-Issue Type mapping (Knowledge Base Taxonomy & CSP Domain)
CATEGORY_ISSUE_MAP: Dict[str, List[str]] = {
    "Infrastructure": [
        "Damaged Public Property",
        "Broken Facility",
        "Structural Damage"
    ],
    "Public Lighting": [
        "Streetlight Not Working",
        "Streetlight Damaged",
        "Multiple Streetlights Not Working"
    ],
    "Sanitation": [
        "Garbage Not Collected",
        "Illegal Dumping",
        "Public Area Cleanliness"
    ],
    "Water Supply": [
        "No Water Supply",
        "Water Leakage",
        "Pipeline Leakage",
        "Contaminated Supply",
        "Low Water Pressure"
    ],
    "Roads": [
        "Pothole",
        "Damaged Road",
        "Blocked Road",
        "Missing Road Sign"
    ],
    "Drainage": [
        "Drain Blockage",
        "Overflow",
        "Damaged Drain"
    ],
    "Public Transport": [
        "Bus Stop Damaged",
        "Route Disruption",
        "Unsafe Transit Stop"
    ],
    "Traffic Signals": [
        "Signal Not Working",
        "Signal Timer Fault",
        "Damaged Signal Post"
    ],
    "Public Facilities": [
        "Park Bench Broken",
        "Public Toilet Unusable",
        "Playground Equipment Damaged"
    ],
    "Waste Management": [
        "Hazardous Waste Dumped",
        "Compost Facility Overflow",
        "Debris Uncollected"
    ],
    "Electricity Infrastructure": [
        "Exposed Electrical Wire",
        "Transformer Sparking",
        "Fallen Power Pole"
    ],
    "Other": [
        "General Civic Issue",
        "Uncategorized Hazard"
    ]
}

# Category Aliases for common citizen inputs
CATEGORY_ALIASES: Dict[str, str] = {
    "water": "Water Supply",
    "lighting": "Public Lighting",
    "electricity": "Electricity Infrastructure",
    "traffic": "Traffic Signals",
    "transport": "Public Transport",
    "waste": "Waste Management"
}

# Standardized normalization helpers
def normalize_key(val: str) -> str:
    return str(val).strip().lower().replace(" ", "_")


def resolve_category(cat: str) -> Optional[str]:
    if not cat:
        return None
    raw = str(cat).strip().lower()
    norm = normalize_key(raw)
    if norm in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[norm]
    for k in CATEGORY_ISSUE_MAP.keys():
        if k.lower() == raw or normalize_key(k) == norm:
            return k
    return None


def is_valid_category_issue_pair(category: str, issue_type: str) -> bool:
    """Verifies that the given issue type belongs to the category's domain in the CSP."""
    matched_cat = resolve_category(category)
    if not matched_cat:
        return False

    valid_issues = CATEGORY_ISSUE_MAP[matched_cat]
    for issue in valid_issues:
        if issue.lower() == str(issue_type).strip().lower() or normalize_key(issue) == normalize_key(str(issue_type)):
            return True

    return False


def validate_complaint_constraints(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """
    Performs full Constraint Satisfaction Problem (CSP) verification:
    - Domain constraints: Category <-> Issue Type compatibility.
    - Value bounds: duration_days >= 0, affected_people >= 0.
    - Enum domain memberships.
    - Semantic contradiction checks (warnings/conflicts).

    Returns:
        (is_valid, violations_list, warnings_list)
    """
    violations = []
    warnings = []

    category = data.get("category", "")
    issue_type = data.get("issue_type", "")

    # 1. CSP Constraint: Category must be registered
    cat_names = list(CATEGORY_ISSUE_MAP.keys())
    matched_cat = resolve_category(str(category))
    if not matched_cat:
        violations.append(f"Invalid category '{category}'. Permitted categories: {', '.join(cat_names)}.")
    else:
        # 2. CSP Constraint: Issue type must belong to category domain
        if not is_valid_category_issue_pair(matched_cat, issue_type):
            valid_for_cat = CATEGORY_ISSUE_MAP.get(matched_cat, [])
            violations.append(
                f"Constraint Violation: Incompatible category/issue combination! "
                f"Issue '{issue_type}' is not valid for category '{category}'. "
                f"Allowed issue types for '{category}' are: {', '.join(valid_for_cat)}."
            )

    # 3. Numeric Bounds
    duration = data.get("duration_days")
    if duration is not None:
        try:
            d_val = int(duration)
            if d_val < 0:
                violations.append("Constraint Violation: Duration in days cannot be negative.")
        except (ValueError, TypeError):
            violations.append("Duration in days must be an integer.")

    affected = data.get("affected_people")
    if affected is not None:
        try:
            a_val = int(affected)
            if a_val < 0:
                violations.append("Constraint Violation: Number of affected people cannot be negative.")
        except (ValueError, TypeError):
            violations.append("Affected people count must be an integer.")

    # 4. Severity Enum Domain
    severity = str(data.get("severity", "")).upper()
    valid_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    if severity and severity not in valid_severities:
        violations.append(f"Invalid severity '{severity}'. Must be in {valid_severities}.")

    # 5. Safety Risk Enum Domain
    safety_risk = str(data.get("safety_risk", "")).upper()
    valid_risks = {"NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
    if safety_risk and safety_risk not in valid_risks:
        violations.append(f"Invalid safety risk '{safety_risk}'. Must be in {valid_risks}.")

    # 6. Frequency Enum Domain
    frequency = str(data.get("frequency", "")).upper()
    valid_freqs = {"ONE_TIME", "OCCASIONAL", "FREQUENT", "CONTINUOUS"}
    if frequency and frequency not in valid_freqs:
        violations.append(f"Invalid frequency '{frequency}'. Must be in {valid_freqs}.")

    # 7. CSP Constraint (Section 4 & 5): Immediate Danger vs Low Severity Inconsistency
    imm_danger = str(data.get("immediate_danger", "")).strip().upper()
    emergency = bool(data.get("emergency", False))
    if (imm_danger in ("YES", "TRUE", "1") or emergency) and severity == "LOW":
        violations.append(
            "Validation Conflict: Immediate Danger is marked Yes, but the selected severity is Low, which violates the defined constraint. The AI recommendation has been paused and the complaint requires administrative review."
        )

    # 8. Semantic Contradictions (recorded as warnings or detected conflicts)
    if not emergency and safety_risk == "CRITICAL":
        warnings.append("Semantic Contradiction: Citizen marked 'emergency = False' but 'safety_risk = CRITICAL'.")

    if duration is not None and int(duration) == 0 and frequency == "CONTINUOUS":
        warnings.append("Semantic Contradiction: Duration is 0 days, yet frequency is specified as 'CONTINUOUS'.")

    return len(violations) == 0, violations, warnings
