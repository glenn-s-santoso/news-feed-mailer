from .news_fetcher import fetch_latest_news
from .email_composer import EmailComposer
from .email_sender_gmail import send_email_gmail
from .logger import get_logger

logger = get_logger(__name__)


def run() -> None:
    """Orchestrate the pipeline: fetch news -> compose email -> send."""
    try:
        articles = fetch_latest_news()
        if not articles:
            logger.warning("No articles fetched; aborting email send.")
            return

        composer = EmailComposer()
        subject, body = composer.compose_email(articles)

        send_email_gmail(subject, body)
    except Exception as exc:
        logger.exception("Unhandled exception: %s", exc)
        raise


if __name__ == "__main__":
    run()
