"""
HYDRA SUMMARY — Audio Generator
---------------------------------
Generates a spoken 1-minute summary of the daily digest using Google TTS.
Returns MP3 bytes that are then POSTed to the Flask server for hosting.
"""

import io
import logging
from gtts import gTTS

log = logging.getLogger("hydra-summary.audio")


def generate_audio(digest: dict, today: str) -> bytes:
    script = _build_script(digest, today)
    log.info(f"  Generating audio ({len(script.split())} words)...")
    tts = gTTS(text=script, lang="en", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    audio_bytes = buf.read()
    log.info(f"  Audio generated ({len(audio_bytes):,} bytes)")
    return audio_bytes


def _build_script(digest: dict, today: str) -> str:
    lines = [f"Welcome to Hydra Summary. Here are the headlines for {today}."]

    lead_items = digest.get("lead_items", [])
    if lead_items:
        lines.append("Today's top stories.")
        for item in lead_items:
            text = item.get("text", "").strip().rstrip(".")
            if text:
                lines.append(f"{text}.")

    news_items = digest.get("news", [])
    if news_items:
        lines.append("In the news.")
        for item in news_items:
            headline = item.get("headline", "").strip().rstrip(".")
            if headline:
                lines.append(f"{headline}.")

    lines.append("That's your Hydra Brief for today. Have a great day.")
    return " ".join(lines)
