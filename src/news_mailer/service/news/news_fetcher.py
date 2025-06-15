import requests
from typing import List, Dict

from src.news_mailer.config import get_settings
from src.news_mailer.utils import get_logger

logger = get_logger(__name__)

NEWS_API_EVERYTHING = "https://newsapi.org/v2/everything"

TOPIC_QUERIES = {
    "macroeconomy": "inflation OR GDP OR unemployment OR macroeconomy",
    "geopolitics": "geopolitics OR geopolitical risk OR foreign policy",
    "us_stock_market": "S&P 500 OR Dow Jones OR Nasdaq",
    "cryptocurrency": "cryptocurrency OR bitcoin OR ethereum",
    "global_stock_markets": "FTSE OR Nikkei OR DAX OR Hang Seng",
    "commodities": "oil OR gold OR copper OR commodity prices",
    "technology": "artificial intelligence OR generative AI OR open source AI OR blockchain technology",
}


def fetch_latest_news(page_size_per_topic: int = 3, language: str = "en") -> List[Dict]:
    """Fetch latest news across predefined topics.

    For each topic defined in ``TOPIC_QUERIES`` this function queries the
    NewsAPI *Everything* endpoint and grabs the ``page_size_per_topic`` most
    recent articles. Results are de-duplicated by URL and returned ordered by
    publication date (descending).
    """
    settings = get_settings()
    all_articles: list[Dict] = []

    headers = {"User-Agent": "news-mailer/1.0"}
    for topic, query in TOPIC_QUERIES.items():
        params = {
            "q": query,
            "language": language,
            "sortBy": "publishedAt",
            "pageSize": page_size_per_topic,
            "apiKey": settings.news_api_key,
        }
        logger.info("Fetching topic '%s'", topic)
        try:
            resp = requests.get(
                NEWS_API_EVERYTHING, params=params, headers=headers, timeout=10
            )
            resp.raise_for_status()
            for art in resp.json().get("articles", []):
                all_articles.append(art)
        except Exception as exc:
            logger.warning("Topic '%s' fetch failed: %s", topic, exc)

    seen = {}
    for art in sorted(
        all_articles, key=lambda a: a.get("publishedAt", ""), reverse=True
    ):
        url = art.get("url")
        if url and url not in seen:
            seen[url] = art

    return list(seen.values())
