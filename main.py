"""
HYDRA SUMMARY — Main Pipeline
-------------------------------
Run this file to generate and send today's Hydra Summary.

What it does, in order:
  1. Fetches articles from all RSS sources defined in sources.py
  2. Fetches stock prices for the Important Numbers section
  3. Sends everything to Claude API for deduplication + summarisation
  4. Builds the finished HTML email from the template
  5. Sends it to the Mailchimp list

To run manually:     python main.py
To run on a schedule: server.py runs this via APScheduler at 6am UTC.

Requirements:
  - .env file with ANTHROPIC_API_KEY and MAILCHIMP_API_KEY (see README)
  - pip install -r requirements.txt
"""

import os
import logging
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Railway injects env vars directly; dotenv not needed

from collector import fetch_all_articles, fetch_stock_prices
from claude_processor import process_with_claude
from email_builder import build_email_html
from mailchimp_sender import send_via_mailchimp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("hydra-summary")


def run():
    today = datetime.now().strftime("%A, %-d %B %Y")
    log.info(f"── Hydra Summary pipeline starting · {today} ──")

    # ── Step 1: Collect articles ────────────────────────────────────────
    log.info("Step 1 · Fetching articles from all sources...")
    articles = fetch_all_articles()
    log.info(f"         {len(articles)} articles collected")

    if len(articles) < 5:
        log.error("Too few articles collected — aborting to avoid empty digest.")
        return

    # ── Step 2: Fetch stock prices ──────────────────────────────────────
    log.info("Step 2 · Fetching stock prices...")
    stocks = fetch_stock_prices()
    numbers_timestamp = datetime.now(timezone.utc).strftime("as of %H:%M UTC")
    log.info(f"         {len(stocks)} stocks fetched")

    # ── Step 3: Claude processes everything ────────────────────────────
    log.info("Step 3 · Sending to Claude for processing...")
    digest = process_with_claude(articles, stocks, today, numbers_timestamp)
    log.info(f"         Claude returned {len(digest.get('news', []))} news items + {len(digest.get('lead_items', []))} lead items")

    # ── Step 4: Build the email HTML ────────────────────────────────────
    log.info("Step 4 · Building email HTML...")
    html = build_email_html(digest, today)
    log.info("         Email HTML built successfully")

    # ── Step 5: Send via Mailchimp ──────────────────────────────────────
    log.info("Step 5 · Sending via Mailchimp...")
    result = send_via_mailchimp(html, today)
    log.info(f"         {result}")

    log.info("── Pipeline complete ──")


if __name__ == "__main__":
    run()
