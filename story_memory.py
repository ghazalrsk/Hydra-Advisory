"""
HYDRA SUMMARY — Story Memory
------------------------------
Tracks story fingerprints for the last 7 days to prevent repetition
across editions. Persisted as a JSON file on disk.

On Railway, the filesystem resets on redeploy, so memory is best-effort —
it survives restarts within a deploy but not across full redeploys.
"""

import json
import os
import re
import logging
from datetime import datetime, timezone, timedelta

log = logging.getLogger("hydra-summary.memory")

MEMORY_FILE = os.environ.get("MEMORY_FILE", "/app/story_memory.json")
MEMORY_DAYS = 7

_STOP = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "its", "it", "this", "that", "has", "have", "had", "will",
    "would", "could", "should", "may", "might", "new", "says", "said",
    "after", "over", "into", "up", "out", "about", "than", "more",
}


def _fingerprint(title: str) -> str:
    """Normalise a headline to a stable key for deduplication."""
    words = re.sub(r"[^\w\s]", "", title.lower()).split()
    meaningful = [w for w in words if w not in _STOP and len(w) > 2]
    return " ".join(meaningful[:6])


def load_memory() -> dict:
    """Load memory dict from disk, pruning entries older than MEMORY_DAYS."""
    try:
        with open(MEMORY_FILE) as f:
            raw = json.load(f)
    except Exception:
        return {}

    cutoff = (datetime.now(timezone.utc) - timedelta(days=MEMORY_DAYS)).isoformat()
    return {k: v for k, v in raw.items() if v >= cutoff}


def save_memory(memory: dict) -> None:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=MEMORY_DAYS)).isoformat()
    pruned = {k: v for k, v in memory.items() if v >= cutoff}
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(pruned, f)
        log.info(f"  Memory saved: {len(pruned)} fingerprints")
    except Exception as e:
        log.warning(f"  Could not save memory: {e}")


def filter_seen(articles: list, memory: dict) -> list:
    """Remove articles whose story fingerprint already exists in memory."""
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
    """Add today's published headlines to memory."""
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
