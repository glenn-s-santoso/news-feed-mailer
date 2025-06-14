from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Sequence

from googleapiclient.discovery import build

from .config import get_settings
from .logger import get_logger
from .oauth import load_user_credentials

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def send_email_gmail(
    subject: str, body: str, to_addresses: Sequence[str] | None = None
) -> None:
    """Send email using Gmail API and a service account.

    The service account must be delegated to act on behalf of `gmail_delegated_user`.
    See Google Workspace docs for setting up domain-wide delegation.
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
