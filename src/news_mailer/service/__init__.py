"""Service layer packages (auth, mail, news)."""

from .auth import oauth
from .mail import email_composer, email_sender_gmail
from .news import news_fetcher

__all__ = ["oauth", "email_composer", "email_sender_gmail", "news_fetcher"]
