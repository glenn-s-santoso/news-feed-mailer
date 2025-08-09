import json
from typing import Any
from dotenv import load_dotenv
from os import getenv

from src.news_mailer.service.news.type.topic_queries import TopicQueries
from src.news_mailer.utils import get_logger

load_dotenv()
logger = get_logger(__name__)

def try_or_return_default_topic_queries() -> dict[str, Any]:
    try:
        print(getenv("TOPIC_QUERIES"))
        return TopicQueries(**json.loads(getenv("TOPIC_QUERIES"))).model_dump()
    except Exception as exc:
        logger.warning("Failed to parse TOPIC_QUERIES: %s\n%s", exc, "Returning default queries.")
        return TopicQueries(
            macroeconomy="inflation OR GDP OR unemployment OR macroeconomy",
            geopolitics="geopolitics OR geopolitical risk OR foreign policy",
            stock_market="S&P 500 OR Dow Jones OR Nasdaq OR FTSE OR Nikkei OR DAX OR Hang Seng",
            cryptocurrency="cryptocurrency OR bitcoin OR ethereum",
            commodities="oil OR gold OR copper OR commodity prices",
            technology="artificial intelligence OR generative AI OR open source AI OR blockchain technology",
        ).model_dump()