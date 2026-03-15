from api_connectors.news_api import NewsAPI


class NewsSentiment:

    def analyze_news(self):

        news_api = NewsAPI()
        articles = news_api.get_supply_chain_news()

        risks = []

        for article in articles[:5]:

            title = article["title"].lower()

            if "strike" in title or "delay" in title or "port" in title:

                risks.append({
                    "event_type": "News Disruption",
                    "description": article["title"],
                    "severity_score": 70
                })

        return risks