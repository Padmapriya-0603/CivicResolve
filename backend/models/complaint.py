"""
Domain model representing a public grievance in memory and storage.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GrievanceComplaint:
    complaint_id: str
    citizen_name: str
    phone: str
    email: str
    ward: str
    location: str
    preferred_contact: str
    category: str
    issue_type: str
    severity: str
    frequency: str
    safety_risk: str
    duration_days: Optional[int] = None
    affected_people: Optional[int] = None
    evidence_available: bool = False
    evidence_filename: Optional[str] = None
    public_accessibility_affected: bool = False
    recurrence: bool = False
    emergency: bool = False

    # Inferred / Derived AI fields
    department: Optional[str] = None
    ai_department: Optional[str] = None
    manual_override: bool = False
    manual_override_reason: Optional[str] = None
    priority: str = "LOW"
    escalation: str = "NO_ESCALATION"
    status: str = "Submitted"

    # Auditing and trace metadata
    missing_info: List[str] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    explanation: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
