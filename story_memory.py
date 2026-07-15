"""
HYDRA SUMMARY — Story Memory
------------------------------
Tracks story fingerprints for the last 7 days to prevent repetition
across editions.

Primary storage: JSONBin.io (persists across Railway deploys).
  Set JSONBIN_KEY and JSONBIN_ID as Railway environment variables.
  Create a free account at jsonbin.io, make a bin, copy the ID and API key.

Fallback: local file (lost on redeploy, but better than nothing).
"""

import json
import os
import re
import logging
import requests
from datetime import datetime, timezone, timedelta

log = logging.getLogger("hydra-summary.memory")

MEMORY_FILE = os.environ.get("MEMORY_FILE", "/app/story_memory.json")
MEMORY_DAYS = 7

_JSONBIN_KEY = os.environ.get("JSONBIN_KEY", "")
_JSONBIN_ID  = os.environ.get("JSONBIN_ID", "")
_JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{_JSONBIN_ID}"

_STOP = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "its", "it", "this", "that", "has", "have", "had", "will",
    "would", "could", "should", "may", "might", "new", "says", "said",
    "after", "over", "into", "up", "out", "about", "than", "more",
}


def _fingerprint(title: str) -> str:
    words = re.sub(r"[^\w\s]", "", title.lower()).split()
    meaningful = [w for w in words if w not in _STOP and len(w) > 2]
    return " ".join(meaningful[:6])


def _prune(memory: dict) -> dict:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=MEMORY_DAYS)).isoformat()
    return {k: v for k, v in memory.items() if v >= cutoff}


def load_memory() -> dict:
    # Try JSONBin first
    if _JSONBIN_KEY and _JSONBIN_ID:
        try:
            resp = requests.get(
                f"{_JSONBIN_URL}/latest",
                headers={"X-Master-Key": _JSONBIN_KEY},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json().get("record", {})
                pruned = _prune(data)
                log.info(f"  Memory loaded from JSONBin: {len(pruned)} fingerprints")
                return pruned
        except Exception as e:
            log.warning(f"  JSONBin load failed: {e} — falling back to file")

    # Fallback: local file
    try:
        with open(MEMORY_FILE) as f:
            return _prune(json.load(f))
    except Exception:
        return {}


def save_memory(memory: dict) -> None:
    pruned = _prune(memory)

    # Try JSONBin first
    if _JSONBIN_KEY and _JSONBIN_ID:
        try:
            resp = requests.put(
                _JSONBIN_URL,
                headers={
                    "X-Master-Key": _JSONBIN_KEY,
                    "Content-Type": "application/json",
                },
                json=pruned,
                timeout=10,
            )
            if resp.status_code == 200:
                log.info(f"  Memory saved to JSONBin: {len(pruned)} fingerprints")
                return
            else:
                log.warning(f"  JSONBin save returned {resp.status_code} — falling back to file")
        except Exception as e:
            log.warning(f"  JSONBin save failed: {e} — falling back to file")

    # Fallback: local file
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(pruned, f)
        log.info(f"  Memory saved to file: {len(pruned)} fingerprints")
    except Exception as e:
        log.warning(f"  Could not save memory: {e}")


def filter_seen(articles: list, memory: dict) -> list:
    fresh = []
    dropped = 0
    for a in articles:
        fp = _fingerprint(a.get("title", ""))
        if fp and fp in memory:
            dropped += 1
        else:
            fresh.append(a)
    if dropped:
        log.info(f"  Memory filter: dropped {dropped} already-seen articles")
    return fresh


def mark_published(digest: dict, memory: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    titles = (
        [item.get("text", "") for item in digest.get("lead_items", [])]
        + [item.get("headline", "") for item in digest.get("news", [])]
    )
    for title in titles:
        fp = _fingerprint(title)
        if fp:
            memory[fp] = now
    return memory
