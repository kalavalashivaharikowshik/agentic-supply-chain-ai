"""Resolves conflicts between stock urgency, cost and risk.

Priority (highest first):
1. Critical stock within budget        -> URGENT_PROCUREMENT
2. Critical stock but over budget      -> ESCALATE (needs human approval)
3. Cost over budget (non-urgent)       -> REJECT_COST
4. Critical risk                       -> RISK_MITIGATION
5. Otherwise                           -> NORMAL_OPERATION
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from conflict_resolver.business_rules import BusinessRules


class RuleEngine:
    def evaluate_detailed(self, stock_days: Optional[float], cost: float, risk_level: str,
                          budget_available: Optional[float] = None) -> Dict[str, Any]:
        rules = BusinessRules().get_rules()
        budget = rules["max_budget"] if budget_available is None else budget_available
        reasons: List[str] = []
        critical_stock = stock_days is not None and stock_days <= rules["critical_stock_days"]
        over_budget = cost > budget

        if critical_stock and not over_budget:
            decision = "URGENT_PROCUREMENT"
            reasons.append(f"stock covers {stock_days} days (critical ≤ {rules['critical_stock_days']})")
        elif critical_stock and over_budget:
            decision = "ESCALATE"
            reasons.append("stock is critical but the order exceeds the available budget")
        elif over_budget:
            decision = "REJECT_COST"
            reasons.append(f"cost {cost:,.0f} exceeds budget {budget:,.0f}")
        elif risk_level == "CRITICAL" and rules["high_risk_priority"]:
            decision = "RISK_MITIGATION"
            reasons.append("critical supply risk is active")
        else:
            decision = "NORMAL_OPERATION"
            reasons.append("no rule triggered")
        return {"decision": decision, "reasons": reasons}

    def evaluate(self, stock_days, cost, risk_level, budget_available=None) -> str:
        return self.evaluate_detailed(stock_days, cost, risk_level, budget_available)["decision"]
