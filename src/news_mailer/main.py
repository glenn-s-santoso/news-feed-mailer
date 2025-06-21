import argparse

from src.news_mailer.service.news import fetch_latest_news
from src.news_mailer.config.topic_loader import get_topics_for_run, all_topic_queries
from src.news_mailer.service.mail import EmailComposer, send_email_gmail
from src.news_mailer.utils import get_logger

logger = get_logger(__name__)


def run() -> None:
    """Orchestrate the pipeline: fetch news -> compose email -> send.

    Accepts optional ``--run-id`` CLI argument so GitHub Actions (or a user)
    can execute a subset of topics configured in ``topics.yaml``.
    """
    parser = argparse.ArgumentParser(description="news-mailer")
    parser.add_argument(
        "--run-id",
        default="all",
        help="Identifier of the configured run you want to execute (see topics.yaml). Use 'all' to fetch every topic.",
    )
    args = parser.parse_args()
    
    logger.info("Running with run_id: %s", args.run_id)

    try:
        if args.run_id == "all":
            topic_queries = all_topic_queries()
        else:
            topic_queries = get_topics_for_run(args.run_id)

        articles = fetch_latest_news(page_size_per_topic=5, topic_queries=topic_queries)
        if not articles:
            logger.warning("No articles fetched; aborting email send.")
            return

        composer = EmailComposer()
        subject, body = composer.compose_email(articles)

        # send_email_gmail(subject, body)
        with open(f"{args.run_id}.html", "w", encoding="utf-8") as fp:
            fp.write(body)
    except Exception as exc:
        logger.exception("Unhandled exception: %s", exc)
        raise

if __name__ == "__main__":
    run()
