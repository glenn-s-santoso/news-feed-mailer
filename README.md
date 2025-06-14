# News Mailer

Generate and send a daily news-summary email using Google Gemini and NewsAPI.

## Features

- Fetches top headlines (defaults to US, change in code)
- Uses Gemini Pro to craft a concise, friendly email
- Builds an HTML digest covering **Macroeconomy, Geopolitics, US Stock Market, Cryptocurrency, Other Global Stock Markets, Commodities, Technology** (configurable in `news_fetcher.py`).
- Adds hyperlink list of sources and author footer.
- Sends via **Gmail API** (user OAuth or Workspace service-account) to one or more recipients
- Config driven via environment variables

### Gmail Credentials

Choose **one** of the following:

1. **User OAuth installed-app flow** (works for personal Gmail accounts)
   - Download OAuth _Desktop_ client JSON → save as `client_secrets.json` next to the code.
   - Run `make run` once; a browser will ask for consent and create `token.json` for future runs.
   - For CI/CD, you can instead provide `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` in the environment.

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

## Environment Variables

| Variable                                    | Purpose                             |
| ------------------------------------------- | ----------------------------------- |
| `GEMINI_API_KEY`                            | Google AI Studio API key            |
| `NEWS_API_KEY`                              | [NewsAPI](https://newsapi.org/) key |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Installed-app OAuth creds (CI)      |
| `GOOGLE_REFRESH_TOKEN`                      | Long-lived refresh token (CI)       |
| `EMAIL_FROM`                                | Sender address                      |
| `EMAIL_TO`                                  | Comma-separated recipients          |

## Code Structure

```
src/news_mailer/
├── config.py         # Pydantic settings
├── news_fetcher.py   # Fetch topic-based headlines
├── email_composer.py # Gemini prompt & generation
├── email_sender.py   # SMTP delivery
├── main.py           # Pipeline entry-point
└── logger.py         # Simple stdout logger
```
