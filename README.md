# News Mailer

Generate and send a daily news-summary email using Google Gemini and NewsAPI.

## Features

- Fetches top headlines (defaults to US, change in code)
- Uses Gemini Pro to craft a concise, friendly email
- Builds an HTML digest covering **Macroeconomy, Geopolitics, US Stock Market, Cryptocurrency, Other Global Stock Markets, Commodities, Technology** (configurable in `news_fetcher.py`).
- Adds hyperlink list of sources and author footer.
- Sends via **Gmail API** (user OAuth or Workspace service-account) to one or more recipients
- Config driven via environment variables

---

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:

   ```bash
   cp .env.example .env  # Windows: copy .env.example .env
   ```

2. Install dependencies using **one** of the Makefile helpers:

   ```bash
   # classic venv + pip
   make venv

   # or fast uv
   make uv

   # or Poetry (creates its own env)
   make poetry
   ```

   (If you used `make venv` or `make uv`, activate the env first:
   `.\n.venv\Scripts\Activate.ps1` on PowerShell.)

3. Run the application:

   ```bash
   make run            # or: poetry run news-mailer
   ```

You can schedule this with cron / Task Scheduler for daily delivery.

### Gmail Credentials

Choose **one** of the following:

1. **User OAuth installed-app flow** (works for personal Gmail accounts)
   - Download OAuth _Desktop_ client JSON → save as `client_secrets.json` next to the code. See [details below](#how-to-obtain-these-variables) for the full walkthrough.
   - Run `make run` once; a browser will ask for consent and create `token.json` for future runs.
   - For CI/CD, you can instead provide `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` in the environment.

## Environment Variables

| Variable                                    | Purpose                             |
| ------------------------------------------- | ----------------------------------- |
| `GEMINI_API_KEY`                            | Google AI Studio API key            |
| `NEWS_API_KEY`                              | [NewsAPI](https://newsapi.org/) key |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Installed-app OAuth creds (CI)      |
| `GOOGLE_REFRESH_TOKEN`                      | Long-lived refresh token (CI)       |
| `EMAIL_FROM`                                | Sender address                      |
| `EMAIL_TO`                                  | Comma-separated recipients          |

### How to obtain these variables

#### 1. GEMINI_API_KEY (Google AI Studio)
1. Navigate to <https://aistudio.google.com/app/apikey> and sign-in with the Google account that will own the quota.
2. Click **Create API Key**, give it a name (e.g. *news-mailer*), then press **Create key**.
3. Make sure to already have a GCP Project beforehand. If you haven't created one, navigate to <https://console.cloud.google.com/projectcreate> and create one.
4. Copy the key that is shown and paste it into your `.env` file as `GEMINI_API_KEY=...`.

#### 2. NEWS_API_KEY (NewsAPI.org)
1. Create a free account at <https://newsapi.org/register> and verify the e-mail address.
2. After logging in you will land on the **API Keys** page. Copy the key shown under *Current key*.
3. Add it to `.env` as `NEWS_API_KEY=...`.

#### 3. GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET (OAuth credentials)
1. Go to <https://console.cloud.google.com/apis/credentials> (create a project if you don’t have one).
2. Click **Create credentials → OAuth client ID**.
3. Choose **Desktop application** as the application type and give it a name.
4. Click **Create**. A dialog appears with *Client ID* and *Client secret* – copy both.
5. Store them in your CI secrets or local `.env` as:
   ```env
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   ```

#### 4. GOOGLE_REFRESH_TOKEN (long-lived)
There are two convenient ways:

**A. Run the helper script locally**
```bash
# This will append the line GOOGLE_REFRESH_TOKEN=... to your .env file
python - <<'PY' >> .env
from src.news_mailer.service.auth.oauth import load_user_credentials
print(f'GOOGLE_REFRESH_TOKEN="{load_user_credentials().refresh_token}"')
PY
```
• The script opens a browser window asking you to grant *Gmail send* permission.  
• After consent a `token.json` file is created and the refresh token is printed – copy it to `GOOGLE_REFRESH_TOKEN` in your `.env` file if there aren't any yet.

**B. Use Google OAuth Playground** (browser-only)
1. Open <https://developers.google.com/oauthplayground>.
2. Click the settings cog and tick **Use your own OAuth credentials**, paste the *Client ID* and *Secret* from step 3.
3. In *Step 1* (left pane) paste the scope `https://www.googleapis.com/auth/gmail.send`, click **Authorize APIs**, grant Gmail-send permission in the popup, then click **Allow**.

   **If you see an "Error 400: redirect_uri_mismatch":**
   1. In Google Cloud Console open **APIs & Services → Credentials → OAuth 2.0 Client IDs**.
   2. Either edit the existing client **or create a new one** with **Application type = Web application**.
   3. Add this entry to **Authorized redirect URIs**:
      ```
      https://developers.google.com/oauthplayground
      ```
   4. Save and repeat the Playground steps above.

   (For the *local helper script* you instead need a client of type **Desktop application** and the JSON saved as `client_secrets.json`; no redirect URI is required.)
4. Back in the playground click **Exchange authorization code for tokens**; you will receive both an *access_token* and a *refresh_token*.
5. Copy the *refresh_token* value and add it to your `.env` file:
   ```env
   GOOGLE_REFRESH_TOKEN="<paste-here>"
   ```

#### 5. EMAIL_FROM / EMAIL_TO
• `EMAIL_FROM` – the Gmail address that owns the OAuth credentials.  
• `EMAIL_TO` – comma-separated list of recipient e-mails (e.g. `foo@example.com,bar@example.com`).

Once all variables are in `.env` (or GitHub Secrets) the application can authenticate successfully.

## Code Structure

```
src/news_mailer/
├── __init__.py
├── main.py                 # Pipeline entry-point
├── config/
│   ├── __init__.py
│   └── base_config.py       # Pydantic settings
├── service/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── oauth.py         # Gmail OAuth helpers
│   ├── mail/
│   │   ├── __init__.py
│   │   ├── email_composer.py # Gemini prompt & generation
│   │   └── email_sender_gmail.py # Send via Gmail API
│   └── news/
│       ├── __init__.py
│       └── news_fetcher.py   # Fetch topic-based headlines
├── utils/
│   ├── __init__.py
│   └── logger.py             # Simple stdout logger
```
