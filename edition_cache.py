"""
Persists the latest sent edition HTML to JSONBin so new subscribers
always receive the most recent edition regardless of server restarts or weekends.

Requires env vars:
  JSONBIN_KEY          — same master key used for story memory
  JSONBIN_EDITION_ID   — a separate JSONBin bin ID just for the edition cache
"""

import os
import logging
import requests

log = logging.getLogger("hydra-summary.edition-cache")

_KEY = os.environ.get("JSONBIN_KEY", "")
_BIN = os.environ.get("JSONBIN_EDITION_ID", "")
_URL = f"https://api.jsonbin.io/v3/b/{_BIN}"


def save_edition(html: str, date_label: str) -> None:
    if not _KEY or not _BIN:
        log.warning("Edition cache: JSONBIN_KEY or JSONBIN_EDITION_ID not set — skipping save")
        return
    try:
        resp = requests.put(
            _URL,
            headers={"X-Master-Key": _KEY, "Content-Type": "application/json"},
            json={"html": html, "date": date_label},
            timeout=15,
        )
        if resp.status_code == 200:
            log.info(f"Edition cached to JSONBin ({date_label})")
        else:
            log.warning(f"Edition cache save returned {resp.status_code}")
    except Exception as e:
        log.warning(f"Edition cache save failed: {e}")


def load_edition() -> dict:
    """Returns {"html": "...", "date": "..."} or {} if unavailable."""
    if not _KEY or not _BIN:
        return {}
    try:
        resp = requests.get(
            f"{_URL}/latest",
            headers={"X-Master-Key": _KEY},
            timeout=10,
        )
        if resp.status_code == 200:
            record = resp.json().get("record", {})
            if record.get("html") and record.get("date"):
                log.info(f"Edition loaded from JSONBin ({record['date']})")
                return record
    except Exception as e:
        log.warning(f"Edition cache load failed: {e}")
    return {}
