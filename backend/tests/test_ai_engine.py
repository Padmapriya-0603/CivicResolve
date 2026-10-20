"""
Automated Test Suite for Classical AI Grievance Routing & Reasoning Engine.
Covers all 10 mandated test specifications:
TEST 1: Streetlight Not Working + High Severity + 80 Affected -> Public Lighting, HIGH
TEST 2: Safety Risk = Critical -> Priority = CRITICAL
TEST 3: Missing affected_people -> Handled without guessing (cannot evaluate condition)
TEST 4: Invalid Category/Issue Combination -> CSP Validation Error
TEST 5: Conflicting Rules -> Explicit Conflict Resolution with Precedence
TEST 6: Emergency = True -> Immediate Escalation
TEST 7: Same Input Submitted Twice -> Identical Deterministic Output
TEST 8: Different Issue Type -> Different Applicable Routing Rule
TEST 9: Negative Duration -> Validation Error
TEST 10: Missing Required Information -> Blocks Unsupported Decision
"""

import pytest
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.schemas import ComplaintCreateRequest
from ai.grievance_agent import GrievanceAgent
from utils.validators import validate_complaint_constraints


@pytest.fixture
def agent():
    return GrievanceAgent()


def test_1_streetlight_high_priority(agent):
    """TEST 1: Issue: Streetlight Not Working, Severity: High, Affected: 80 -> Department: Public Lighting, Priority: HIGH"""
    req = ComplaintCreateRequest(
        citizen_name="Citizen Test 1",
        phone="9876543210",
        email="test1@example.com",
        ward="Ward 1",
        location="North Road",
        category="Public Lighting",
        issue_type="Streetlight Not Working",
        severity="HIGH",
        affected_people=80,
        frequency="FREQUENT",
        safety_risk="HIGH",
        duration_days=5,
        recurrence=True,
        emergency=False
    )
    res = agent.process_grievance(req)
    assert res["success"] is True
    assert res["department"] == "Public Lighting"
    assert res["priority"] == "HIGH"
    # Should fire R001 (routing) and PR003/PR005 (priority HIGH)
    fired_rule_ids = [s["rule_id"] for s in res["reasoning_trace"] if s.get("rule_id")]
    assert "R001" in fired_rule_ids


def test_2_safety_risk_critical(agent):
    """TEST 2: Safety Risk: Critical -> Priority: CRITICAL"""
    req = ComplaintCreateRequest(
        citizen_name="Citizen Test 2",
        phone="9876543210",
        email="test2@example.com",
        ward="Ward 2",
        location="South Avenue",
        category="Electricity Infrastructure",
        issue_type="Exposed Electrical Wire",
        severity="LOW",  # Reported low severity, but safety risk is critical
        affected_people=5,
        frequency="ONE_TIME",
        safety_risk="CRITICAL",
        duration_days=1,
        recurrence=False,
        emergency=False
    )
    res = agent.process_grievance(req)
    assert res["success"] is True
    assert res["priority"] == "CRITICAL"
    assert res["escalation"] == "IMMEDIATE"


def test_3_missing_affected_people(agent):
    """TEST 3: Missing affected_people -> Affected-person rule cannot be evaluated; not guessed as 0"""
    req = ComplaintCreateRequest(
        citizen_name="Citizen Test 3",
        phone="9876543210",
        email="test3@example.com",
        ward="Ward 3",
        location="Market Yard",
        category="Sanitation",
        issue_type="Garbage Not Collected",
        severity="HIGH",
        affected_people=None,  # Intentionally missing!
        frequency="OCCASIONAL",
        safety_risk="LOW",
        duration_days=2,
        recurrence=False,
        emergency=False
    )
    res = agent.process_grievance(req)
    assert res["success"] is True
    # The missing info log must record that affected_people rule was not evaluated
    missing_items = " ".join(res["missing_info"])
    assert "affected_people" in missing_items


def test_4_invalid_category_issue_csp():
    """TEST 4: Incompatible category/issue combination -> CSP Validation error"""
    # Category = Water Supply, Issue = Streetlight Not Working
    data = {
        "category": "Water Supply",
        "issue_type": "Streetlight Not Working",
        "duration_days": 1,
        "affected_people": 10,
        "severity": "LOW",
        "safety_risk": "NONE",
        "frequency": "ONE_TIME"
    }
    is_valid, violations, warnings = validate_complaint_constraints(data)
    assert is_valid is False
    assert any("Incompatible category/issue" in v for v in violations)


def test_5_conflicting_rules_precedence(agent):
    """TEST 5: Conflicting rules -> Explicit conflict resolution (CRITICAL overrides HIGH)"""
    # Rule PR001 fires (safety_risk=CRITICAL -> CRITICAL)
    # Rule PR003 fires (severity=HIGH and affected_people > 50 -> HIGH)
    req = ComplaintCreateRequest(
        citizen_name="Citizen Test 5",
        phone="9876543210",
        email="test5@example.com",
        ward="Ward 5",
        location="High Bridge",
        category="Roads",
        issue_type="Damaged Road",
        severity="HIGH",
        affected_people=100,
        frequency="FREQUENT",
        safety_risk="CRITICAL",
        duration_days=4,
        recurrence=False,
        emergency=False
    )
    res = agent.process_grievance(req)
    assert res["success"] is True
    # Priority conflict should be detected and resolved to CRITICAL
    assert res["priority"] == "CRITICAL"
    conflict_types = [c.get("conflict_type") for c in res["conflicts"]]
    assert "RULE_CONCLUSION_CONFLICT" in conflict_types


def test_6_emergency_immediate_escalation(agent):
    """TEST 6: Emergency = true -> Immediate escalation"""
    req = ComplaintCreateRequest(
        citizen_name="Citizen Test 6",
        phone="9876543210",
        email="test6@example.com",
        ward="Ward 6",
        location="Canal Road",
        category="Drainage",
        issue_type="Overflow",
        severity="MEDIUM",
        affected_people=20,
        frequency="CONTINUOUS",
        safety_risk="MEDIUM",
        duration_days=1,
        recurrence=False,
        emergency=True
    )
    res = agent.process_grievance(req)
    assert res["success"] is True
    assert res["priority"] == "CRITICAL"
    assert res["escalation"] == "IMMEDIATE"


def test_7_deterministic_reproducibility(agent):
    """TEST 7: Same input submitted twice -> Identical reasoning result"""
    req = ComplaintCreateRequest(
        citizen_name="Citizen Test 7",
        phone="9876543210",
        email="test7@example.com",
        ward="Ward 7",
        location="Station Square",
        category="Public Lighting",
        issue_type="Streetlight Not Working",
        severity="HIGH",
        affected_people=80,
        frequency="FREQUENT",
        safety_risk="HIGH",
        duration_days=5,
        recurrence=True,
        emergency=False
    )
    res1 = agent.process_grievance(req)
    res2 = agent.process_grievance(req)
    assert res1["department"] == res2["department"]
    assert res1["priority"] == res2["priority"]
    assert res1["escalation"] == res2["escalation"]
    assert len(res1["reasoning_trace"]) == len(res2["reasoning_trace"])


def test_8_different_issue_different_routing(agent):
    """TEST 8: Different issue type -> Different applicable routing rule"""
    req1 = ComplaintCreateRequest(
        citizen_name="Citizen 8A",
        phone="9876543210",
        email="test8a@example.com",
        ward="Ward 8",
        location="Lane A",
        category="Public Lighting",
        issue_type="Streetlight Not Working",
        severity="LOW",
        affected_people=5,
        frequency="ONE_TIME",
        safety_risk="NONE",
        duration_days=1,
        recurrence=False,
        emergency=False
    )
    req2 = ComplaintCreateRequest(
        citizen_name="Citizen 8B",
        phone="9876543210",
        email="test8b@example.com",
        ward="Ward 8",
        location="Lane B",
        category="Sanitation",
        issue_type="Garbage Not Collected",
        severity="LOW",
        affected_people=5,
        frequency="ONE_TIME",
        safety_risk="NONE",
        duration_days=1,
        recurrence=False,
        emergency=False
    )
    res1 = agent.process_grievance(req1)
    res2 = agent.process_grievance(req2)
    assert res1["department"] == "Public Lighting"
    assert res2["department"] == "Sanitation"
    assert res1["department"] != res2["department"]


def test_9_negative_duration_validation():
    """TEST 9: Negative duration -> Validation error"""
    with pytest.raises(ValueError):
        ComplaintCreateRequest(
            citizen_name="Citizen Test 9",
            phone="9876543210",
            email="test9@example.com",
            ward="Ward 9",
            location="Lane 9",
            category="Sanitation",
            issue_type="Garbage Not Collected",
            severity="LOW",
            affected_people=5,
            frequency="ONE_TIME",
            safety_risk="NONE",
            duration_days=-3,  # Negative!
            recurrence=False,
            emergency=False
        )


def test_10_missing_required_facts_blocks_unsupported_decision():
    """TEST 10: Missing or invalid required taxonomy -> Blocks unsupported final decision"""
    data = {
        "category": "InvalidCategoryUnknown",
        "issue_type": "UnknownIssue",
        "duration_days": 1,
        "affected_people": 10,
        "severity": "LOW",
        "safety_risk": "NONE",
        "frequency": "ONE_TIME"
    }
    is_valid, violations, warnings = validate_complaint_constraints(data)
    assert is_valid is False
    assert len(violations) > 0
