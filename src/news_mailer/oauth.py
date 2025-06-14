"""Utility helpers for Gmail OAuth installed-app flow."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES: Sequence[str] = ("https://www.googleapis.com/auth/gmail.send",)
CLIENT_SECRETS = Path("client_secrets.json")
TOKEN_FILE = Path("token.json")


def load_user_credentials() -> Credentials | None:
    """Return cached or newly-obtained user OAuth credentials.

    If `client_secrets.json` is present but no token cache exists, this will
    open a local browser window for the user to grant consent. The resulting
    refresh token is stored in `token.json`.
    """
    creds: Credentials | None = None

    # 1. Load cached token if present
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)  # type: ignore[arg-type]
        if creds and creds.valid and not creds.expired:
            return creds
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                TOKEN_FILE.write_text(creds.to_json())
                return creds
            except GoogleAuthError:
                creds = None  # refresh failed, fall back to new flow

    # 2. Environment variables (non-interactive, e.g. CI)
    env_refresh = os.getenv("GOOGLE_REFRESH_TOKEN")
    env_client_id = os.getenv("GOOGLE_CLIENT_ID")
    env_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if env_refresh and env_client_id and env_client_secret:
        creds = Credentials(
            token=None,
            refresh_token=env_refresh,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=env_client_id,
            client_secret=env_client_secret,
            scopes=list(SCOPES),
        )
        try:
            creds.refresh(Request())
        except GoogleAuthError:
            return None
        return creds

    # 3. Start installed-app flow if client secrets available (interactive)
    if CLIENT_SECRETS.exists():
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
        return creds

    # 4. Nothing available
    return None
