from dotenv import load_dotenv
from os import getenv
from typing import List, Dict, Tuple
import datetime

import google.generativeai as genai

from src.news_mailer.config import get_settings
from src.news_mailer.utils import get_logger
from src.news_mailer.service.news import TOPIC_QUERIES

load_dotenv()
logger = get_logger(__name__)


def _pretty_topic(key: str) -> str:
    """Convert snake_case topic keys to display form like 'US Stock Market'."""
    return " ".join(
        word.upper() if len(word) <= 3 else word.capitalize() for word in key.split("_")
    )

REGION = getenv("REGION") if getenv("REGION") else "Global"

DISPLAY_TOPICS = ", ".join(_pretty_topic(k) for k in TOPIC_QUERIES.keys())

SNIPPET_CHARS = 400

PROMPT_TEMPLATE = f"""
You are an expert financial and global news analyst tasked with creating an engaging and informative HTML email digest. Your goal is to deliver the most critical and latest time-sensitive news, providing insightful context and analysis that helps the reader understand the "why" and "what's next." Your digest MUST include at least one numbered section for EACH of these topics: {DISPLAY_TOPICS}.

The email should be structured with clear headings, subheadings, and bullet points, using simple inline styles for readability and broad email client compatibility. Do NOT wrap the output in <html><body>; just produce the inner HTML fragment.

**Key Requirements:**
1.  **Overall Tone:** Professional, insightful, slightly urgent due to time-sensitive nature, yet easy to understand for a general audience. Adopt a tone that feels like a trusted expert explaining complex events.
2.  **Introduction:** Start with a friendly, date-aware greeting in a `<p>` tag (e.g., "Good morning/afternoon/evening from Jakarta!"). Immediately set the stage by highlighting the overall market mood or the most dominant theme of the day.
3.  **Contextual Overview:** Provide a brief, high-level summary of the day's significant events, emphasizing any prevailing "wait-and-see" attitudes, upcoming major announcements, or key ongoing discussions. Use a `<p>` tag for this.
4.  **Section Header:** Use an `<h2>` for a section like "Let's break it down."
5.  **Main News Stories (Numbered Sections):**
    * For each of the provided news articles, create a distinct section.
    * Each section should start with an `<h3>` heading for the news item's title followed by the citation tag in square brackets (e.g., "1. [News Title] [<a href='URL'>1</a>]").
    * Under each `<h3>`, use the following structure with `<p>` tags and inline styles:
        * `<p style="font-weight: bold;">What Happened:</p>`: A concise, one-sentence summary of the news event.
        * `<p style="font-weight: bold;">Simple Explanation:</p>`: Briefly explain the news in layman's terms, including any relevant background if necessary.
        * `<p style="font-weight: bold;">The Results:</p>`: State the immediate, concrete outcomes or data points from the news.
        * `<p style="font-weight: bold;">Why it Matters:</p>`: Explain the significance and broader implications of the news.
        * `<p style="font-weight: bold;">Simple Implication (If... Then...):</p>`: Provide a clear "if-then" statement to illustrate potential future impacts or market reactions.
        * `<p style="font-weight: bold;">Expert Opinion:</p>`: Craft a single, rich paragraph (3–4 sentences) offering a nuanced expert perspective, addressing the news fully, challenging surface interpretations, and guiding how readers should think about its broader significance. Focus on substance over filler.
        * Conclude the section with a `<p>` relating the specific news to broader market movements (e.g., currency shifts, stock reactions), ensuring any statistics or claims are followed by the appropriate citation tag, e.g. "[<a href='URL'>2</a>]".
6.  **"All Eyes Are Now on Tomorrow" Section:**
    * Create a dedicated `<h3>` section for upcoming critical events.
    * List key events (e.g., economic reports, central bank meetings) using an unordered list (`<ul>`) where each `<li>` describes the event and its potential impact.
    * Use a `<p>` to explain why these upcoming events are so crucial and how they might set the tone for global markets (stocks, bonds, currencies, crypto, etc.).
7.  **Closing:** End with a polite and forward-looking closing in a `<p>` tag, summarizing the day's overall mood and hinting at what's to come.

**News Articles (for detailed analysis):**
[INSERT_NEWS_ARTICLES_HERE]
"""
MODEL_NAME = "gemini-2.5-flash-preview-05-20"

class EmailComposer:
    """Compose email content using Gemini Pro 2.5."""

    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(MODEL_NAME)

    def compose_email(self, articles: List[Dict]) -> Tuple[str, str]:
        """Generate email subject and body from a list of articles.

        Args:
            articles: List of article dicts with `title` and `url`.

        Returns:
            subject, body
        """
        news_lines = []
        for idx, article in enumerate(articles, start=1):
            snippet = article.get("content") or article.get("description") or ""
            snippet = snippet.strip()
            if len(snippet) > SNIPPET_CHARS:
                snippet = snippet[:SNIPPET_CHARS].rstrip() + "…"
            news_lines.append(
                f"- [{idx}] {article['title']}\n  {snippet}\n  {article['url']}\n"
            )
        news_block = "\n".join(news_lines)

        jakarta_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            hours=7
        )
        current_date_str = jakarta_now.strftime("%A, %B %d, %Y")

        date_preface = f"Today's date in Jakarta is {current_date_str}. Use this exact date in the greeting WITHOUT additional styling. For any other components other than date, you are allowed to style it"

        prompt = date_preface + PROMPT_TEMPLATE.replace(
            "[INSERT_NEWS_ARTICLES_HERE]", news_block
        )
        logger.info("Composing email with %d articles", len(articles))
        response = self.model.generate_content(prompt)
        body = response.text.strip()

        sources_html_lines = [
            "<hr>",
            '<p style="font-weight:bold;">Sources:</p>',
            "<ul>",
        ]
        for idx, article in enumerate(articles, start=1):
            url = article.get("url")
            title = article.get("title", url)
            sources_html_lines.append(f'<li>[{idx}] <a href="{url}">{title}</a></li>')
        sources_html_lines.append("</ul>")

        settings = get_settings()
        author_name = (
            getattr(settings, "author_name", None) or settings.email_from.split("@")[0]
        )
        footer_html = (
            f'<p style="font-size:0.8em;">News feed generated by Gemini, authored by '
            f"{author_name} &lt;{settings.email_from}&gt;</p>"
        )

        body += "\n" + "\n".join(sources_html_lines) + "\n" + footer_html

        subject = f"Your {REGION} Daily News Digest - {current_date_str}"
        return subject, body
