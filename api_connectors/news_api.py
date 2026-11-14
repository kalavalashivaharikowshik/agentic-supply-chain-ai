"""NewsAPI.org client. Requires NEWS_API_KEY in the environment."""

from __future__ import annotations

from typing import Any, Dict, List

import requests

from app.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class NewsAPI:
    url = "https://newsapi.org/v2/everything"
    query = '"supply chain" OR "port strike" OR "shipping delay" OR "port congestion" OR "chip shortage"'

    def __init__(self, timeout: float = 8.0):
        settings = get_settings()
        self.api_key = settings.news_api_key
        self.enabled = settings.enable_external_apis and bool(self.api_key)
        self.timeout = timeout

    def get_supply_chain_news(self, page_size: int = 20) -> List[Dict[str, Any]]:
        if not self.enabled:
            logger.info("News API disabled (set NEWS_API_KEY to enable)")
            return []
        params = {
            "q": self.query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
        }
        try:
            response = requests.get(self.url, params=params, headers={"X-Api-Key": self.api_key}, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("articles", [])
        except (requests.RequestException, ValueError) as exc:
            logger.warning("News API unavailable: %s", exc)
            return []
