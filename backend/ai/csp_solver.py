"""
Constraint Satisfaction Problem (CSP) Component for Public Grievance AI.
Implements Sections 8, 9, and 10 of the specification:
1. Variables, Domains, Constraints representation.
2. Validation of structured input combinations.
3. Constraint enforcement and conflict detection with clear explainability.
4. Guaranteed deterministic, explainable reasoning without NLP or black-box ML.
"""

from typing import Dict, Any, List, Optional, Set
from pydantic import BaseModel
from utils.validators import CATEGORY_ISSUE_MAP, is_valid_category_issue_pair


# ==============================================================
# 1. CSP VARIABLE & DOMAIN DEFINITIONS (Section 8)
# ==============================================================

CSP_DOMAINS: Dict[str, Set[str]] = {
    "severity": {"LOW", "MEDIUM", "HIGH", "CRITICAL"},
    "immediate_danger": {"YES", "NO"},
    "affected_people": {"SINGLE", "MULTIPLE"},
    "priority": {"LOW", "MEDIUM", "HIGH", "CRITICAL"},
    "escalation": {"REQUIRED", "NOT_REQUIRED"},
    "location_type": {
        "Public Road",
        "Residential Area",
        "Commercial Zone",
        "School/Hospital Zone",
        "Government Facility",
        "Open Public Ground",
        "Other"
    },
    "department": {
        "Public Works & Infrastructure",
        "Public Lighting",
        "Electricity",
        "Water Supply & Sewerage",
        "Water Supply",
        "Solid Waste Management",
        "Sanitation",
        "Road Maintenance",
        "Roads",
        "Stormwater Drainage",
        "Drainage",
        "Public Transport",
        "Traffic Signals",
        "Public Facilities & Parks",
        "General Civic Administration"
    }
}


class ConstraintResult(BaseModel):
    constraint_id: str
    name: str
    satisfied: bool
    is_blocking: bool
    explanation: str
    conflicting_elements: List[str] = []


class CSPValidationResult(BaseModel):
    is_valid: bool
    assigned_variables: Dict[str, Any]
    constraints_checked: List[ConstraintResult]
    violations: List[str]
    warnings: List[str]
    inferred_department: Optional[str] = None
    inferred_priority: Optional[str] = None
    inferred_escalation: Optional[str] = None
    explanation: str


class CSPSolver:
    """
    Evaluates grievance percepts against formal constraints.
    Detects invalid combinations, infers candidate values, and produces auditable explanations.
    """

    def __init__(self):
        pass

    def normalize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes variables into canonical CSP domain format."""
        norm = dict(data)

        # Normalize immediate_danger
        danger = norm.get("immediate_danger")
        if isinstance(danger, bool):
            norm["immediate_danger"] = "YES" if danger else "NO"
        elif isinstance(danger, str):
            norm["immediate_danger"] = "YES" if danger.strip().upper() in ("YES", "TRUE", "1") else "NO"
        elif norm.get("emergency") is True:
            norm["immediate_danger"] = "YES"
        else:
            norm["immediate_danger"] = "NO"

        # Normalize affected_people
        aff = norm.get("affected_people")
        if isinstance(aff, int):
            norm["affected_people"] = "MULTIPLE" if aff > 1 else "SINGLE"
        elif isinstance(aff, str):
            norm["affected_people"] = "MULTIPLE" if aff.strip().upper() in ("MULTIPLE", "COMMUNITY", "PUBLIC", "MANY") else "SINGLE"
        else:
            norm["affected_people"] = "SINGLE"

        # Normalize severity
        sev = str(norm.get("severity", "MEDIUM")).strip().upper()
        norm["severity"] = sev if sev in CSP_DOMAINS["severity"] else "MEDIUM"

        # Normalize priority if supplied
        prio = str(norm.get("priority", "")).strip().upper()
        norm["priority"] = prio if prio in CSP_DOMAINS["priority"] else None

        # Normalize problem_type / issue_type
        prob = norm.get("problem_type") or norm.get("issue_type") or ""
        norm["problem_type"] = prob

        # Normalize category
        cat = norm.get("complaint_category") or norm.get("category") or ""
        norm["complaint_category"] = cat

        # Normalize location_type
        loc_type = norm.get("location_type") or "Public Road"
        norm["location_type"] = loc_type

        return norm

    def validate_and_solve(self, raw_input: Dict[str, Any]) -> CSPValidationResult:
        """
        Executes Step 1, 2, and 3 of Section 10:
        1. Validate structured input.
        2. Run CSP constraints.
        3. Identify valid/invalid combinations and infer values.
        """
        vars = self.normalize_input(raw_input)
        checks: List[ConstraintResult] = []
        violations: List[str] = []
        warnings: List[str] = []

        inferred_dept: Optional[str] = None
        inferred_prio: Optional[str] = None
        inferred_escl: Optional[str] = None

        category = vars.get("complaint_category", "")
        problem = vars.get("problem_type", "")
        severity = vars.get("severity", "MEDIUM")
        immediate_danger = vars.get("immediate_danger", "NO")
        affected = vars.get("affected_people", "SINGLE")
        priority = vars.get("priority")

        # -------------------------------------------------------------
        # Domain Constraint 0: Valid Category and Problem Type pairing
        # -------------------------------------------------------------
        cat_valid = is_valid_category_issue_pair(category, problem)
        if not cat_valid and category and problem:
            msg = f"Complaint category '{category}' does not support problem type '{problem}'."
            checks.append(ConstraintResult(
                constraint_id="CSP-C0",
                name="Domain Category-Problem Compatibility",
                satisfied=False,
                is_blocking=True,
                explanation=msg,
                conflicting_elements=[f"category={category}", f"problem_type={problem}"]
            ))
            violations.append(msg)
        else:
            checks.append(ConstraintResult(
                constraint_id="CSP-C0",
                name="Domain Category-Problem Compatibility",
                satisfied=True,
                is_blocking=False,
                explanation=f"Problem type '{problem}' is valid within domain of category '{category}'."
            ))

        # -------------------------------------------------------------
        # Constraint 1 (Section 4 & 5): Immediate Danger vs Low Severity Inconsistency
        # -------------------------------------------------------------
        if immediate_danger == "YES" and severity == "LOW":
            msg = (
                "Validation Conflict: Immediate Danger is marked Yes, but the selected severity is Low, "
                "which violates the defined constraint. The AI recommendation has been paused and the complaint "
                "requires administrative review."
            )
            checks.append(ConstraintResult(
                constraint_id="CSP-C1-CONFLICT",
                name="Danger-Severity Inconsistency",
                satisfied=False,
                is_blocking=True,
                explanation=msg,
                conflicting_elements=["immediate_danger=YES", "severity=LOW"]
            ))
            violations.append(msg)

        # -------------------------------------------------------------
        # Constraint 2 (Section 4): IF immediate_danger = YES THEN priority != LOW
        # -------------------------------------------------------------
        if immediate_danger == "YES":
            if priority == "LOW":
                msg = "Immediate danger is marked as YES, but the selected information indicates LOW priority. Priority cannot be LOW during immediate danger."
                checks.append(ConstraintResult(
                    constraint_id="CSP-C1",
                    name="Danger-Priority Constraint",
                    satisfied=False,
                    is_blocking=True,
                    explanation=msg,
                    conflicting_elements=["immediate_danger=YES", "priority=LOW"]
                ))
                violations.append(msg)
            else:
                checks.append(ConstraintResult(
                    constraint_id="CSP-C1",
                    name="Danger-Priority Constraint",
                    satisfied=True,
                    is_blocking=False,
                    explanation="Immediate danger present: Priority constrained to non-LOW (elevated to HIGH/CRITICAL)."
                ))
                # Infer minimum HIGH priority
                inferred_prio = "CRITICAL" if severity == "CRITICAL" else "HIGH"

        # -------------------------------------------------------------
        # Constraint 3 (Section 4): IF severity = CRITICAL THEN priority = CRITICAL
        # -------------------------------------------------------------
        pop_count = 1
        raw_pop = raw_input.get("affected_people") or raw_input.get("population_impact")
        if raw_pop is not None:
            try:
                pop_count = int(raw_pop)
            except (ValueError, TypeError):
                pop_count = 1

        if severity == "CRITICAL":
            inferred_prio = "CRITICAL"
            checks.append(ConstraintResult(
                constraint_id="CSP-C2",
                name="Critical Severity Constraint",
                satisfied=True,
                is_blocking=False,
                explanation="Severity is CRITICAL, forcing priority to CRITICAL."
            ))
        elif severity == "HIGH" and pop_count >= 10:
            inferred_prio = "CRITICAL"
            checks.append(ConstraintResult(
                constraint_id="CSP-C2",
                name="High Severity with Population Impact >= 10",
                satisfied=True,
                is_blocking=False,
                explanation=f"Severity is HIGH with Population Impact ({pop_count} >= 10), elevating priority to CRITICAL."
            ))
        elif severity == "LOW" and immediate_danger == "NO":
            if not inferred_prio:
                inferred_prio = "LOW"
            checks.append(ConstraintResult(
                constraint_id="CSP-C2",
                name="Low Severity Baseline Constraint",
                satisfied=True,
                is_blocking=False,
                explanation="Non-critical severity with no immediate danger satisfied."
            ))

        # -------------------------------------------------------------
        # Constraint 4 (Section 4): IF severity = HIGH AND affected_people = MULTIPLE THEN escalation = REQUIRED
        # -------------------------------------------------------------
        if (severity in ("HIGH", "CRITICAL") and (affected == "MULTIPLE" or pop_count >= 10)) or immediate_danger == "YES":
            inferred_escl = "REQUIRED"
            checks.append(ConstraintResult(
                constraint_id="CSP-C3",
                name="High Impact Escalation Constraint",
                satisfied=True,
                is_blocking=False,
                explanation=f"High impact scope (Severity '{severity}', Population Impact {pop_count}): Escalation is REQUIRED."
            ))
        else:
            inferred_escl = "NOT_REQUIRED"
            checks.append(ConstraintResult(
                constraint_id="CSP-C3",
                name="High Impact Escalation Constraint",
                satisfied=True,
                is_blocking=False,
                explanation="Standard impact scope: Escalation not required by CSP constraint."
            ))

        # -------------------------------------------------------------
        # Constraint 4 (Section 9): IF problem_type = STREETLIGHT THEN recommended department = ELECTRICITY / PUBLIC LIGHTING
        # -------------------------------------------------------------
        prob_upper = problem.upper().replace(" ", "_")
        if any(kw in prob_upper for kw in ["STREETLIGHT", "LIGHTING", "LUMINAIRE"]):
            inferred_dept = "Public Lighting"
            checks.append(ConstraintResult(
                constraint_id="CSP-C4",
                name="Streetlight Routing Constraint",
                satisfied=True,
                is_blocking=False,
                explanation="Problem type is streetlight-related, mapping recommended department to Public Lighting / Electricity."
            ))

        # -------------------------------------------------------------
        # Constraint 5 (Section 9): IF problem_type = GARBAGE THEN recommended department = SANITATION
        # -------------------------------------------------------------
        elif any(kw in prob_upper for kw in ["GARBAGE", "DUMPING", "CLEANLINESS", "WASTE"]):
            inferred_dept = "Solid Waste Management"
            checks.append(ConstraintResult(
                constraint_id="CSP-C5",
                name="Garbage/Sanitation Routing Constraint",
                satisfied=True,
                is_blocking=False,
                explanation="Problem type is sanitation/waste-related, mapping recommended department to Solid Waste Management / Sanitation."
            ))

        # -------------------------------------------------------------
        # Constraint 6 (Section 9): IF problem_type = WATER_LEAKAGE THEN recommended department = WATER_SUPPLY
        # -------------------------------------------------------------
        elif any(kw in prob_upper for kw in ["WATER", "LEAKAGE", "PIPELINE", "SUPPLY"]):
            inferred_dept = "Water Supply & Sewerage"
            checks.append(ConstraintResult(
                constraint_id="CSP-C6",
                name="Water Supply Routing Constraint",
                satisfied=True,
                is_blocking=False,
                explanation="Problem type is water-related, mapping recommended department to Water Supply & Sewerage."
            ))
        elif any(kw in prob_upper for kw in ["POTHOLE", "ROAD", "PAVEMENT"]):
            inferred_dept = "Road Maintenance"
            checks.append(ConstraintResult(
                constraint_id="CSP-C7",
                name="Road Maintenance Routing Constraint",
                satisfied=True,
                is_blocking=False,
                explanation="Problem type is road-related, mapping recommended department to Road Maintenance."
            ))

        # Synthesize overall explanation
        is_valid = len(violations) == 0
        if is_valid:
            exp = (
                f"CSP Validation Succeeded. Evaluated {len(checks)} domain constraints across "
                f"variables {{severity={severity}, immediate_danger={immediate_danger}, "
                f"affected_people={affected}, problem_type='{problem}'}}. Zero blocking constraint violations."
            )
        else:
            exp = f"CSP Validation Failed. Constraint violations: {'; '.join(violations)}"

        return CSPValidationResult(
            is_valid=is_valid,
            assigned_variables=vars,
            constraints_checked=checks,
            violations=violations,
            warnings=warnings,
            inferred_department=inferred_dept,
            inferred_priority=inferred_prio,
            inferred_escalation=inferred_escl,
            explanation=exp
        )


csp_solver = CSPSolver()
