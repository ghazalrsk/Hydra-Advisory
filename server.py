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




# ── Pipeline runner ───────────────────────────────────────────────────────

def run_pipeline(test_email: str = ""):
    log.info("── Pipeline starting ──")
    try:
        from datetime import datetime, timezone
        from collector import fetch_all_articles, fetch_stock_prices
        from claude_processor import process_with_claude
        from email_builder import build_email_html

        today = datetime.now().strftime("%A, %-d %B %Y")
        articles = fetch_all_articles()
        if len(articles) < 5:
            log.error("Too few articles — aborting")
            return
        stocks = fetch_stock_prices()
        numbers_timestamp = datetime.now(timezone.utc).strftime("as of %H:%M UTC")
        digest = process_with_claude(articles, stocks, today, numbers_timestamp)
        html = build_email_html(digest, today)

        import os as _os
        provider = _os.environ.get("EMAIL_PROVIDER", "mailchimp").lower()
        if test_email:
            if provider == "zoho":
                from zoho_sender import send_test_email_zoho
                send_test_email_zoho(html, today, test_email)
            else:
                from mailchimp_sender import send_test_email
                send_test_email(html, today, test_email)
            log.info(f"Test email sent to {test_email} via {provider}")
        else:
            if provider == "zoho":
                from zoho_sender import send_via_zoho
                send_via_zoho(html, today)
            else:
                from mailchimp_sender import send_via_mailchimp
                send_via_mailchimp(html, today)
            log.info(f"Email sent to full list via {provider}")

    except Exception as e:
        log.error(f"Pipeline failed: {e}", exc_info=True)


@app.route("/trigger")
def trigger():
    test_email = request.args.get("email", "")
    threading.Thread(target=run_pipeline, args=(test_email,), daemon=True).start()
    if test_email:
        return f"Pipeline triggered — test email sending to {test_email}. Check Railway logs for progress.", 200
    return "Pipeline triggered — sending to full list. Check Railway logs for progress.", 200


@app.route("/debug")
def trigger_sync():
    """Runs pipeline synchronously and returns full log output — use for debugging only."""
    import io, logging as _logging
    test_email = request.args.get("email", "")
    buf = io.StringIO()
    handler = _logging.StreamHandler(buf)
    handler.setLevel(_logging.DEBUG)
    _logging.getLogger().addHandler(handler)
    try:
        run_pipeline(test_email)
    except Exception as e:
        buf.write(f"\nFATAL: {e}")
    finally:
        _logging.getLogger().removeHandler(handler)
    return f"<pre>{buf.getvalue()}</pre>", 200


@app.route("/get-zoho-token")
def get_zoho_token():
    """Temporary: exchange a Zoho auth code for a refresh token."""
    import requests as _req
    code = request.args.get("code", "")
    if not code:
        return "Pass ?code=YOUR_CODE", 400
    resp = _req.post("https://accounts.zoho.eu/oauth/v2/token", params={
        "code":          code,
        "client_id":     "1000.G2L6RNFPWWZ3SAOQ1NVG371YVSXHYR",
        "client_secret": "f46ea66cbd0bad984fea294e09e06aec14127fdc85",
        "grant_type":    "authorization_code",
    })
    return f"<pre>{resp.text}</pre>", 200


# ── Entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_pipeline, "cron", hour=6, minute=0)
    scheduler.start()
    log.info("Scheduler started — pipeline runs daily at 06:00 UTC")

    port = int(os.environ.get("PORT", 8080))
    log.info(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
