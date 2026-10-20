"""
Domain model and evaluator for Production Rules in Classical AI.
Supports structured logical conditions: equality, inequality, comparisons, and list membership.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ConditionClause:
    field: str
    operator: str  # "==", "!=", ">", ">=", "<", "<=", "in", "contains", "is_not_none"
    value: Any


@dataclass
class ProductionRule:
    rule_id: str
    rule_name: str
    rule_type: str  # ROUTING, PRIORITY, ESCALATION, CONFLICT
    description: str
    conditions: List[ConditionClause]
    conclusion: Dict[str, Any]
    priority_order: int = 10  # Lower number = higher evaluation precedence
    is_active: bool = True

    def evaluate(self, facts: Dict[str, Any]) -> tuple[bool, Dict[str, Any], List[str]]:
        """
        Evaluates rule preconditions against current working facts.
        Returns:
            (is_matched, evaluated_conditions_map, missing_fields)
        """
        if not self.is_active:
            return False, {}, []

        matched = True
        evaluated_conditions = {}
        missing_fields = []

        for clause in self.conditions:
            field_name = clause.field
            op = clause.operator
            target_val = clause.value

            if field_name not in facts or facts[field_name] is None:
                # Field is missing. In classical reasoning, we DO NOT assume default 0 or False!
                missing_fields.append(field_name)
                evaluated_conditions[field_name] = f"MISSING (Required for condition '{field_name} {op} {target_val}')"
                matched = False
                continue

            actual_val = facts[field_name]
            clause_result = False

            try:
                if op == "==":
                    clause_result = (str(actual_val).lower() == str(target_val).lower()) if isinstance(target_val, str) else (actual_val == target_val)
                elif op == "!=":
                    clause_result = (str(actual_val).lower() != str(target_val).lower()) if isinstance(target_val, str) else (actual_val != target_val)
                elif op == ">":
                    clause_result = float(actual_val) > float(target_val)
                elif op == ">=":
                    clause_result = float(actual_val) >= float(target_val)
                elif op == "<":
                    clause_result = float(actual_val) < float(target_val)
                elif op == "<=":
                    clause_result = float(actual_val) <= float(target_val)
                elif op == "in":
                    clause_result = actual_val in target_val
                elif op == "is_not_none":
                    clause_result = actual_val is not None
                else:
                    clause_result = False
            except (ValueError, TypeError):
                clause_result = False

            evaluated_conditions[f"{field_name} {op} {target_val}"] = {
                "actual_value": actual_val,
                "satisfied": clause_result
            }

            if not clause_result:
                matched = False

        return matched, evaluated_conditions, missing_fields
