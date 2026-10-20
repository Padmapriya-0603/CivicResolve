"""
Knowledge Base for Public Grievance AI.
Stores ontological entities: Departments, Categories, Issue Taxonomies,
Departmental capabilities, and Escalation Authorities.
"""

from typing import Dict, List, Any, Optional

DEPARTMENTS_KB: List[Dict[str, Any]] = [
    {
        "department_id": "DEPT_PUB_LIGHTING",
        "name": "Public Lighting",
        "description": "Responsible for municipal street lamps, high-mast illumination, pole maintenance, and timers.",
        "supported_issues": [
            "streetlight_not_working",
            "streetlight_damaged",
            "multiple_streetlights_not_working"
        ],
        "escalation_authority": "Chief Electrical Inspector & Deputy Commissioner (Public Lighting)",
        "is_active": True
    },
    {
        "department_id": "DEPT_SANITATION",
        "name": "Sanitation",
        "description": "Handles daily household garbage collection, public street sweeping, and market cleanliness.",
        "supported_issues": [
            "garbage_not_collected",
            "illegal_dumping",
            "public_area_cleanliness"
        ],
        "escalation_authority": "Director of Municipal Solid Waste & Chief Health Officer",
        "is_active": True
    },
    {
        "department_id": "DEPT_WATER_SUPPLY",
        "name": "Water Supply",
        "description": "Manages potable drinking water pipeline networks, water pressure, leaks, and contamination.",
        "supported_issues": [
            "no_water_supply",
            "water_leakage",
            "contaminated_supply",
            "low_water_pressure"
        ],
        "escalation_authority": "Superintending Engineer (Water Supply & Sewerage Board)",
        "is_active": True
    },
    {
        "department_id": "DEPT_ROAD_MAINT",
        "name": "Road Maintenance",
        "description": "Handles asphalt surfacing, potholes, road obstructions, cave-ins, and road signage.",
        "supported_issues": [
            "pothole",
            "damaged_road",
            "blocked_road",
            "missing_road_sign"
        ],
        "escalation_authority": "Chief Engineer (Civil Works & Highways)",
        "is_active": True
    },
    {
        "department_id": "DEPT_DRAINAGE",
        "name": "Drainage",
        "description": "Manages storm water drains, underground sewers, flood prevention, and canal desilting.",
        "supported_issues": [
            "drain_blockage",
            "overflow",
            "damaged_drain"
        ],
        "escalation_authority": "Superintendent Engineer (Storm Water Drainage & Flood Control)",
        "is_active": True
    },
    {
        "department_id": "DEPT_PUB_TRANSPORT",
        "name": "Public Transport",
        "description": "Oversees public bus stops, terminal shelters, transit corridors, and route schedules.",
        "supported_issues": [
            "bus_stop_damaged",
            "route_disruption",
            "unsafe_transit_stop"
        ],
        "escalation_authority": "Commissioner of City Transport Authority",
        "is_active": True
    },
    {
        "department_id": "DEPT_TRAFFIC_MGMT",
        "name": "Traffic Management",
        "description": "Operates electronic traffic signals, lane markers, traffic cameras, and pedestrian crossings.",
        "supported_issues": [
            "signal_not_working",
            "signal_timer_fault",
            "damaged_signal_post"
        ],
        "escalation_authority": "Additional Commissioner of Police (Traffic Management)",
        "is_active": True
    },
    {
        "department_id": "DEPT_PUB_FACILITIES",
        "name": "Public Facilities",
        "description": "Maintains municipal parks, public restrooms, children's play equipment, and open spaces.",
        "supported_issues": [
            "park_bench_broken",
            "public_toilet_unusable",
            "playground_equipment_damaged",
            "damaged_public_property",
            "broken_facility",
            "structural_damage"
        ],
        "escalation_authority": "Director of Municipal Parks & Civic Amenities",
        "is_active": True
    },
    {
        "department_id": "DEPT_WASTE_MGMT",
        "name": "Waste Management",
        "description": "Oversees hazardous and industrial disposal, biomedical waste, and processing yards.",
        "supported_issues": [
            "hazardous_waste_dumped",
            "compost_facility_overflow",
            "debris_uncollected"
        ],
        "escalation_authority": "Regional Officer (State Pollution Control Board)",
        "is_active": True
    },
    {
        "department_id": "DEPT_ELEC_INFRA",
        "name": "Electricity Infrastructure",
        "description": "Manages high-voltage power lines, distribution transformers, live wires, and electric substations.",
        "supported_issues": [
            "exposed_electrical_wire",
            "transformer_sparking",
            "fallen_power_pole"
        ],
        "escalation_authority": "Executive Engineer (Power Distribution Corporation)",
        "is_active": True
    }
]

PRIORITY_PRECEDENCE: Dict[str, int] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

ESCALATION_PRECEDENCE: Dict[str, int] = {
    "IMMEDIATE": 3,
    "REQUIRED": 2,
    "NO_ESCALATION": 1
}


class KnowledgeBase:
    """Provides querying and capability lookup over municipal domains."""

    def __init__(self, departments: Optional[List[Dict[str, Any]]] = None):
        self.departments = departments or DEPARTMENTS_KB

    def get_all_departments(self) -> List[Dict[str, Any]]:
        return self.departments

    def find_department_by_id(self, dept_id: str) -> Optional[Dict[str, Any]]:
        for d in self.departments:
            if d["department_id"] == dept_id:
                return d
        return None

    def find_department_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        for d in self.departments:
            if d["name"].lower() == name.lower():
                return d
        return None

    def find_department_for_issue(self, issue_type: str) -> Optional[Dict[str, Any]]:
        norm = issue_type.strip().lower().replace(" ", "_")
        for d in self.departments:
            if not d.get("is_active", True):
                continue
            if norm in [i.lower() for i in d["supported_issues"]]:
                return d
        return None

    def supports_issue(self, dept_name: str, issue_type: str) -> bool:
        dept = self.find_department_by_name(dept_name)
        if not dept:
            return False
        norm = issue_type.strip().lower().replace(" ", "_")
        return norm in [i.lower() for i in dept["supported_issues"]]

    def get_escalation_authority(self, dept_name: str) -> str:
        dept = self.find_department_by_name(dept_name)
        if dept:
            return dept.get("escalation_authority", "Municipal Commissioner")
        return "Municipal Commissioner"


kb_instance = KnowledgeBase()
