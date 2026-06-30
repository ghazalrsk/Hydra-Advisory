"""
HYDRA SUMMARY — Web Server + Scheduler
----------------------------------------
Single process that does two things:

  1. Runs Flask as a web server (Railway keeps it alive as a web service)
     Endpoints:
       GET  /health              — health check for Railway
       GET  /ics?...             — downloadable .ics for Apple Calendar
       POST /store-audio         — called internally to cache daily audio
       GET  /audio/today         — serves today's audio brief

  2. Runs the Hydra pipeline daily at 06:00 UTC via APScheduler
     (replaces the Railway cron job — set this service as a web service,
      not a cron service, with start command: python server.py)

Railway setup:
  - Service type: Web Service
  - Start command: python server.py
  - Environment variables: same as before (ANTHROPIC_API_KEY, MAILCHIMP_*, etc.)
"""

import logging
import os
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, Response

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("hydra-server")

app = Flask(__name__)

_AUDIO_PATH = "/tmp/hydra_brief_today.mp3"
_audio_cache: bytes = b""


def _load_cached_audio() -> bytes:
    try:
        with open(_AUDIO_PATH, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return b""


_audio_cache = _load_cached_audio()


# ── Flask endpoints ───────────────────────────────────────────────────────

@app.route("/health")
def health():
    return "OK", 200


@app.route("/ics")
def ics():
    event = request.args.get("event", "Event")
    start = request.args.get("start", "")
    end   = request.args.get("end",   "")
    desc  = request.args.get("desc",  "")

    if not start or not end:
        return "Missing start or end date", 400

    content = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Hydra Advisory//Hydra Brief//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"DTSTART;VALUE=DATE:{start}",
        f"DTEND;VALUE=DATE:{end}",
        f"SUMMARY:{event}",
        f"DESCRIPTION:{desc}",
        "END:VEVENT",
        "END:VCALENDAR",
    ])

    filename = event.replace(" ", "_").replace("/", "-")[:40] + ".ics"
    return Response(
        content,
        mimetype="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.route("/store-audio", methods=["POST"])
def store_audio():
    global _audio_cache
    data = request.get_data()
    if not data:
        return "No audio data received", 400
    _audio_cache = data
    try:
        with open(_AUDIO_PATH, "wb") as f:
            f.write(data)
    except Exception:
        pass
    return "OK", 200


@app.route("/audio/today")
def audio_today():
    if not _audio_cache:
        return "No audio available yet", 404
    return Response(
        _audio_cache,
        mimetype="audio/mpeg",
        headers={"Content-Disposition": 'inline; filename="hydra_brief_today.mp3"'},
    )


# ── Pipeline runner ───────────────────────────────────────────────────────

def run_pipeline():
    log.info("── Scheduled pipeline starting ──")
    try:
        from main import run
        run()
    except Exception as e:
        log.error(f"Pipeline failed: {e}", exc_info=True)


# ── Entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_pipeline, "cron", hour=6, minute=0)
    scheduler.start()
    log.info("Scheduler started — pipeline runs daily at 06:00 UTC")

    port = int(os.environ.get("PORT", 8080))
    log.info(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
