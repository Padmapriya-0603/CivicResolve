"""
Forward Chaining Inference Engine for Classical AI.
Executes an iterative data-driven deduction loop:
Initial Facts -> Rule Matching -> Conflict Resolution -> Assert Derived Facts -> Fixed-Point Termination.
Tracks complete execution trace, cycle count, and missing-information evaluation blocks.
"""

from typing import Dict, Any, List, Optional, Set
from models.rule import ProductionRule
from ai.facts import FactStore


class ReasoningStep:
    """Represents a single atomic deduction or audit event in the reasoning trace."""

    def __init__(
        self,
        step_order: int,
        step_type: str,
        rule_id: Optional[str] = None,
        rule_name: Optional[str] = None,
        conditions_evaluated: Optional[Dict[str, Any]] = None,
        derived_fact: Optional[Dict[str, Any]] = None,
        explanation: str = ""
    ):
        self.step_order = step_order
        self.step_type = step_type  # INPUT_FACT, RULE_MATCH, DERIVED_FACT, CONFLICT_RESOLUTION, ESCALATION, FINAL_DECISION
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.conditions_evaluated = conditions_evaluated or {}
        self.derived_fact = derived_fact or {}
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_order": self.step_order,
            "step_type": self.step_type,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "conditions_evaluated": self.conditions_evaluated,
            "derived_fact": self.derived_fact,
            "explanation": self.explanation
        }


class ForwardChainingEngine:
    """
    Classical production rule forward-chaining engine with fixed-point termination.
    Guaranteed deterministic and explainable.
    """

    def __init__(self, rules: List[ProductionRule], max_cycles: int = 50):
        self.rules = rules
        self.max_cycles = max_cycles

    def run(self, fact_store: FactStore) -> tuple[FactStore, List[ReasoningStep], List[str], List[Dict[str, Any]]]:
        """
        Executes the forward chaining cycle.
        Returns:
            (updated_fact_store, reasoning_trace, missing_evaluations, candidate_priorities)
        """
        trace: List[ReasoningStep] = []
        missing_evaluations: List[str] = []
        candidate_priorities: List[Dict[str, Any]] = []
        fired_rules: Set[str] = set()

        step_counter = 1

        # Step 1: Record Input Facts in trace
        trace.append(
            ReasoningStep(
                step_order=step_counter,
                step_type="INPUT_FACTS",
                explanation=f"Initialized working memory with ground facts: issue_type='{fact_store.get_fact('issue_type')}', category='{fact_store.get_fact('category')}', severity='{fact_store.get_fact('severity')}', safety_risk='{fact_store.get_fact('safety_risk')}'."
            )
        )
        step_counter += 1

        cycle = 0
        while cycle < self.max_cycles:
            cycle += 1
            facts_derived_in_cycle = 0

            # Scan all active rules sorted by rule priority
            sorted_rules = sorted(self.rules, key=lambda r: r.priority_order)

            for rule in sorted_rules:
                if rule.rule_id in fired_rules:
                    continue  # Each rule fires at most once in this monotonic deduction system

                matched, evaluated_conditions, missing_fields = rule.evaluate(fact_store.all_facts)

                # Record missing condition warnings if any field was absent
                for field in missing_fields:
                    note = f"Rule {rule.rule_id} ('{rule.rule_name}') cannot evaluate condition because '{field}' is missing."
                    if note not in missing_evaluations:
                        missing_evaluations.append(note)

                if matched:
                    # Fire rule!
                    fired_rules.add(rule.rule_id)
                    conclusions = rule.conclusion

                    # If this is a priority rule, register candidate priority for resolution
                    if rule.rule_type == "PRIORITY" and "priority" in conclusions:
                        candidate_priorities.append({
                            "rule_id": rule.rule_id,
                            "rule_name": rule.rule_name,
                            "priority": conclusions["priority"],
                            "description": rule.description
                        })

                    # Assert derived facts into working memory
                    for fact_k, fact_v in conclusions.items():
                        # If fact doesn't exist or is not priority (priority resolved through precedence)
                        if fact_k != "priority":
                            current_val = fact_store.get_fact(fact_k)
                            if current_val != fact_v:
                                fact_store.set_fact(fact_k, fact_v, is_derived=True)
                                facts_derived_in_cycle += 1

                    # Log Rule Firing in trace
                    trace.append(
                        ReasoningStep(
                            step_order=step_counter,
                            step_type="RULE_FIRE",
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            conditions_evaluated=evaluated_conditions,
                            derived_fact=conclusions,
                            explanation=f"Rule {rule.rule_id} ('{rule.rule_name}') preconditions satisfied. Derived: {conclusions}."
                        )
                    )
                    step_counter += 1

            # Termination condition: Fixed Point (no new facts asserted in this cycle)
            if facts_derived_in_cycle == 0:
                break

        return fact_store, trace, missing_evaluations, candidate_priorities
