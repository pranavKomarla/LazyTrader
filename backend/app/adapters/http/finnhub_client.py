import finnhub

from app.core.config import config
FINNHUB_API_KEY = config.FINNHUB_API_KEY

class FinnhubClient:
    def __init__(self):
        self.api_key = FINNHUB_API_KEY

    def get_news(self):
        pass

    def get_company_news(self, symbol: str):
        pass