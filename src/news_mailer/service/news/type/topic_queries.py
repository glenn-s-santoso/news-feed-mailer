from pydantic import BaseModel


class TopicQueries(BaseModel):
    macroeconomy: str
    geopolitics: str
    stock_market: str
    cryptocurrency: str
    commodities: str
    technology: str
