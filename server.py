"""
HYDRA SUMMARY — Web Server
---------------------------
Lightweight Flask server that runs on Railway alongside the cron pipeline.

Endpoints:
  GET /ics?event=NAME&start=YYYYMMDD&end=YYYYMMDD&desc=DESCRIPTION
      Returns a downloadable .ics file so email recipients can add
      Sector Diary events to Apple Calendar or any other iCal client.

  GET /health
      Simple health check for Railway.

To deploy: set this as the start command for your Railway web service:
  python server.py
"""

import os
from flask import Flask, request, Response

app = Flask(__name__)


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
