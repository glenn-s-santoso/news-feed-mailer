from src.news_mailer.service.news import fetch_latest_news
from src.news_mailer.service.mail import EmailComposer, send_email_brevo
from src.news_mailer.utils import get_logger

logger = get_logger(__name__)


def run() -> None:
    """Orchestrate the pipeline: fetch news -> compose email -> send."""
    try:
        articles = fetch_latest_news(page_size_per_topic=5)
        if not articles:
            logger.warning("No articles fetched; aborting email send.")
            return

        composer = EmailComposer()
        subject, body = composer.compose_email(articles)

        send_email_brevo(subject, body)
    except Exception as exc:
        logger.exception("Unhandled exception: %s", exc)
        raise

if __name__ == "__main__":
    run()
