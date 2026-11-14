"""Multi-criteria supplier scoring (reliability, price, lead time)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.settings import get_settings


class SupplierRanking:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        default = {"reliability": 0.5, "price": 0.3, "lead_time": 0.2}
        self.weights = weights or get_settings().get("procurement.weights", default) or default

    @staticmethod
    def _normalize(value: float, low: float, high: float, invert: bool = False) -> float:
        if high == low:
            return 1.0
        score = (value - low) / (high - low)
        return 1.0 - score if invert else score

    def rank_suppliers(self, suppliers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return suppliers sorted best-first, each annotated with a 0-100 ``score``."""
        if not suppliers:
            return []
        prices = [float(s["price_index"]) for s in suppliers]
        leads = [int(s["average_lead_time"]) for s in suppliers]
        rels = [float(s["reliability_score"]) for s in suppliers]
        ranked = []
        for s in suppliers:
            components = {
                "reliability": self._normalize(float(s["reliability_score"]), min(rels), max(rels)),
                "price": self._normalize(float(s["price_index"]), min(prices), max(prices), invert=True),
                "lead_time": self._normalize(int(s["average_lead_time"]), min(leads), max(leads), invert=True),
            }
            score = sum(self.weights.get(k, 0) * v for k, v in components.items())
            ranked.append({**s, "score": round(score * 100, 1), "score_breakdown": components})
        ranked.sort(key=lambda x: (-x["score"], -float(x["reliability_score"]), float(x["price_index"])))
        return ranked
