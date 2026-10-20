"""
Intelligent Grievance Routing Agent (Classical AI Agent Architecture).
Formally models the agent with:
- Environment: Public Municipal Administration
- Percepts: Structured citizen grievance attributes
- Internal State: Knowledge Base, Working Memory, Fired Rules, Conflict Registry
- Actions: ROUTE, PRIORITIZE, ESCALATE, CONFLICT_FLAG, EXPLAIN
- Goal: Deterministic, explainable, constraint-satisfying grievance disposition
- Performance Metrics: Constraint satisfaction rate, deductive auditability, zero hallucinations
"""

from typing import Dict, Any, List, Optional
from models.schemas import ComplaintCreateRequest
from models.rule import ProductionRule
from ai.facts import extract_facts_from_request, FactStore
from ai.knowledge_base import KnowledgeBase, kb_instance
from ai.rules import get_default_rules
from ai.inference_engine import ForwardChainingEngine, ReasoningStep
from ai.priority_engine import PriorityEngine
from ai.conflict_detector import ConflictDetector
from ai.explanation_engine import ExplanationEngine


class GrievanceAgent:
    """
    Classical Intelligent Agent coordinating perceptual analysis,
    forward chaining deduction, constraint satisfaction, and explanation.
    """

    def __init__(self, kb: Optional[KnowledgeBase] = None, rules: Optional[List[ProductionRule]] = None):
        self.kb = kb or kb_instance
        self.rules = rules or get_default_rules()
        self.conflict_detector = ConflictDetector()
        self.priority_engine = PriorityEngine()
        self.explanation_engine = ExplanationEngine()

    def process_grievance(self, request: ComplaintCreateRequest) -> Dict[str, Any]:
        """
        Agent Cycle:
        1. Receive Percept (Structured Request)
        2. Formulate Ground Facts
        3. Check Fact Conflicts & Domain Constraints
        4. Forward Chaining Deduction Loop
        5. Priority Arbitration & Conflict Precedence
        6. Second-order Escalation Chaining
        7. Generate Deductive Explanation & Trace
        8. Return Actionable Decision
        """
        # Step 1 & 2: Percept to Working Memory Facts
        fact_store: FactStore = extract_facts_from_request(request)
        initial_ground_facts = fact_store.all_facts

        # Step 3: Conflict & Contradiction Detection
        detected_conflicts = self.conflict_detector.detect_fact_conflicts(initial_ground_facts)

        # Check for blocking conflicts (e.g. invalid category/issue domain pairing or Danger=YES with Severity=LOW)
        blocking_conflicts = [c for c in detected_conflicts if c.get("is_blocking")]
        if blocking_conflicts:
            conflict_msg = (
                "Validation Conflict: Immediate Danger is marked Yes, but the selected severity is Low, "
                "which violates the defined constraint. The AI recommendation has been paused and the complaint "
                "requires administrative review."
                if any("severity=LOW" in c.get("conflicting_elements", []) for c in blocking_conflicts)
                else f"Validation Conflict: {blocking_conflicts[0]['description']} The AI recommendation has been paused and the complaint requires administrative review."
            )
            return {
                "success": False,
                "error": conflict_msg,
                "explanation": conflict_msg,
                "conflicts": detected_conflicts,
                "missing_info": []
            }

        # Step 4: Forward Chaining Inference Loop (Routing & Preliminary Facts)
        engine = ForwardChainingEngine(self.rules)
        fact_store, trace, missing_evaluations, candidate_priorities = engine.run(fact_store)

        # Step 5: Priority Engine (Arbitrates multiple priority rules via formal precedence)
        resolved_priority, priority_conflict = self.priority_engine.resolve_priority(candidate_priorities)
        if priority_conflict:
            detected_conflicts.append(priority_conflict)

        # Assert resolved priority into fact store
        fact_store.set_fact("priority", resolved_priority, is_derived=True)

        # Record priority arbitration in trace
        trace.append(
            ReasoningStep(
                step_order=len(trace) + 1,
                step_type="PRIORITY_ARBITRATION",
                derived_fact={"priority": resolved_priority},
                explanation=(
                    f"Priority established as '{resolved_priority}'. " +
                    (priority_conflict["resolution"] if priority_conflict else "Derived from rule match without conflict.")
                )
            )
        )

        # Step 6: Second-order Forward Chaining for Escalation (using newly derived priority)
        # Evaluate escalation rules that depend on the final resolved priority
        escalation_rules = [r for r in self.rules if r.rule_type == "ESCALATION"]
        resolved_escalation = "NO_ESCALATION"

        sorted_escalation_rules = sorted(escalation_rules, key=lambda r: r.priority_order)
        for er in sorted_escalation_rules:
            matched, cond_eval, _ = er.evaluate(fact_store.all_facts)
            if matched:
                resolved_escalation = er.conclusion.get("escalation", "NO_ESCALATION")
                fact_store.set_fact("escalation", resolved_escalation, is_derived=True)
                trace.append(
                    ReasoningStep(
                        step_order=len(trace) + 1,
                        step_type="RULE_FIRE",
                        rule_id=er.rule_id,
                        rule_name=er.rule_name,
                        conditions_evaluated=cond_eval,
                        derived_fact=er.conclusion,
                        explanation=f"Escalation Rule {er.rule_id} ('{er.rule_name}') satisfied. Derived escalation: '{resolved_escalation}'."
                    )
                )
                break  # Fired highest precedence escalation rule

        # Determine responsible department from derived facts or KB fallback
        derived_dept = fact_store.get_fact("department")

        if not derived_dept:
            # Fallback lookup in KB capability table
            kb_dept = self.kb.find_department_for_issue(request.issue_type)
            if kb_dept:
                derived_dept = kb_dept["name"]
                fact_store.set_fact("department", derived_dept, is_derived=True)
                trace.append(
                    ReasoningStep(
                        step_order=len(trace) + 1,
                        step_type="KB_LOOKUP",
                        derived_fact={"department": derived_dept},
                        explanation=f"Department '{derived_dept}' identified via Knowledge Base capability table for issue '{request.issue_type}'."
                    )
                )

        if not derived_dept:
            derived_dept = None
            routing_explanation = "Unable to determine responsible department. No configured rule matches. Manual review required."
        else:
            routing_explanation = f"Department '{derived_dept}' assigned deterministically."

        # Final decision step in trace
        trace.append(
            ReasoningStep(
                step_order=len(trace) + 1,
                step_type="FINAL_DECISION",
                derived_fact={
                    "department": derived_dept,
                    "priority": resolved_priority,
                    "escalation": resolved_escalation
                },
                explanation=f"Final disposition formulated: Department='{derived_dept or 'UNASSIGNED'}', Priority='{resolved_priority}', Escalation='{resolved_escalation}'."
            )
        )

        # Step 7: Synthesize Explanation
        explanation_narrative = self.explanation_engine.build_narrative_explanation(
            ground_facts=initial_ground_facts,
            trace=trace,
            selected_department=derived_dept,
            selected_priority=resolved_priority,
            selected_escalation=resolved_escalation,
            priority_conflict=priority_conflict,
            missing_info=missing_evaluations
        )

        return {
            "success": True,
            "department": derived_dept,
            "priority": resolved_priority,
            "escalation": resolved_escalation,
            "conflicts": detected_conflicts,
            "missing_info": missing_evaluations,
            "reasoning_trace": [step.to_dict() for step in trace],
            "explanation": explanation_narrative
        }
