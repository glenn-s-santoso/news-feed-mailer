"""Mail service."""

from .email_composer import EmailComposer
from .email_sender_gmail import send_email_gmail
from .email_sender_brevo import send_email_brevo

__all__ = ["EmailComposer", "send_email_gmail", "send_email_brevo"]
