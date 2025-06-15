"""Mail service."""

from .email_composer import EmailComposer
from .email_sender_gmail import send_email_gmail

__all__ = ["EmailComposer", "send_email_gmail"]
