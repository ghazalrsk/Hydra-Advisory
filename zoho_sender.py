"""
HYDRA SUMMARY — Zoho Campaigns Sender
---------------------------------------
Sends the daily email via Zoho Campaigns API.

Required environment variables:
  ZOHO_CLIENT_ID       — Zoho OAuth client ID
  ZOHO_CLIENT_SECRET   — Zoho OAuth client secret
  ZOHO_REFRESH_TOKEN   — Zoho OAuth refresh token
  ZOHO_LIST_KEY        — Mailing list key (Zoho Campaigns → Lists → Settings)
  ZOHO_FROM_EMAIL      — Sender email (must be verified in Zoho)
  ZOHO_FROM_NAME       — Sender display name (default: "Hydra Advisory")

HOW TO GET THESE:
  1. Go to https://api-console.zoho.com → Create a Server-based Application
  2. Scopes: ZohoCampaigns.campaigns.ALL, ZohoCampaigns.lists.ALL
  3. Generate a refresh token via OAuth flow
  4. List Key: Zoho Campaigns → Contacts → Lists → click your list → Settings
"""

import os
import logging
import requests

log = logging.getLogger("hydra-summary.zoho")

_TOKEN_URL = "https://accounts.zoho.eu/oauth/v2/token"
_API_BASE  = "https://campaigns.zoho.eu/api/v1.1"


def _get_access_token() -> str:
    resp = requests.post(_TOKEN_URL, params={
        "refresh_token": os.environ["ZOHO_REFRESH_TOKEN"],
        "client_id":     "1000.ZKN2B8W42JGJ6EMK6OZD2SKAZ5NI5R",
        "client_secret": "08d1d8d92e6549384529f6a96383285ecd11b68dcd",
        "grant_type":    "refresh_token",
    })
    resp.raise_for_status()
    data = resp.json()
    if "access_token" not in data:
        raise ValueError(f"Token refresh failed: {data}")
    return data["access_token"]


def send_via_zoho(html: str, today: str) -> str:
    token      = _get_access_token()
    list_key   = os.environ["ZOHO_LIST_KEY"]
    from_email = os.environ.get("ZOHO_FROM_EMAIL", "info@hydra-advisory.com")
    from_name  = os.environ.get("ZOHO_FROM_NAME",  "Hydra Advisory")
    subject    = f"Hydra Summary · {today}"

    headers = {"Authorization": f"Zoho-oauthtoken {token}"}

    # Step 1: Create campaign
    r = requests.post(f"{_API_BASE}/createcampaign", headers=headers, data={
        "campaignName":  f"Hydra Summary {today}",
        "fromName":      from_name,
        "fromEmail":     from_email,
        "replyTo":       from_email,
        "subject":       subject,
        "campaignType":  "autoresponder",
        "mailListKey":   list_key,
        "clickTracking": "true",
        "openTracking":  "true",
    })
    r.raise_for_status()
    data = r.json()
    campaign_key = data.get("campaign_key") or data.get("details", {}).get("campaignKey")
    if not campaign_key:
        raise ValueError(f"No campaign key in response: {data}")
    log.info(f"  Campaign created: {campaign_key}")

    # Step 2: Set HTML content
    r = requests.post(f"{_API_BASE}/updatecampaigncontent", headers=headers, data={
        "campaignKey": campaign_key,
        "htmlBody":    html,
    })
    r.raise_for_status()
    log.info("  Content set")

    # Step 3: Send
    r = requests.post(f"{_API_BASE}/sendcampaign", headers=headers, data={
        "campaignKey":  campaign_key,
        "sendDate":     "immediate",
        "timezone":     "Europe/Rome",
    })
    r.raise_for_status()
    log.info("  Campaign sent")

    return f"Zoho campaign '{subject}' sent (key: {campaign_key})"


def send_test_email_zoho(html: str, today: str, test_email: str) -> str:
    token      = _get_access_token()
    list_key   = os.environ["ZOHO_LIST_KEY"]
    from_email = os.environ.get("ZOHO_FROM_EMAIL", "info@hydra-advisory.com")
    from_name  = os.environ.get("ZOHO_FROM_NAME",  "Hydra Advisory")
    subject    = f"[TEST] Hydra Summary · {today}"

    headers = {"Authorization": f"Zoho-oauthtoken {token}"}

    r = requests.post(f"{_API_BASE}/createcampaign", headers=headers, data={
        "campaignName":  f"TEST Hydra Summary {today}",
        "fromName":      from_name,
        "fromEmail":     from_email,
        "replyTo":       from_email,
        "subject":       subject,
        "campaignType":  "autoresponder",
        "mailListKey":   list_key,
    })
    log.info(f"  createcampaign status={r.status_code} body={r.text[:500]}")
    r.raise_for_status()
    if not r.text:
        raise ValueError(f"Empty response from createcampaign: status={r.status_code}")
    data = r.json()
    campaign_key = data.get("campaign_key") or data.get("details", {}).get("campaignKey")
    if not campaign_key:
        raise ValueError(f"No campaign key in response: {data}")

    r = requests.post(f"{_API_BASE}/updatecampaigncontent", headers=headers, data={
        "campaignKey": campaign_key,
        "htmlBody":    html,
    })
    r.raise_for_status()

    r = requests.post(f"{_API_BASE}/sendtestmail", headers=headers, data={
        "campaignKey": campaign_key,
        "emailIds":    test_email,
    })
    r.raise_for_status()

    return f"Zoho test email sent to {test_email} (key: {campaign_key})"
