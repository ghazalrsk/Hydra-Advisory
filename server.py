"""
HYDRA SUMMARY — Web Server
---------------------------
Lightweight Flask server that runs on Railway alongside the cron pipeline.

Endpoints:
  GET  /health
      Simple health check for Railway.

  GET  /ics?event=NAME&start=YYYYMMDD&end=YYYYMMDD&desc=DESCRIPTION
      Returns a downloadable .ics file so email recipients can add
      Sector Diary events to Apple Calendar or any other iCal client.

  POST /store-audio
      Called by the cron pipeline after generating the daily digest.
      Accepts raw MP3 bytes, caches them for serving.

  GET  /audio/today
      Serves the latest daily audio brief as an MP3 file.

To deploy: set this as the start command for your Railway web service:
  python server.py
"""

import os
from flask import Flask, request, Response

app = Flask(__name__)

_AUDIO_PATH = "/tmp/hydra_brief_today.mp3"
_audio_cache: bytes = b""


def _load_cached_audio() -> bytes:
    """Load audio from disk on startup if it exists from a prior run."""
    try:
        with open(_AUDIO_PATH, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return b""


# Load on startup so a server restart doesn't lose today's audio
_audio_cache = _load_cached_audio()


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
        pass  # disk write failure is non-fatal; in-memory cache is sufficient
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
