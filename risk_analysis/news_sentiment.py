"""Keyword-weighted risk extraction from supply chain news headlines."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from api_connectors.news_api import NewsAPI
from app.settings import get_settings
from risk_analysis.risk_scorer import RiskScorer

# keyword -> severity contribution
RISK_KEYWORDS = {
    "strike": 30,
    "closure": 30,
    "closed": 25,
    "shutdown": 30,
    "blockade": 35,
    "attack": 35,
    "typhoon": 30,
    "hurricane": 30,
    "earthquake": 35,
    "flood": 25,
    "fire": 20,
    "shortage": 25,
    "congestion": 20,
    "delay": 15,
    "disruption": 15,
    "sanction": 20,
    "tariff": 10,
    "port": 5,
}

COUNTRIES = ["China", "Taiwan", "South Korea", "Japan", "India", "Vietnam", "Germany", "Sweden",
             "Netherlands", "Singapore", "United States", "Red Sea", "Suez", "Panama"]


class NewsSentiment:
    def __init__(self, api: Optional[NewsAPI] = None):
        self.api = api or NewsAPI()
        self.scorer = RiskScorer()

    def score_headline(self, text: str) -> int:
        text = text.lower()
        score = sum(weight for kw, weight in RISK_KEYWORDS.items() if kw in text)
        return min(100, score)

    def extract_location(self, text: str) -> str:
        lowered = text.lower()
        for port in get_settings().ports:
            city = port["name"].replace(" Port", "").lower()
            if city in lowered:
                return port["name"]
        for country in COUNTRIES:
            if country.lower() in lowered:
                return country
        return "Global"

    def analyze_articles(self, articles: List[Dict[str, Any]], min_score: int = 30) -> List[Dict[str, Any]]:
        risks = []
        for article in articles:
            title = article.get("title") or ""
            text = f"{title} {article.get('description') or ''}"
            score = self.score_headline(text)
            if score >= min_score:
                risks.append({
                    "event_type": "News Disruption",
                    "location": self.extract_location(text),
                    "severity_score": score,
                    "risk_level": self.scorer.calculate_risk(score),
                    "description": title[:500],
                })
        return risks

    def analyze_news(self) -> List[Dict[str, Any]]:
        return self.analyze_articles(self.api.get_supply_chain_news())
