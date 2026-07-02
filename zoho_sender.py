"""
HYDRA SUMMARY — Zoho Campaigns Sender
---------------------------------------
Sends the daily email via Zoho Campaigns API v1.1 (EU region).

Required environment variables:
  ZOHO_REFRESH_TOKEN   — Zoho OAuth refresh token
  ZOHO_LIST_KEY        — Mailing list key (Zoho Campaigns → Contacts → Lists → Settings)
  ZOHO_FROM_EMAIL      — Sender email (must be verified in Zoho)
  ZOHO_FROM_NAME       — Sender display name (default: "Hydra Advisory")
"""

import os
import re
import logging
import requests

log = logging.getLogger("hydra-summary.zoho")

_TOKEN_URL = "https://accounts.zoho.eu/oauth/v2/token"
_API_BASE  = "https://campaigns.zoho.eu/api/v1.1"

_SELF_CLIENT_ID     = "1000.ZKN2B8W42JGJ6EMK6OZD2SKAZ5NI5R"
_SELF_CLIENT_SECRET = "08d1d8d92e6549384529f6a96383285ecd11b68dcd"


def _get_access_token() -> str:
    resp = requests.post(_TOKEN_URL, params={
        "refresh_token": os.environ["ZOHO_REFRESH_TOKEN"],
        "client_id":     _SELF_CLIENT_ID,
        "client_secret": _SELF_CLIENT_SECRET,
        "grant_type":    "refresh_token",
    })
    resp.raise_for_status()
    data = resp.json()
    if "access_token" not in data:
        raise ValueError(f"Token refresh failed: {data}")
    return data["access_token"]


def _api(token: str, action: str, data: dict) -> str:
    """Call Zoho Campaigns API v1.1."""
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    payload = {"resfmt": "JSON"}
    payload.update(data)
    r = requests.post(f"{_API_BASE}/{action}", headers=headers, params={"resfmt": "JSON"}, data=payload)
    log.info(f"  {action} status={r.status_code} body={r.text[:300]}")
    r.raise_for_status()
    return r.text


def _extract_campaign_key(text: str) -> str:
    m = re.search(r'"campaignKey"\s*:\s*"([^"]+)"', text)
    if not m:
        m = re.search(r"<campaignKey>([^<]+)</campaignKey>", text)
    if not m:
        raise ValueError(f"No campaignKey in response: {text[:300]}")
    return m.group(1)


def send_via_zoho(html: str, today: str) -> str:
    token      = _get_access_token()
    list_key   = os.environ["ZOHO_LIST_KEY"]
    from_email = os.environ.get("ZOHO_FROM_EMAIL", "info@hydra-advisory.com")
    from_name  = os.environ.get("ZOHO_FROM_NAME",  "Hydra Advisory")
    subject    = f"Hydra Summary · {today}"

    resp = _api(token, "createcampaign", {
        "campaignName":  f"Hydra Summary {today}",
        "fromName":      from_name,
        "fromEmail":     from_email,
        "replyTo":       from_email,
        "subject":       subject,
        "campaignType":  "regular",
        "mailListKey":   list_key,
        "clickTracking": "true",
        "openTracking":  "true",
    })
    campaign_key = _extract_campaign_key(resp)
    log.info(f"  Campaign created: {campaign_key}")

    _api(token, "updatecampaigncontent", {
        "campaignKey": campaign_key,
        "htmlBody":    html,
    })
    log.info("  Content set")

    _api(token, "sendcampaign", {
        "campaignKey": campaign_key,
        "sendDate":    "immediate",
        "timezone":    "Europe/Rome",
    })
    log.info("  Campaign sent")

    return f"Zoho campaign '{subject}' sent (key: {campaign_key})"


def send_test_email_zoho(html: str, today: str, test_email: str) -> str:
    token      = _get_access_token()
    list_key   = os.environ["ZOHO_LIST_KEY"]
    from_email = os.environ.get("ZOHO_FROM_EMAIL", "info@hydra-advisory.com")
    from_name  = os.environ.get("ZOHO_FROM_NAME",  "Hydra Advisory")
    subject    = f"[TEST] Hydra Summary · {today}"

    resp = _api(token, "createcampaign", {
        "campaignName":  f"TEST Hydra Summary {today}",
        "fromName":      from_name,
        "fromEmail":     from_email,
        "replyTo":       from_email,
        "subject":       subject,
        "campaignType":  "regular",
        "mailListKey":   list_key,
    })
    campaign_key = _extract_campaign_key(resp)
    log.info(f"  Test campaign created: {campaign_key}")

    _api(token, "updatecampaigncontent", {
        "campaignKey": campaign_key,
        "htmlBody":    html,
    })
    log.info("  Content set")

    _api(token, "sendtestmail", {
        "campaignKey": campaign_key,
        "emailIds":    test_email,
    })
    log.info("  Test email sent")

    return f"Zoho test email sent to {test_email} (key: {campaign_key})"
