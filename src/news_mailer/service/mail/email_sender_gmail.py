from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Sequence

from googleapiclient.discovery import build

from src.news_mailer.config import get_settings
from src.news_mailer.utils import get_logger
from src.news_mailer.service.auth import load_user_credentials

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def send_email_gmail(
    subject: str, body: str, to_addresses: Sequence[str] | None = None
) -> None:
    """Send an HTML email via the Gmail API.

    Credentials are resolved by :func:`load_user_credentials`, which supports two flows:
    1. **User OAuth installed-app flow** – uses the `client_secrets.json` / `token.json` files or
       the `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` environment
       variables.
    2. **Service-account with domain-wide delegation** – enabled by setting
       `GMAIL_SERVICE_ACCOUNT_FILE` and `GMAIL_DELEGATED_USER` in the environment.

    If *to_addresses* is omitted the comma-separated `EMAIL_TO` addresses from settings are used.
    """
    settings = get_settings()
    creds = load_user_credentials()

    if creds is None:
        raise RuntimeError(
            "No Gmail credentials available. Provide service-account vars in .env or client_secrets.json for user OAuth."
        )

    service = build("gmail", "v1", credentials=creds)

    recipients = to_addresses or [addr.strip() for addr in settings.email_to.split(",")]

    logger.info("Sending Gmail API email to %s", recipients)

    message = EmailMessage()
    message["From"] = settings.email_from
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body, subtype="html")

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_request = {
        "raw": encoded_message,
    }

    service.users().messages().send(userId="me", body=send_request).execute()
    logger.info("Email sent via Gmail API")
