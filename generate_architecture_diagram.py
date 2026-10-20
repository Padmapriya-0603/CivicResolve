import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

def create_diagram(output_path):
    fig, ax = plt.subplots(figsize=(18, 11), dpi=220)
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # -------------------------------------------------------------
    # Helper: Draw stylized card
    # -------------------------------------------------------------
    def draw_card(x, y, w, h, bg_color, border_color, border_width=1.5, radius=1.2):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0,rounding_size={radius}",
            facecolor=bg_color,
            edgecolor=border_color,
            linewidth=border_width,
            zorder=2
        )
        ax.add_patch(box)
        return box

    # Helper: Draw pill badge
    def draw_badge(x, y, text, bg='#e2e8f0', fg='#334155', fontsize=8):
        ax.text(
            x, y, text,
            fontsize=fontsize, fontweight='bold', color=fg,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor=bg, edgecolor='none'),
            zorder=5
        )

    # -------------------------------------------------------------
    # TOP HEADER BANNER
    # -------------------------------------------------------------
    draw_card(3, 89, 94, 9, '#0f172a', '#1e293b', border_width=2, radius=1.5)
    
    # Title & Slogan
    ax.text(6, 94.7, "CivicResolve", fontsize=21, fontweight='black', color='#ffffff', zorder=5)
    ax.text(20.5, 94.9, "|  Enterprise System Architecture", fontsize=13, fontweight='medium', color='#94a3b8', zorder=5)
    ax.text(6, 91.2, "Smart Complaints. Clear Decisions. Better Governance  •  Deterministic Classical AI & 5-Stage Lifecycle Engine", 
            fontsize=9.5, fontweight='bold', color='#38bdf8', zorder=5)

    # Tech Badges on Header Right
    draw_badge(72, 93.5, 'FastAPI 0.110+', '#1e293b', '#38bdf8', fontsize=8.5)
    draw_badge(81.5, 93.5, 'React 18 + Vite', '#1e293b', '#67e8f9', fontsize=8.5)
    draw_badge(91, 93.5, 'Pure Python AI', '#1e293b', '#c084fc', fontsize=8.5)

    # -------------------------------------------------------------
    # TIER 1: CLIENT & PRESENTATION LAYER (Y: 69 to 87)
    # -------------------------------------------------------------
    draw_card(3, 69, 94, 18, '#ffffff', '#cbd5e1', border_width=1.5)
    # Section Label Tab
    draw_card(4, 83.8, 28, 3.2, '#1e3a8a', '#1e3a8a', radius=0.6)
    ax.text(5, 85.3, "TIER 1: PRESENTATION & CLIENT LAYER", fontsize=9, fontweight='bold', color='#ffffff', zorder=5)
    ax.text(33.5, 85.3, "Modern Single Page Application (SPA) • Role-Based Views • Reactive Dashboard", fontsize=8.5, color='#64748b', style='italic', zorder=5)

    # Sub-box 1: Citizen Portal
    draw_card(5, 70.5, 28, 12, '#eff6ff', '#bfdbfe')
    ax.text(7, 80, "Citizen Portal", fontsize=11, fontweight='bold', color='#1e3a8a', zorder=5)
    citizen_features = [
        "• Structured Grievance Submission Form",
        "• Real-Time CSP Conflict Warnings",
        "• 5-Stage Interactive Progress Tracker",
        "• Notification Center (In-App Badges)",
        "• 6-Digit Password Reset Workflow"
    ]
    for i, line in enumerate(citizen_features):
        ax.text(7, 77.5 - (i * 1.5), line, fontsize=8, color='#334155', zorder=5)

    # Sub-box 2: Officer Console
    draw_card(36, 70.5, 28, 12, '#f0fdf4', '#bbf7d0')
    ax.text(38, 80, "Department Officer Console", fontsize=11, fontweight='bold', color='#166534', zorder=5)
    officer_features = [
        "• Department-Scoped Work Queue",
        "• Sequential 5-Stage Transition Actions",
        "• Field Investigation Progress Notes",
        "• Resolution Verification & Completion",
        "• Performance & SLA Adherence Stats"
    ]
    for i, line in enumerate(officer_features):
        ax.text(38, 77.5 - (i * 1.5), line, fontsize=8, color='#334155', zorder=5)

    # Sub-box 3: Administrator Console
    draw_card(67, 70.5, 28, 12, '#fdf4ff', '#f5d0fe')
    ax.text(69, 80, "Municipal Admin Console", fontsize=11, fontweight='bold', color='#86198f', zorder=5)
    admin_features = [
        "• Full Grievance Registry & Life Cycle Control",
        "• Classical AI Recommendations & Override",
        "• Department Master & Capacity Config",
        "• User RBAC & Security Administration",
        "• Municipal Analytics & Tamper-Evident Logs"
    ]
    for i, line in enumerate(admin_features):
        ax.text(69, 77.5 - (i * 1.5), line, fontsize=8, color='#334155', zorder=5)

    # -------------------------------------------------------------
    # TIER 2: API GATEWAY & SECURITY LAYER (Y: 52 to 66)
    # -------------------------------------------------------------
    draw_card(3, 53, 94, 13.5, '#ffffff', '#cbd5e1', border_width=1.5)
    draw_card(4, 63.5, 28, 3, '#0284c7', '#0284c7', radius=0.6)
    ax.text(5, 65, "TIER 2: API GATEWAY & SECURITY LAYER", fontsize=9, fontweight='bold', color='#ffffff', zorder=5)
    ax.text(33.5, 65, "FastAPI Async Engine • Strict Authentication Boundary • Declarative Validation", fontsize=8.5, color='#64748b', style='italic', zorder=5)

    # Auth box
    draw_card(5, 54.5, 28, 8, '#f8fafc', '#e2e8f0')
    ax.text(7, 60.5, "Authentication & Crypto", fontsize=10, fontweight='bold', color='#0369a1', zorder=5)
    ax.text(7, 58.5, "• JWT Bearer Tokens (HS256)", fontsize=8, color='#475569', zorder=5)
    ax.text(7, 56.8, "• Salted Bcrypt Password Hashing", fontsize=8, color='#475569', zorder=5)
    ax.text(7, 55.1, "• Expiring OTP Reset Tokens", fontsize=8, color='#475569', zorder=5)

    # RBAC box
    draw_card(36, 54.5, 28, 8, '#f8fafc', '#e2e8f0')
    ax.text(38, 60.5, "Role-Based Access Control (RBAC)", fontsize=10, fontweight='bold', color='#0369a1', zorder=5)
    ax.text(38, 58.5, "• Granular Route Guards & Scopes", fontsize=8, color='#475569', zorder=5)
    ax.text(38, 56.8, "• Roles: CITIZEN | OFFICER | ADMIN", fontsize=8, color='#475569', zorder=5)
    ax.text(38, 55.1, "• Department Isolation & Privacy Enforcement", fontsize=8, color='#475569', zorder=5)

    # Validation box
    draw_card(67, 54.5, 28, 8, '#f8fafc', '#e2e8f0')
    ax.text(69, 60.5, "Data Integrity & Schema", fontsize=10, fontweight='bold', color='#0369a1', zorder=5)
    ax.text(69, 58.5, "• Pydantic v2 Type Enforcement", fontsize=8, color='#475569', zorder=5)
    ax.text(69, 56.8, "• CORS & Secure HTTP Headers", fontsize=8, color='#475569', zorder=5)
    ax.text(69, 55.1, "• Auto OpenAPI 3.0 Interactive Docs", fontsize=8, color='#475569', zorder=5)

    # -------------------------------------------------------------
    # TIER 3: DETERMINISTIC CLASSICAL AI ENGINE (Y: 33 to 50)
    # -------------------------------------------------------------
    draw_card(3, 34, 94, 16.5, '#ffffff', '#cbd5e1', border_width=1.5)
    draw_card(4, 47.5, 34, 3, '#6d28d9', '#6d28d9', radius=0.6)
    ax.text(5, 49, "TIER 3: DETERMINISTIC CLASSICAL AI CORE", fontsize=9, fontweight='bold', color='#ffffff', zorder=5)
    ax.text(39.5, 49, "Zero Black-Box LLMs • 100% Explainable • Formal Logic & Symbolic Reasoning", fontsize=8.5, color='#64748b', style='italic', zorder=5)

    # Sub-box: CSP
    draw_card(5, 35.5, 28, 11, '#faf5ff', '#e9d5ff')
    ax.text(7, 44.5, "Constraint Satisfaction (CSP)", fontsize=10.5, fontweight='bold', color='#6d28d9', zorder=5)
    csp_points = [
        "• Formal Triplet (V, D, C) Formulation",
        "• Finite Domains (Severity, Danger, Risk)",
        "• Domain Integrity & Inconsistency Check",
        "• Forward Checking & MRV Heuristics",
        "• Real-Time Citizen Form Feedback"
    ]
    for i, line in enumerate(csp_points):
        ax.text(7, 42.5 - (i * 1.4), line, fontsize=8, color='#334155', zorder=5)

    # Sub-box: Forward Chaining
    draw_card(36, 35.5, 28, 11, '#faf5ff', '#e9d5ff')
    ax.text(38, 44.5, "Forward Chaining Rule Engine", fontsize=10.5, fontweight='bold', color='#6d28d9', zorder=5)
    rule_points = [
        "• 28 Propositional Horn Clause Rules",
        "• Working Memory & Fact Propagation",
        "• Deterministic Department Routing",
        "• Priority Precedence Lattice: C > H > M > L",
        "• Finite Steps Termination Guarantee"
    ]
    for i, line in enumerate(rule_points):
        ax.text(38, 42.5 - (i * 1.4), line, fontsize=8, color='#334155', zorder=5)

    # Sub-box: Explainability & Audit
    draw_card(67, 35.5, 28, 11, '#faf5ff', '#e9d5ff')
    ax.text(69, 44.5, "Explainable Proof Generator", fontsize=10.5, fontweight='bold', color='#6d28d9', zorder=5)
    audit_points = [
        "• Monotonic Deduction Traces",
        "• Explicit Fired Rule IDs & Precedents",
        "• Admin AI Override Logging & Diff Tracking",
        "• Automated Escalation Flag Evaluation",
        "• 100% Verifiable Regulatory Compliance"
    ]
    for i, line in enumerate(audit_points):
        ax.text(69, 42.5 - (i * 1.4), line, fontsize=8, color='#334155', zorder=5)

    # -------------------------------------------------------------
    # TIER 4: 5-STAGE LIFECYCLE STATE MACHINE (Y: 19 to 31)
    # -------------------------------------------------------------
    draw_card(3, 20, 94, 11.5, '#ffffff', '#cbd5e1', border_width=1.5)
    draw_card(4, 28.5, 34, 3, '#047857', '#047857', radius=0.6)
    ax.text(5, 30, "TIER 4: 5-STAGE SEQUENTIAL STATE MACHINE", fontsize=9, fontweight='bold', color='#ffffff', zorder=5)
    ax.text(39.5, 30, "Finite State Automaton • Sequential Progress • Enforced Stage Jumps Prevention", fontsize=8.5, color='#64748b', style='italic', zorder=5)

    stages = [
        ("Stage 1", "SUBMITTED", "20% Progress", "Intake & AI Analysis", "#0284c7"),
        ("Stage 2", "ACKNOWLEDGED", "40% Progress", "Assigned & SLA Clock", "#2563eb"),
        ("Stage 3", "IN_PROGRESS", "60% Progress", "Field Remediation", "#d97706"),
        ("Stage 4", "RESOLVED", "80% Progress", "Remediation Complete", "#059669"),
        ("Stage 5", "CLOSED", "100% Progress", "Citizen Closed & Archived", "#15803d")
    ]

    for idx, (st_num, st_name, st_prog, st_desc, st_color) in enumerate(stages):
        sx = 5 + idx * 18.2
        draw_card(sx, 21.2, 16.5, 6.5, '#f8fafc', st_color, border_width=1.5)
        ax.text(sx + 8.25, 26.2, f"{st_num}: {st_name}", fontsize=8.5, fontweight='black', color=st_color, ha='center', zorder=5)
        ax.text(sx + 8.25, 24.3, st_prog, fontsize=8, fontweight='bold', color='#0f172a', ha='center', zorder=5)
        ax.text(sx + 8.25, 22.5, st_desc, fontsize=7.2, color='#64748b', ha='center', zorder=5)

        # Connector arrows between stages
        if idx < 4:
            ax.annotate(
                "", xy=(sx + 18, 24.45), xytext=(sx + 16.5, 24.45),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=2, mutation_scale=12),
                zorder=6
            )

    # -------------------------------------------------------------
    # TIER 5: PERSISTENCE, AUDIT & DATA LAYER (Y: 3 to 17)
    # -------------------------------------------------------------
    draw_card(3, 4, 94, 13.5, '#ffffff', '#cbd5e1', border_width=1.5)
    draw_card(4, 14.5, 34, 3, '#334155', '#334155', radius=0.6)
    ax.text(5, 16, "TIER 5: PERSISTENCE, AUDIT & STORAGE LAYER", fontsize=9, fontweight='bold', color='#ffffff', zorder=5)
    ax.text(39.5, 16, "Relational Persistence • SQLAlchemy ORM • WAL Mode • Realtime Dispatcher", fontsize=8.5, color='#64748b', style='italic', zorder=5)

    # Sub-box: Relational DB
    draw_card(5, 5.5, 28, 8, '#f8fafc', '#cbd5e1')
    ax.text(7, 11.5, "SQLite / Relational DB", fontsize=10, fontweight='bold', color='#1e293b', zorder=5)
    ax.text(7, 9.8, "• Users & Role Credentials", fontsize=8, color='#475569', zorder=5)
    ax.text(7, 8.2, "• Complaints (5-Stage Lifecycle)", fontsize=8, color='#475569', zorder=5)
    ax.text(7, 6.6, "• Department Taxonomy & SLAs", fontsize=8, color='#475569', zorder=5)

    # Sub-box: Audit Trail
    draw_card(36, 5.5, 28, 8, '#f8fafc', '#cbd5e1')
    ax.text(38, 11.5, "Immutable Audit Trail", fontsize=10, fontweight='bold', color='#1e293b', zorder=5)
    ax.text(38, 9.8, "• Append-Only Lifecycle Logs", fontsize=8, color='#475569', zorder=5)
    ax.text(38, 8.2, "• AI Routing & Override Records", fontsize=8, color='#475569', zorder=5)
    ax.text(38, 6.6, "• Actor ID & Precision Timestamps", fontsize=8, color='#475569', zorder=5)

    # Sub-box: Notification Dispatcher
    draw_card(67, 5.5, 28, 8, '#f8fafc', '#cbd5e1')
    ax.text(69, 11.5, "Events & Notifications", fontsize=10, fontweight='bold', color='#1e293b', zorder=5)
    ax.text(69, 9.8, "• Citizen In-App Notification Hub", fontsize=8, color='#475569', zorder=5)
    ax.text(69, 8.2, "• Reactive Stage Shift Alerts", fontsize=8, color='#475569', zorder=5)
    ax.text(69, 6.6, "• Automated SLA Escalations", fontsize=8, color='#475569', zorder=5)

    # -------------------------------------------------------------
    # VERTICAL CONNECTIONS & DATA FLOW ARROWS
    # -------------------------------------------------------------
    # Tier 1 -> Tier 2
    ax.annotate("", xy=(50, 66.5), xytext=(50, 69),
                arrowprops=dict(arrowstyle="<->", color="#2563eb", lw=2, mutation_scale=14), zorder=7)
    ax.text(50.8, 67.7, "HTTPS REST / JWT Bearer", fontsize=7.5, fontweight='bold', color='#2563eb', zorder=7)

    # Tier 2 -> Tier 3
    ax.annotate("", xy=(50, 50.5), xytext=(50, 53),
                arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=2, mutation_scale=14), zorder=7)
    ax.text(50.8, 51.7, "Grievance Evaluation & CSP Verify", fontsize=7.5, fontweight='bold', color='#7c3aed', zorder=7)

    # Tier 3 -> Tier 4
    ax.annotate("", xy=(50, 31.5), xytext=(50, 34),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=2, mutation_scale=14), zorder=7)
    ax.text(50.8, 32.7, "Initialize Stage 1 & Assign Dept", fontsize=7.5, fontweight='bold', color='#059669', zorder=7)

    # Tier 4 -> Tier 5
    ax.annotate("", xy=(50, 17.5), xytext=(50, 20),
                arrowprops=dict(arrowstyle="<->", color="#334155", lw=2, mutation_scale=14), zorder=7)
    ax.text(50.8, 18.7, "State Persistence & Audit Event Dispatch", fontsize=7.5, fontweight='bold', color='#334155', zorder=7)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=220, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Architecture diagram successfully saved to {output_path}")

if __name__ == "__main__":
    out1 = "d:/New folder/PublicGrievanceAI/architecture_diagram.png"
    out2 = "d:/New folder/PublicGrievanceAI/frontend/public/architecture_diagram.png"
    create_diagram(out1)
    create_diagram(out2)
