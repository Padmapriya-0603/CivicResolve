"""
Production Rules Repository for Classical AI Inference Engine.
Defines formal forward-chaining rules for:
- Department Routing
- Priority Reasoning (with conflict resolution precedence)
- Escalation Determination
- Semantic Conflict Detection
"""

from typing import List
from models.rule import ProductionRule, ConditionClause


def get_default_rules() -> List[ProductionRule]:
    """Returns the set of formal production rules loaded into the knowledge base."""
    rules: List[ProductionRule] = []

    # ==========================================
    # 1. ROUTING RULES (R001 - R015)
    # ==========================================
    rules.append(
        ProductionRule(
            rule_id="R001",
            rule_name="Streetlight Routing",
            rule_type="ROUTING",
            description="Routes streetlight outages to Public Lighting department.",
            conditions=[
                ConditionClause(field="issue_type", operator="==", value="streetlight_not_working")
            ],
            conclusion={"department": "Public Lighting"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R002",
            rule_name="Streetlight Damaged Routing",
            rule_type="ROUTING",
            description="Routes physical streetlight damage to Public Lighting department.",
            conditions=[
                ConditionClause(field="issue_type", operator="==", value="streetlight_damaged")
            ],
            conclusion={"department": "Public Lighting"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R003",
            rule_name="Multiple Streetlights Routing",
            rule_type="ROUTING",
            description="Routes widespread streetlight failure to Public Lighting department.",
            conditions=[
                ConditionClause(field="issue_type", operator="==", value="multiple_streetlights_not_working")
            ],
            conclusion={"department": "Public Lighting"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R004",
            rule_name="Garbage Collection Routing",
            rule_type="ROUTING",
            description="Routes uncollected garbage to Sanitation department.",
            conditions=[
                ConditionClause(field="issue_type", operator="==", value="garbage_not_collected")
            ],
            conclusion={"department": "Sanitation"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R005",
            rule_name="Illegal Dumping Routing",
            rule_type="ROUTING",
            description="Routes unauthorized waste dumping to Sanitation department.",
            conditions=[
                ConditionClause(field="issue_type", operator="==", value="illegal_dumping")
            ],
            conclusion={"department": "Sanitation"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R006",
            rule_name="Public Area Cleanliness Routing",
            rule_type="ROUTING",
            description="Routes public hygiene complaints to Sanitation department.",
            conditions=[
                ConditionClause(field="issue_type", operator="==", value="public_area_cleanliness")
            ],
            conclusion={"department": "Sanitation"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R007",
            rule_name="Water Supply Outage Routing",
            rule_type="ROUTING",
            description="Routes potable water shortages to Water Supply department.",
            conditions=[
                ConditionClause(field="issue_type", operator="==", value="no_water_supply")
            ],
            conclusion={"department": "Water Supply"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R008",
            rule_name="Water Leakage & Contamination Routing",
            rule_type="ROUTING",
            description="Routes pipe leaks or water contamination to Water Supply department.",
            conditions=[
                ConditionClause(field="issue_type", operator="in", value=["water_leakage", "pipe_leakage", "pipeline_leakage", "contaminated_supply", "low_water_pressure", "no_water_supply"])
            ],
            conclusion={"department": "Water Supply"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R009",
            rule_name="Road Surface & Pothole Routing",
            rule_type="ROUTING",
            description="Routes asphalt defects, potholes, and damaged roads to Road Maintenance.",
            conditions=[
                ConditionClause(field="issue_type", operator="in", value=["pothole", "damaged_road", "blocked_road", "missing_road_sign"])
            ],
            conclusion={"department": "Road Maintenance"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R010",
            rule_name="Drainage & Overflow Routing",
            rule_type="ROUTING",
            description="Routes drain clogs, sewage overflow, and canal defects to Drainage department.",
            conditions=[
                ConditionClause(field="issue_type", operator="in", value=["drain_blockage", "overflow", "damaged_drain"])
            ],
            conclusion={"department": "Drainage"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R011",
            rule_name="Public Transport Routing",
            rule_type="ROUTING",
            description="Routes damaged transit shelters and service disruptions to Public Transport.",
            conditions=[
                ConditionClause(field="issue_type", operator="in", value=["bus_stop_damaged", "route_disruption", "unsafe_transit_stop"])
            ],
            conclusion={"department": "Public Transport"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R012",
            rule_name="Traffic Signal Routing",
            rule_type="ROUTING",
            description="Routes faulty traffic signals and junction controllers to Traffic Management.",
            conditions=[
                ConditionClause(field="issue_type", operator="in", value=["signal_not_working", "signal_timer_fault", "damaged_signal_post"])
            ],
            conclusion={"department": "Traffic Management"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R013",
            rule_name="Public Facilities & Property Routing",
            rule_type="ROUTING",
            description="Routes public benches, restrooms, and park equipment to Public Facilities.",
            conditions=[
                ConditionClause(field="issue_type", operator="in", value=["park_bench_broken", "public_toilet_unusable", "playground_equipment_damaged", "damaged_public_property", "broken_facility", "structural_damage"])
            ],
            conclusion={"department": "Public Facilities"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R014",
            rule_name="Hazardous Waste Routing",
            rule_type="ROUTING",
            description="Routes hazardous chemicals, medical waste, or compost overflow to Waste Management.",
            conditions=[
                ConditionClause(field="issue_type", operator="in", value=["hazardous_waste_dumped", "compost_facility_overflow", "debris_uncollected"])
            ],
            conclusion={"department": "Waste Management"},
            priority_order=10
        )
    )

    rules.append(
        ProductionRule(
            rule_id="R015",
            rule_name="Electrical Grid Routing",
            rule_type="ROUTING",
            description="Routes dangling high-voltage wires, sparking transformers, or broken poles to Electricity Infrastructure.",
            conditions=[
                ConditionClause(field="issue_type", operator="in", value=["exposed_electrical_wire", "transformer_sparking", "fallen_power_pole"])
            ],
            conclusion={"department": "Electricity Infrastructure"},
            priority_order=10
        )
    )

    # ==========================================
    # 2. PRIORITY RULES (PR000 - PR008)
    # ==========================================
    rules.append(
        ProductionRule(
            rule_id="PR000",
            rule_name="Immediate Danger Priority & Emergency",
            rule_type="PRIORITY",
            description="Assigns CRITICAL priority and asserts emergency fact when immediate danger is YES.",
            conditions=[
                ConditionClause(field="immediate_danger", operator="==", value="YES")
            ],
            conclusion={"priority": "CRITICAL", "emergency": True},
            priority_order=1
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR_POP10",
            rule_name="High Severity with Population Impact >= 10 on Critical Utilities",
            rule_type="PRIORITY",
            description="Assigns CRITICAL priority when severity is HIGH and population impact is at least 10 on critical utilities.",
            conditions=[
                ConditionClause(field="severity", operator="==", value="high"),
                ConditionClause(field="affected_people", operator=">=", value=10),
                ConditionClause(field="category", operator="in", value=["water", "water_supply", "electricity", "electricity_infrastructure", "drainage"])
            ],
            conclusion={"priority": "CRITICAL"},
            priority_order=2
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR001",
            rule_name="Critical Safety Hazard Priority",
            rule_type="PRIORITY",
            description="Assigns CRITICAL priority when safety hazard is CRITICAL.",
            conditions=[
                ConditionClause(field="safety_risk", operator="==", value="critical")
            ],
            conclusion={"priority": "CRITICAL"},
            priority_order=2
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR002",
            rule_name="Declared Emergency Priority",
            rule_type="PRIORITY",
            description="Assigns CRITICAL priority when citizen flags an emergency.",
            conditions=[
                ConditionClause(field="emergency", operator="==", value=True)
            ],
            conclusion={"priority": "CRITICAL"},
            priority_order=2
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR003",
            rule_name="High Severity with Large Population Impact",
            rule_type="PRIORITY",
            description="Assigns HIGH priority when severity is high and affected people > 50.",
            conditions=[
                ConditionClause(field="severity", operator="==", value="high"),
                ConditionClause(field="affected_people", operator=">", value=50)
            ],
            conclusion={"priority": "HIGH"},
            priority_order=3
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR004",
            rule_name="Continuous High Duration Priority",
            rule_type="PRIORITY",
            description="Assigns HIGH priority when problem is continuous and persists >= 3 days.",
            conditions=[
                ConditionClause(field="frequency", operator="==", value="continuous"),
                ConditionClause(field="duration_days", operator=">=", value=3)
            ],
            conclusion={"priority": "HIGH"},
            priority_order=4
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR005",
            rule_name="High Safety Risk Priority",
            rule_type="PRIORITY",
            description="Assigns HIGH priority when safety risk is HIGH.",
            conditions=[
                ConditionClause(field="safety_risk", operator="==", value="high")
            ],
            conclusion={"priority": "HIGH"},
            priority_order=5
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR006",
            rule_name="Accessibility Impairment Priority",
            rule_type="PRIORITY",
            description="Assigns HIGH priority when public access is blocked and severity is non-trivial.",
            conditions=[
                ConditionClause(field="public_accessibility_affected", operator="==", value=True),
                ConditionClause(field="severity", operator="in", value=["medium", "high", "critical"])
            ],
            conclusion={"priority": "HIGH"},
            priority_order=6
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR007",
            rule_name="Moderate Impact Priority",
            rule_type="PRIORITY",
            description="Assigns MEDIUM priority when severity is MEDIUM.",
            conditions=[
                ConditionClause(field="severity", operator="==", value="medium")
            ],
            conclusion={"priority": "MEDIUM"},
            priority_order=7
        )
    )

    rules.append(
        ProductionRule(
            rule_id="PR008",
            rule_name="Low Impact Baseline Priority",
            rule_type="PRIORITY",
            description="Assigns LOW priority when severity is LOW.",
            conditions=[
                ConditionClause(field="severity", operator="==", value="low")
            ],
            conclusion={"priority": "LOW"},
            priority_order=8
        )
    )

    # ==========================================
    # 3. ESCALATION RULES (ER_EMERGENCY, ER001 - ER005)
    # ==========================================
    rules.append(
        ProductionRule(
            rule_id="ER_EMERGENCY",
            rule_name="Immediate Escalation on Declared Emergency",
            rule_type="ESCALATION",
            description="Requires IMMEDIATE escalation when an emergency or immediate danger fact is derived.",
            conditions=[
                ConditionClause(field="emergency", operator="==", value=True)
            ],
            conclusion={"escalation": "IMMEDIATE"},
            priority_order=1
        )
    )

    rules.append(
        ProductionRule(
            rule_id="ER001",
            rule_name="Immediate Escalation on Critical Priority",
            rule_type="ESCALATION",
            description="Requires IMMEDIATE escalation when derived priority is CRITICAL.",
            conditions=[
                ConditionClause(field="priority", operator="==", value="CRITICAL")
            ],
            conclusion={"escalation": "IMMEDIATE"},
            priority_order=1
        )
    )

    rules.append(
        ProductionRule(
            rule_id="ER002",
            rule_name="Prolonged High Priority Escalation",
            rule_type="ESCALATION",
            description="Requires escalation when priority is HIGH and problem persists >= 3 days.",
            conditions=[
                ConditionClause(field="priority", operator="==", value="HIGH"),
                ConditionClause(field="duration_days", operator=">=", value=3)
            ],
            conclusion={"escalation": "REQUIRED"},
            priority_order=2
        )
    )

    rules.append(
        ProductionRule(
            rule_id="ER003",
            rule_name="Recurrent High Severity Escalation",
            rule_type="ESCALATION",
            description="Requires escalation when an issue recurs with high/critical severity.",
            conditions=[
                ConditionClause(field="recurrence", operator="==", value=True),
                ConditionClause(field="severity", operator="in", value=["high", "critical"])
            ],
            conclusion={"escalation": "REQUIRED"},
            priority_order=3
        )
    )

    rules.append(
        ProductionRule(
            rule_id="ER004",
            rule_name="Emergency Transit Transit Access Escalation",
            rule_type="ESCALATION",
            description="Requires IMMEDIATE escalation when emergency impedes public access.",
            conditions=[
                ConditionClause(field="emergency", operator="==", value=True),
                ConditionClause(field="public_accessibility_affected", operator="==", value=True)
            ],
            conclusion={"escalation": "IMMEDIATE"},
            priority_order=4
        )
    )

    rules.append(
        ProductionRule(
            rule_id="ER005",
            rule_name="Baseline No Escalation",
            rule_type="ESCALATION",
            description="Sets NO_ESCALATION for standard complaints.",
            conditions=[
                ConditionClause(field="priority", operator="in", value=["LOW", "MEDIUM", "HIGH"])
            ],
            conclusion={"escalation": "NO_ESCALATION"},
            priority_order=10
        )
    )

    return rules
