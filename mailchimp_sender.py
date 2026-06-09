"""
HYDRA SUMMARY — Mailchimp Sender
----------------------------------
Creates a Mailchimp campaign and sends it to the subscriber list.

Requires in .env:
  MAILCHIMP_API_KEY     — your Mailchimp API key (Account → Extras → API Keys)
  MAILCHIMP_LIST_ID     — the audience ID to send to (Audience → Settings → Audience name & defaults)
  MAILCHIMP_SERVER      — the server prefix in your API key, e.g. "us21" (the part before .api.mailchimp.com)
  MAILCHIMP_FROM_NAME   — sender display name, e.g. "Hydra Advisory"
  MAILCHIMP_FROM_EMAIL  — sender email, e.g. "info@hydra-advisory.com"

HOW TO FIND THESE:
  API Key:   Mailchimp → Account → Extras → API Keys
  List ID:   Mailchimp → Audience → Settings → Audience name & defaults → Audience ID
  Server:    Look at your API key — it ends with "-us21" or similar. That suffix is your server prefix.
"""

import os
import logging
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

log = logging.getLogger("hydra-summary.mailchimp")


def send_via_mailchimp(html: str, today: str) -> str:
    """
    Creates a Mailchimp campaign with the given HTML and sends it immediately.

    Returns a string describing the result (for logging).
    Raises an exception if sending fails.
    """
    api_key    = os.environ["MAILCHIMP_API_KEY"]
    list_id    = os.environ["MAILCHIMP_LIST_ID"]
    server     = os.environ["MAILCHIMP_SERVER"]          # e.g. "us21"
    from_name  = os.environ.get("MAILCHIMP_FROM_NAME",  "Hydra Advisory")
    from_email = os.environ.get("MAILCHIMP_FROM_EMAIL", "info@hydra-advisory.com")

    subject = f"Hydra Summary · {today}"

    client = MailchimpMarketing.Client()
    client.set_config({
        "api_key": api_key,
        "server": server,
    })

    try:
        # ── Step A: Create the campaign ──────────────────────────────────
        campaign = client.campaigns.create({
            "type": "regular",
            "recipients": {
                "list_id": list_id,
            },
            "settings": {
                "subject_line":  subject,
                "from_name":     from_name,
                "reply_to":      from_email,
                "title":         f"Hydra Summary {today}",
            },
        })

        campaign_id = campaign["id"]
        log.info(f"  Campaign created: {campaign_id}")

        # ── Step B: Set the email content ────────────────────────────────
        client.campaigns.set_content(campaign_id, {
            "html": html,
        })

        log.info(f"  Content set")

        # ── Step C: Send ─────────────────────────────────────────────────
        client.campaigns.send(campaign_id)

        return f"Campaign '{subject}' sent successfully (id: {campaign_id})"

    except ApiClientError as e:
        log.error(f"Mailchimp API error: {e.text}")
        raise


def send_test_email(html: str, today: str, test_email: str) -> str:
    """
    Sends a test email to a single address instead of the full list.
    Use this during the testing week (Week 3 of the build plan) before going live.

    Usage:
        from mailchimp_sender import send_test_email
        send_test_email(html, today, "yourname@hydra-advisory.com")
    """
    api_key   = os.environ["MAILCHIMP_API_KEY"]
    list_id   = os.environ["MAILCHIMP_LIST_ID"]
    server    = os.environ["MAILCHIMP_SERVER"]
    from_name  = os.environ.get("MAILCHIMP_FROM_NAME",  "Hydra Advisory")
    from_email = os.environ.get("MAILCHIMP_FROM_EMAIL", "info@hydra-advisory.com")

    client = MailchimpMarketing.Client()
    client.set_config({"api_key": api_key, "server": server})

    subject = f"[TEST] Hydra Summary · {today}"

    try:
        campaign = client.campaigns.create({
            "type": "regular",
            "recipients": {"list_id": list_id},
            "settings": {
                "subject_line": subject,
                "from_name":    from_name,
                "reply_to":     from_email,
                "title":        f"TEST Hydra Summary {today}",
            },
        })

        campaign_id = campaign["id"]

        client.campaigns.set_content(campaign_id, {"html": html})

        client.campaigns.send_test_email(campaign_id, {
            "test_emails": [test_email],
            "send_type": "html",
        })

        return f"Test email sent to {test_email} (campaign id: {campaign_id})"

    except ApiClientError as e:
        log.error(f"Mailchimp test send error: {e.text}")
        raise
