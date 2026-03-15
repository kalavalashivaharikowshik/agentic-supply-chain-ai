import requests


class NewsAPI:

    def __init__(self):
        self.api_key = "d65d2dbec20d4f1c894d2e49c0229517"
        self.url = "https://newsapi.org/v2/everything"

    def get_supply_chain_news(self):

        params = {
            "q": "supply chain disruption OR port strike OR shipping delay",
            "language": "en",
            "apiKey": self.api_key
        }

        response = requests.get(self.url, params=params)

        if response.status_code == 200:
            return response.json()["articles"]
        else:
            return []