"""Human-readable explanations for agent decisions, derived from the data."""

from __future__ import annotations

from statistics import mean
from typing import Any, Dict, List, Optional


class DecisionExplainer:
    def supplier_reasons(self, supplier: Dict[str, Any], alternatives: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        alternatives = alternatives or []
        reasons: List[str] = []
        rel = float(supplier["reliability_score"])
        price = float(supplier["price_index"])
        lead = int(supplier["average_lead_time"])
        if "score" in supplier:
            reasons.append(f"Overall score {supplier['score']}/100 (weighted reliability, price, lead time)")
        if not alternatives:
            reasons.append(f"Only qualified supplier: reliability {rel:.0%}, price {price:,.2f}, lead time {lead} days")
            return reasons

        avg_rel = mean(float(a["reliability_score"]) for a in alternatives)
        avg_price = mean(float(a["price_index"]) for a in alternatives)
        avg_lead = mean(int(a["average_lead_time"]) for a in alternatives)

        diff_rel = (rel - avg_rel) * 100
        reasons.append(f"Reliability {rel:.0%} ({diff_rel:+.1f} pts vs alternatives)")
        diff_price = (price - avg_price) / avg_price * 100 if avg_price else 0
        reasons.append(f"Unit price {price:,.2f} ({diff_price:+.1f}% vs alternatives' average)")
        diff_lead = lead - avg_lead
        reasons.append(f"Lead time {lead} days ({diff_lead:+.1f} days vs alternatives)")
        if supplier.get("at_risk_location"):
            reasons.append(f"⚠ Note: an active high risk exists in {supplier['country']}")
        else:
            risky = [a["supplier_name"] for a in alternatives if a.get("at_risk_location")]
            if risky:
                reasons.append(f"Avoided suppliers in high-risk locations: {', '.join(risky[:3])}")
        return reasons

    def explain_supplier_choice(self, supplier: Dict[str, Any], alternatives: Optional[List[Dict[str, Any]]] = None) -> str:
        lines = [f"Recommended Supplier: {supplier['supplier_name']} ({supplier.get('country', '')})", "", "Reasons:"]
        lines += [f"• {r}" for r in self.supplier_reasons(supplier, alternatives)]
        return "\n".join(lines)
