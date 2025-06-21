import requests
from typing import List, Dict, Mapping

from src.news_mailer.config.topic_loader import all_topic_queries

from src.news_mailer.config import get_settings
from src.news_mailer.utils import get_logger

logger = get_logger(__name__)

NEWS_API_EVERYTHING = "https://newsapi.org/v2/everything"

# Default fallback (used mainly for tests); in normal execution we rely on YAML
_DEFAULT_TOPIC_QUERIES = {
    "macroeconomy": "inflation OR GDP OR unemployment OR macroeconomy",
    "geopolitics": "geopolitics OR geopolitical risk OR foreign policy",
    "us_stock_market": "S&P 500 OR Dow Jones OR Nasdaq",
    "cryptocurrency": "cryptocurrency OR bitcoin OR ethereum",
    "global_stock_markets": "FTSE OR Nikkei OR DAX OR Hang Seng",
    "commodities": "oil OR gold OR copper OR commodity prices",
    "technology": "artificial intelligence OR generative AI OR open source AI OR blockchain technology",
}


def fetch_latest_news(
    *,
    page_size_per_topic: int = 3,
    language: str = "en",
    topic_queries: Mapping[str, str] | None = None,
) -> List[Dict]:
    """Fetch latest news across predefined topics.

    For each topic defined in ``topic_queries`` this function queries the
    NewsAPI *Everything* endpoint and grabs the ``page_size_per_topic`` most
    recent articles. Results are de-duplicated by URL and returned ordered by
    publication date (descending).

    Parameters
    ----------
    page_size_per_topic: int
        Maximum number of articles to fetch per topic.
    language: str
        ISO language code to filter NewsAPI results.
    topic_queries: Mapping[str, str] | None
        Mapping of topic name to query string. If ``None`` the configuration in
        ``topics.yaml`` is used (fallback to the in-file default when that is
        unavailable).
    """
    settings = get_settings()

    if topic_queries is None:
        try:
            topic_queries = all_topic_queries()
        except Exception:
            # Fallback if YAML cannot be read (e.g. during unit tests)
            topic_queries = _DEFAULT_TOPIC_QUERIES
    all_articles: list[Dict] = []

    headers = {"User-Agent": "news-mailer/1.0"}
    for topic, query in topic_queries.items():
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
