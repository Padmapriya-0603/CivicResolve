"""
Knowledge Representation: Fact Extraction and Working Memory for Classical AI.
Translates structured complaint input into symbolic ground facts.
Explicitly tracks missing facts to prevent unauthorized default assumptions.
"""

from typing import Dict, Any, Optional, List
from models.schemas import ComplaintCreateRequest


class FactStore:
    """Working Memory storing ground and derived facts during forward chaining."""

    def __init__(self, initial_facts: Optional[Dict[str, Any]] = None):
        self._facts: Dict[str, Any] = {}
        self._derived_facts: Dict[str, Any] = {}
        self._missing_facts: List[str] = []
        if initial_facts:
            for k, v in initial_facts.items():
                self.set_fact(k, v)

    def set_fact(self, key: str, value: Any, is_derived: bool = False) -> None:
        """Stores a ground or derived fact."""
        self._facts[key] = value
        if is_derived:
            self._derived_facts[key] = value

    def get_fact(self, key: str, default: Any = None) -> Any:
        return self._facts.get(key, default)

    def has_fact(self, key: str) -> bool:
        return key in self._facts and self._facts[key] is not None

    def record_missing(self, field_name: str) -> None:
        if field_name not in self._missing_facts:
            self._missing_facts.append(field_name)

    @property
    def all_facts(self) -> Dict[str, Any]:
        return self._facts.copy()

    @property
    def derived_facts(self) -> Dict[str, Any]:
        return self._derived_facts.copy()

    @property
    def missing_facts(self) -> List[str]:
        return self._missing_facts.copy()


def extract_facts_from_request(req: ComplaintCreateRequest) -> FactStore:
    """
    Transforms structured complaint request into internal symbolic facts.
    Normalizes string identifiers (e.g. 'Streetlight Not Working' -> 'streetlight_not_working').
    Preserves None for missing numeric attributes so rules do not make false assumptions.
    """
    raw_issue = req.issue_type.strip().lower().replace(" ", "_")
    raw_category = req.category.strip().lower().replace(" ", "_")
    raw_severity = req.severity.strip().lower()
    raw_safety_risk = req.safety_risk.strip().lower()
    raw_frequency = req.frequency.strip().lower()

    # Normalize immediate_danger and emergency
    imm_danger = "NO"
    if req.immediate_danger:
        imm_danger = "YES" if str(req.immediate_danger).strip().upper() in ("YES", "TRUE", "1") else "NO"
    elif req.emergency:
        imm_danger = "YES"

    facts = FactStore()
    facts.set_fact("citizen_name", req.citizen_name)
    facts.set_fact("ward", req.ward)
    facts.set_fact("location", req.location)
    facts.set_fact("category", raw_category)
    facts.set_fact("issue_type", raw_issue)
    facts.set_fact("severity", raw_severity)
    facts.set_fact("immediate_danger", imm_danger)
    facts.set_fact("safety_risk", raw_safety_risk)
    facts.set_fact("frequency", raw_frequency)
    facts.set_fact("evidence_available", bool(req.evidence_available))
    facts.set_fact("evidence_filename", req.evidence_filename)
    facts.set_fact("public_accessibility_affected", bool(req.public_accessibility_affected))
    facts.set_fact("recurrence", bool(req.recurrence))
    facts.set_fact("emergency", bool(req.emergency or imm_danger == "YES"))

    # Optional facts: only set if non-null, else record as missing fact if evaluated
    if req.duration_days is not None:
        facts.set_fact("duration_days", int(req.duration_days))
    else:
        facts.set_fact("duration_days", None)

    if req.affected_people is not None:
        facts.set_fact("affected_people", int(req.affected_people))
        facts.set_fact("population_impact", int(req.affected_people))
    else:
        facts.set_fact("affected_people", None)
        facts.set_fact("population_impact", None)

    return facts
