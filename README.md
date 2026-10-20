# AI-BASED PUBLIC GRIEVANCE ROUTING & REASONING SYSTEM
### Classical Deterministic Artificial Intelligence for Public Municipal Administration

> **Core System Assurance:**  
> *"The system provides deterministic and explainable grievance routing based on structured inputs, a predefined knowledge base, and a rule set. This system uses structured inputs and deterministic rule-based reasoning. It does not perform natural-language understanding."*

---

## 1. Project Title
**AI-Based Public Grievance Routing & Reasoning System**  
A full-stack, auditable civic grievance management platform powered by Classical Artificial Intelligence (Production Rules, Forward Chaining, Constraint Satisfaction, and Intelligent Agent architecture).

---

## 2. Problem Statement
Municipal governments receive thousands of citizen complaints daily regarding public lighting, broken roads, sanitation hazards, water contamination, and drainage issues. Conventional approaches either:
1. Rely on manual human sorting, resulting in administrative bottlenecks, delayed escalations for life-threatening emergencies, and biased routing; or
2. Attempt to use opaque, non-deterministic Machine Learning / LLM models that suffer from hallucinations, arbitrary classification probabilities, non-reproducible decisions, and lack of verifiable legal auditability.

---

## 3. Motivation
In public administration, every grievance disposition must be **accountable, deterministic, legally defensible, and 100% explainable**. When a public safety hazard is reported, citizens and municipal authorities need to know exactly which rule triggered an escalation, why a specific department was assigned, and how conflicting priorities were resolved—without statistical uncertainty or black-box predictions.

---

## 4. Objective
To build a complete, production-ready web application that:
- Ingests structured civic grievance data.
- Enforces strict Constraint Satisfaction Problem (CSP) domain validation.
- Employs data-driven forward chaining across a formalized knowledge base.
- Arbitrates rule and fact contradictions via formal precedence hierarchies.
- Produces a step-by-step verifiable reasoning trace.
- Tracks grievance lifecycles and permits auditable human-in-the-loop manual overrides without corrupting the original AI trace.

---

## 5. Proposed Solution
A decoupled full-stack architecture featuring:
- **Frontend:** Responsive React + Vite application providing structured categorical inputs, real-time CSP validation, interactive inference visualization, grievance lifecycle management, and knowledge base inspection.
- **Backend:** FastAPI REST service with Pydantic type contracts and SQLite persistence.
- **Classical AI Engine:** Pure Python inference engine executing forward chaining, conflict detection, priority lattice arbitration, and deterministic trace generation.

---

## 6. Features
- **Strict Structured Input Paradigm:** Dropdowns, discrete numbers, enums, and boolean flags preventing ambiguity.
- **CSP Domain Compatibility Verification:** Guarantees incompatible category-issue pairings (e.g., Water Supply + Streetlight outage) are caught and rejected prior to evaluation.
- **Data-Driven Forward Chaining:** Evaluates rule preconditions iteratively, asserting derived facts into working memory until reaching a fixed point.
- **Rule & Fact Conflict Resolution:** Explicit priority precedence ($\text{CRITICAL} \succ \text{HIGH} \succ \text{MEDIUM} \succ \text{LOW}$) arbitrates competing conclusions.
- **Zero-Guessing Policy for Missing Facts:** Explicitly registers missing variables rather than assuming default zeros or booleans.
- **Verifiable Reasoning Trace:** Visual step-by-step deduction path showing input facts, evaluated preconditions, fired rules, and asserted facts.
- **Manual Department Override:** Allows officers to override routing while strictly preserving the original AI decision and reasoning trace.
- **Evidence Management (No OCR / Vision):** Accepts supporting photos/PDFs as cataloged evidence without performing unverified computer vision.
- **Direct SQL Analytics:** Real-time KPIs calculated directly from SQLite tables.

---

## 7. System Architecture

```
Structured Citizen Form
         ↓
Input Fact Store (facts.py)
         ↓
CSP Constraint Validator (validators.py)
         ↓
Semantic Conflict Detector (conflict_detector.py)
         ↓
Knowledge Base & Production Rules (knowledge_base.py, rules.py)
         ↓
Forward Chaining Inference Engine (inference_engine.py)
         ↓
Derived Facts Pool (Department, Preliminary Facts)
         ↓
Priority Reasoning Engine (priority_engine.py - Precedence Resolution)
         ↓
Second-Order Escalation Chaining (Escalation Rules)
         ↓
Explanation & Trace Synthesizer (explanation_engine.py)
         ↓
Intelligent Grievance Agent (grievance_agent.py)
         ↓
Service & SQLite Persistence (complaint_service.py, database.py)
         ↓
FastAPI Endpoints (main.py)
         ↓
React + Vite Civic Portal (App.jsx, Dashboard, ReasoningTrace, etc.)
```

---

## 8. Technology Stack
- **AI Reasoning Engine:** Pure Python 3.12 (Custom Forward Chaining, Propositional Logic, Constraint Checking)
- **Backend Framework:** FastAPI, Pydantic v2, Uvicorn, Python-Multipart
- **Authentication & Security:** JWT (PyJWT), Bcrypt password hashing, RBAC route guards
- **Database:** SQLite3 (Relational persistence with foreign keys and ACID transactions)
- **Frontend Framework:** React 18, Vite 5, Axios (with JWT interceptors), Lucide React
- **Styling:** Modern, accessible, responsive CSS (civic theme, WCAG contrast compliance)
- **Test Suite:** Pytest, HTTPX (26 automated test cases)

---

## 9. Knowledge Representation
Grievances are converted from user inputs into an internal symbolic **Fact Store**:

```python
facts = {
    "citizen_name": "Priya Verma",
    "ward": "Ward 14 - North Zone",
    "location": "Main Road, Near Metro Junction",
    "category": "public_lighting",
    "issue_type": "streetlight_not_working",
    "duration_days": 5,
    "severity": "high",
    "affected_people": 80,
    "frequency": "frequent",
    "evidence_available": True,
    "evidence_filename": "evidence_streetlight.jpg",
    "safety_risk": "high",
    "public_accessibility_affected": False,
    "recurrence": True,
    "emergency": False
}
```

The Knowledge Base houses ontological definitions:
- **10 Municipal Departments** (ID, name, description, supported issue taxonomy, escalation authority).
- **12 Categories & 35+ Structured Issue Types**.
- **Precedence Lattices** for priority and escalation.

---

## 10. Rule-Based Reasoning
Rules are represented as first-class `ProductionRule` objects with condition clauses:

```python
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
```

Operators supported: `==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `is_not_none`.

---

## 11. Forward Chaining
The inference loop executes data-driven deduction:
1. Initialize working memory with ground facts $F_0$.
2. In each cycle $k$:
   - Scan active rules sorted by precedence.
   - Evaluate preconditions against $F_k$.
   - For all matching rules, fire rule and assert conclusion $C$ into $F_{k+1}$.
   - Log rule identifier, precondition values, and derived assertions into the reasoning trace.
3. Terminate when $F_{k+1} = F_k$ (Fixed-Point Convergence) or safe cycle threshold reached.
4. Guaranteed termination and monotonic reasoning.

---

## 12. Constraint Satisfaction (CSP)
Modeled as a formal CSP:
- **Variables:** $V = \{Category, IssueType, Duration, Affected, Severity, SafetyRisk, Emergency\}$
- **Domains:** Discrete taxonomies defined in the knowledge base.
- **Constraints:**
  - $IssueType \in Domain(Category)$
  - $Duration \ge 0, Affected \ge 0$
  - $Severity \in \{LOW, MEDIUM, HIGH, CRITICAL\}$
  - $SafetyRisk \in \{NONE, LOW, MEDIUM, HIGH, CRITICAL\}$
  - $DepartmentSupports(Department, IssueType) = True$

Violations cause immediate rejection with human-readable diagnostic messages.

---

## 13. Conflict Detection
Identifies contradictions at two layers:
1. **Fact Contradictions:**
   - `emergency = False` while `safety_risk = CRITICAL` $\rightarrow$ Evaluated as a safety divergence; priority elevated conservatively to CRITICAL.
   - `duration_days = 0` while `frequency = CONTINUOUS` $\rightarrow$ Flagged as temporal conflict.
2. **Rule Conclusion Conflicts:**
   - Multiple rules inferring competing priorities.

---

## 14. Priority Reasoning
Priority levels: **LOW, MEDIUM, HIGH, CRITICAL**.  
Determined via explicit production rules (PR001 - PR008):
- IF `safety_risk == CRITICAL` $\to$ `CRITICAL`
- IF `emergency == True` $\to$ `CRITICAL`
- IF `severity == HIGH` AND `affected_people > 50` $\to$ `HIGH`
- IF `frequency == CONTINUOUS` AND `duration_days >= 3` $\to$ `HIGH`
- IF `severity == MEDIUM` $\to$ `MEDIUM`
- IF `severity == LOW` $\to$ `LOW`

Competing conclusions are arbitrated by the formal lattice:
$$\text{CRITICAL (4)} \succ \text{HIGH (3)} \succ \text{MEDIUM (2)} \succ \text{LOW (1)}$$

---

## 15. Escalation Reasoning
Second-order production rules evaluate administrative urgency:
- **IMMEDIATE:** Fired when derived priority is `CRITICAL` or an emergency blocks public accessibility. Dispatches to 24/7 Rapid Action Force.
- **REQUIRED:** Fired when priority is `HIGH` with $\ge 3$ days duration, or high-severity recurrence occurs. Dispatched to Zonal Chief Engineer.
- **NO_ESCALATION:** Standard ward queue.

---

## 16. Explainability
Every narrative sentence in the output explanation maps directly to a recorded step in the inference trace:
- Which preconditions were evaluated against ground facts.
- Which specific production rules fired.
- What conflicts arose and what formal precedence arbitrated them.
- **Zero LLM synthesis, zero hallucinations.**

---

## 17. Intelligent Agent Model
Formally characterized using Russell & Norvig's PEAS framework:
- **Agent Type:** Goal-Based, Utility-Maximizing Deduction Agent
- **Environment:** Municipal Civic Administration System
- **Percepts:** Structured grievance input vectors
- **Internal State:** Knowledge Base, Working Memory Fact Store, Fired Rule Agenda, Precedence Lattice
- **Actions:** Assign Department, Establish Priority, Trigger Escalation, Document Audit Trace, Detect Contradictions
- **Goals:** Consistent, auditable, deterministic complaint routing
- **Performance Measure:** Precondition accuracy, constraint compliance, zero unsupported assumptions

---

## 18. Database Design
SQLite schema (`backend/grievances.db`):
- `departments`: department metadata, supported issue array, escalation authorities.
- `categories`: high-level grievance classifications.
- `issue_types`: specific issue taxonomies with foreign keys to categories.
- `rules`: serialized production rules, preconditions, conclusions, priority orders.
- `complaints`: complete record of citizen input facts, AI-derived outputs, manual override logs, and conflict metadata.
- `reasoning_traces`: step-by-step auditable execution log for each complaint.
- `status_history`: lifecycle state transition logs with timestamps and officer IDs.

---

## 19. API Documentation & RBAC Scopes

| Method | Endpoint | RBAC Role Required | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | Public | Citizen self-registration |
| `POST` | `/api/auth/login` | Public | Authenticates credentials and returns JWT token |
| `GET` | `/api/auth/me` | Authenticated | Returns current authenticated user session |
| `PUT` | `/api/auth/profile` | Authenticated | Updates citizen/officer profile (name, phone) |
| `GET` | `/api/health` | Public | System health check and classical AI confirmation |
| `POST` | `/api/complaints` | Citizen / Admin | Submits structured grievance and runs forward chaining |
| `GET` | `/api/complaints` | Authenticated | Lists complaints (**server-side scoped** by citizen/officer/admin) |
| `GET` | `/api/complaints/{id}` | Authenticated | Fetches full complaint, trace, and status history (scoped) |
| `PUT` | `/api/complaints/{id}/status` | Officer / Admin | Updates lifecycle status with audit remarks |
| `PUT` | `/api/admin/complaints/{id}/override` | Admin Only | Manually overrides department with reason while preserving AI trace |
| `GET` | `/api/complaints/{id}/reasoning` | Authenticated | Returns atomic inference steps of reasoning trace (scoped) |
| `POST` | `/api/validate-complaint` | Public | Validates CSP constraints dynamically |
| `GET` | `/api/dashboard` | Authenticated | Returns role-scoped SQL-aggregated grievance metrics |
| `GET` | `/api/departments` | Public | Lists all departments and capability matrices |
| `POST` | `/api/admin/departments` | Admin Only | Creates a new municipal department |
| `PUT` | `/api/admin/departments/{id}` | Admin Only | Updates department capabilities or soft deactivates |
| `GET` | `/api/admin/users` | Admin Only | Lists users with search, role, and department filters |
| `POST` | `/api/admin/users` | Admin Only | Creates new officer or administrator account |
| `PUT` | `/api/admin/users/{id}/role` | Admin Only | Changes user role and department (with safety checks) |
| `PUT` | `/api/admin/users/{id}/status` | Admin Only | Activates or deactivates user accounts |
| `GET` | `/api/admin/audit-logs` | Admin Only | Retrieves immutable security audit log |
| `GET` | `/api/categories` | Public | Lists all categories |
| `GET` | `/api/issue-types/{category}` | Public | Lists compatible issue types for a category |
| `GET` | `/api/rules` | Admin Only | Returns all active production rules |
| `PUT` | `/api/admin/rules/{id}/toggle` | Admin Only | Toggles rule active status with audit logging |
| `GET` | `/api/knowledge-base` | Admin Only | Returns complete symbolic knowledge base |
| `POST` | `/api/evidence-upload` | Authenticated | Uploads supporting files without OCR/vision |

---

## 20. Role-Based Access Control (RBAC) & Demo Credentials

The platform enforces strict server-side scoping and authorization across 3 roles:

### 1. CITIZEN (`CITIZEN`)
- Can submit structured public grievances.
- Can view **only their own** complaints and AI reasoning traces.
- Can view their profile and update personal contact info.
- **Forbidden:** Accessing other citizens' complaints, modifying complaint status, overriding departments, viewing internal user lists, modifying production rules, or accessing knowledge base management.

### 2. DEPARTMENT OFFICER (`DEPARTMENT_OFFICER`)
- Assigned to a specific municipal department (e.g. Public Lighting, Water Supply, Road Maintenance).
- Can view **only complaints assigned to their department**.
- Can transition operational lifecycle statuses (`Under Review`, `In Progress`, `Resolved`, `Rejected`, `Closed`) and record field remarks.
- Can view department-specific analytics and AI reasoning traces.
- **Forbidden:** Viewing complaints from other departments, performing manual department overrides, changing user roles, or editing production rules.

### 3. ADMINISTRATOR (`ADMIN`)
- Complete system-wide visibility over all municipal departments and complaints.
- Can perform **manual department overrides** with mandatory justification notes (strictly preserving original AI decisions and reasoning traces).
- Manages users: creates officers/admins, activates/deactivates accounts, reassigns departments, and changes roles (with safety checks preventing removal of the last admin).
- Manages departments: creates departments, modifies supported issues, and performs soft deactivations.
- Manages rule base: inspects production rules, toggles active rules, and inspects the symbolic knowledge base.
- Inspects system audit logs.

### 🔑 Configured Accounts

| Role | Name | Email | Password | Scope & Authority |
|---|---|---|---|---|
| **Citizen** | `priya` | `priya@gmail.com` | `123456` | Citizen portal, submit complaints, view own history |
| **Administrator** | `Administrator` | `admin@gmail.com` | `123456` | Full administrative control, user & department management, rule base, manual overrides |
| **Administrator (alt)** | `Administrator` | `admin@grievance.local` | `123456` | Alternative admin login |

*All demo accounts and pre-filled complaints have been removed. The system starts with an empty complaints registry ready for live submissions.*

```
PublicGrievanceAI/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── database.py
│   ├── seed_data.py
│   │
│   ├── models/
│   │   ├── complaint.py
│   │   ├── rule.py
│   │   └── schemas.py
│   │
│   ├── ai/
│   │   ├── knowledge_base.py
│   │   ├── facts.py
│   │   ├── rules.py
│   │   ├── inference_engine.py
│   │   ├── priority_engine.py
│   │   ├── conflict_detector.py
│   │   ├── explanation_engine.py
│   │   └── grievance_agent.py
│   │
│   ├── services/
│   │   ├── complaint_service.py
│   │   └── dashboard_service.py
│   │
│   ├── utils/
│   │   └── validators.py
│   │
│   └── tests/
│       └── test_ai_engine.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   │
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── App.css
│       │
│       ├── components/
│       │   ├── Dashboard.jsx
│       │   ├── ComplaintForm.jsx
│       │   ├── ComplaintResult.jsx
│       │   ├── ReasoningTrace.jsx
│       │   ├── ComplaintHistory.jsx
│       │   ├── ComplaintDetails.jsx
│       │   ├── RuleViewer.jsx
│       │   ├── KnowledgeBaseViewer.jsx
│       │   ├── ConflictPanel.jsx
│       │   ├── Statistics.jsx
│       │   └── DepartmentStatus.jsx
│       │
│       └── services/
│           └── api.js
│
└── README.md
```

---

## 21. Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

---

## 22. Backend Setup

```bash
cd backend
python -m venv venv

# Windows Activation:
venv\Scripts\activate

# Linux/macOS Activation:
# source venv/bin/activate

pip install -r requirements.txt
python seed_data.py
```

---

## 23. Frontend Setup

```bash
cd frontend
npm install
```

---

## 24. Running the Project

### Start Backend Service
```bash
cd backend
uvicorn main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### Start Frontend Application
```bash
cd frontend
npm run dev
```
Civic Portal will be available at `http://localhost:5173`.

---

## 25. Testing
The test suite validates both Classical AI Reasoning and complete Role-Based Access Control:

```bash
cd backend
# 1. Run AI Engine Deterministic Tests (10 tests)
pytest tests/test_ai_engine.py -v

# 2. Run Role-Based Access Control & Security Tests (16 tests)
pytest tests/test_rbac.py -v

# Run all 26 automated tests:
pytest
```

All 26 tests run and pass deterministically:
- **Classical AI Reasoning Engine (10/10):**
  1. `test_1_streetlight_high_priority`
  2. `test_2_safety_risk_critical`
  3. `test_3_missing_affected_people`
  4. `test_4_invalid_category_issue_csp`
  5. `test_5_conflicting_rules_precedence`
  6. `test_6_emergency_immediate_escalation`
  7. `test_7_deterministic_reproducibility`
  8. `test_8_different_issue_different_routing`
  9. `test_9_negative_duration_validation`
  10. `test_10_missing_required_facts_blocks_unsupported_decision`
- **Role-Based Access Control & Security (16/16):**
  1. `test_citizen_registration_and_login`
  2. `test_login_invalid_credentials_rejected`
  3. `test_citizen_can_submit_complaint`
  4. `test_officer_cannot_submit_complaint`
  5. `test_citizen_sees_only_own_complaints`
  6. `test_officer_sees_only_department_complaints`
  7. `test_officer_cannot_access_other_department_complaint_by_id`
  8. `test_admin_sees_all_complaints`
  9. `test_officer_can_update_status_in_own_department`
  10. `test_officer_cannot_update_status_in_other_department`
  11. `test_citizen_cannot_update_status`
  12. `test_admin_can_override_department_and_preserves_original_ai_decision`
  13. `test_officer_and_citizen_cannot_override_department`
  14. `test_admin_user_management_and_last_admin_protection`
  15. `test_admin_department_management`
  16. `test_audit_log_records_security_events`

---

## 26. Example Input (Demonstration Scenario)

- **Category:** Public Lighting
- **Issue Type:** Streetlight Not Working
- **Severity:** HIGH
- **Duration (Days):** 5
- **Affected People:** 80
- **Frequency:** FREQUENT
- **Safety Risk:** HIGH
- **Evidence Available:** True
- **Recurrence:** True
- **Emergency:** False

---

## 27. Example Reasoning Trace (Output)

```
STEP 1: [INPUT_FACTS] Initialized working memory with ground facts:
        issue_type='streetlight_not_working', severity='high', affected_people=80, safety_risk='high'.

STEP 2: [RULE_FIRE] Rule R001 ('Streetlight Routing') satisfied:
        Condition: issue_type == 'streetlight_not_working' -> TRUE
        ↳ Inferred Fact: {'department': 'Public Lighting'}

STEP 3: [RULE_FIRE] Rule PR003 ('High Severity with Large Population Impact') satisfied:
        Condition: severity == 'high' -> TRUE
        Condition: affected_people > 50 -> TRUE (80 > 50)
        ↳ Inferred Fact: {'priority': 'HIGH'}

STEP 4: [RULE_FIRE] Rule PR005 ('High Safety Risk Priority') satisfied:
        Condition: safety_risk == 'high' -> TRUE
        ↳ Inferred Fact: {'priority': 'HIGH'}

STEP 5: [PRIORITY_ARBITRATION] Priority established as 'HIGH' via unanimous rule agreement.

STEP 6: [RULE_FIRE] Rule ER002 ('Prolonged High Priority Escalation') satisfied:
        Condition: priority == 'HIGH' -> TRUE
        Condition: duration_days >= 3 -> TRUE (5 >= 3)
        ↳ Inferred Fact: {'escalation': 'REQUIRED'}

STEP 7: [FINAL_DECISION]
        • Assigned Department: Public Lighting
        • Priority: HIGH
        • Escalation Status: REQUIRED
```

---

## 28. Limitations
- **No Natural Language Free-Text Processing:** Requires structured inputs (dropdowns, selectors, numbers). Free-text narratives are not parsed.
- **Closed-World Assumption:** The system only reasons about known categories, issues, and rules contained in the knowledge base. Unregistered issue types must be handled through manual officer review.
- **Rule Base Completeness Dependent:** If no production rule exists for a rare condition, the agent declines to guess and refers the complaint for human review.

---

## 29. Future Enhancements
- **Spatial GIS Topology Reasoning:** Integrating GIS coordinates to evaluate clustered grievances geographically through spatial inference rules.
- **Dynamic Rule Authoring Interface:** Web interface for authorized commissioners to submit new rules with automatic consistency and non-contradiction verification.
- **Citizen SMS / Webhook Gateway:** Real-time push updates triggered on status history updates.

---

## 30. AI Syllabus Mapping

### Unit I: Intelligent Agents
- Models a goal-driven agent with well-defined PEAS parameters operating in an accessible, deterministic, static, discrete civic environment.

### Unit II: Search
- Search is deliberately not faked or artificially forced here. Fact retrieval uses indexed knowledge lookup ($O(1)$) and forward chaining rule evaluation cycles rather than state-space graph search (e.g. $A^*$ / BFS), because grievance routing is a deductive inference problem rather than a pathfinding problem.

### Unit III: Constraint Satisfaction Problems (CSP)
- Formulates category-issue taxonomies and validity bounds as consistency constraints. Incompatible domain pairings are filtered using arc-consistency style validation.

### Unit IV: Knowledge Representation and Reasoning
- Explicit ground facts, production rules, monotonic working memory, forward chaining algorithm, precedence lattices, and auditable reasoning traces.
