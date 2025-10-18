from __future__ import annotations

from typing import Sequence

import brevo_python
from brevo_python.rest import ApiException

from src.news_mailer.config import get_settings
from src.news_mailer.utils import get_logger

logger = get_logger(__name__)


def send_email_brevo(
    subject: str, body: str, to_addresses: Sequence[str] | None = None
) -> None:
    """Send an HTML email via the Brevo API.

    This function uses the Brevo Transactional Email API to send emails.
    The API key is resolved from the `BREVO_API_KEY` environment variable.
    The sender email is resolved from the `BREVO_EMAIL_PROVIDER` environment variable.

    If *to_addresses* is omitted the comma-separated `EMAIL_TO` addresses from settings are used.
    """
    settings = get_settings()

    # Get Brevo-specific settings
    brevo_api_key = settings.brevo_api_key
    brevo_sender_email = settings.brevo_email_provider

    if not brevo_api_key:
        raise RuntimeError(
            "BREVO_API_KEY is not set. Please provide it in your .env file."
        )

    if not brevo_sender_email:
        raise RuntimeError(
            "BREVO_EMAIL_PROVIDER is not set. Please provide it in your .env file."
        )

    # Configure API key authorization
    configuration = brevo_python.Configuration()
    configuration.api_key["api-key"] = brevo_api_key

    # Create an instance of the API class
    api_instance = brevo_python.TransactionalEmailsApi(
        brevo_python.ApiClient(configuration)
    )

    recipients = to_addresses or [addr.strip() for addr in settings.email_to.split(",")]

    logger.info("Sending Brevo API email to %s", recipients)

    # Create the email message
    send_smtp_email = brevo_python.SendSmtpEmail(
        sender={"email": brevo_sender_email},
        to=[{"email": email} for email in recipients],
        subject=subject,
        html_content=body,
        text_content=None,  # Optional: can add plain text version if needed
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info("Email sent via Brevo API. Message ID: %s", api_response.message_id)
    except ApiException as e:
        logger.error("Error sending email via Brevo API: %s", e)
        raise RuntimeError(f"Failed to send email via Brevo: {e}")
