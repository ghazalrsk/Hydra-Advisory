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
from flask import Flask, request, Response, send_file, jsonify

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

@app.route("/")
def index():
    resp = send_file(os.path.join(os.path.dirname(__file__), "landing.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp


@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"ok": False, "message": "Email required"}), 400
    try:
        import mailchimp_marketing as MailchimpMarketing
        from mailchimp_marketing.api_client import ApiClientError
        client = MailchimpMarketing.Client()
        client.set_config({
            "api_key": os.environ["MAILCHIMP_API_KEY"],
            "server":  os.environ["MAILCHIMP_SERVER"],
        })
        client.lists.add_list_member(os.environ["MAILCHIMP_LIST_ID"], {
            "email_address": email,
            "status": "subscribed",
        })
        log.info(f"New subscriber: {email}")
        return jsonify({"ok": True})
    except Exception as e:
        err = str(getattr(e, "text", e))
        if "already a list member" in err.lower():
            return jsonify({"ok": True})
        log.error(f"Subscribe error for {email}: {err}")
        return jsonify({"ok": False, "message": "Could not subscribe"}), 500


@app.route("/health")
def health():
    return "OK", 200


@app.route("/get-zoho-token")
def get_zoho_token():
    import requests as _req
    code = request.args.get("code", "")
    if not code:
        return "Pass ?code=YOUR_CODE", 400
    resp = _req.post("https://accounts.zoho.eu/oauth/v2/token", params={
        "code":          code,
        "client_id":     "1000.G2L6RNFPWWZ3SAOQ1NVG371YVSXHYR",
        "client_secret": "f46ea66cbd0bad984fea294e09e06aec14127fdc85",
        "redirect_uri":  "https://localhost",
        "grant_type":    "authorization_code",
    })
    return f"<pre>{resp.text}</pre>", 200


@app.route("/env-check")
def env_check():
    return f"EMAIL_PROVIDER={os.environ.get('EMAIL_PROVIDER', 'NOT_SET')}\nZOHO_CLIENT_ID={os.environ.get('ZOHO_CLIENT_ID', 'NOT_SET')[:10]}...", 200


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
        from datetime import datetime, timezone, timedelta
        from collector import fetch_all_articles, fetch_stock_prices
        from claude_processor import process_with_claude
        from email_builder import build_email_html
        from story_memory import load_memory, save_memory, filter_seen, mark_published

        now = datetime.now(timezone.utc)
        weekday = now.weekday()  # 0=Mon, 5=Sat, 6=Sun

        # Skip weekends for scheduled runs (test emails always go through)
        if not test_email and weekday in (5, 6):
            log.info(f"Weekend ({now.strftime('%A')}) — pipeline skipped")
            return

        is_monday = (weekday == 0)
        today = now.strftime("%A, %-d %B %Y")

        # Load 7-day story memory and fetch articles
        memory = load_memory()
        articles = fetch_all_articles(is_monday=is_monday)

        # Filter out stories already covered in recent editions
        # If memory filter leaves too few, fall back to the full unfiltered pool
        filtered = filter_seen(articles, memory)
        if len(filtered) < 5:
            log.warning(f"Only {len(filtered)} articles after memory filter — using full pool of {len(articles)}")
            articles = articles
        else:
            articles = filtered

        all_stocks = fetch_stock_prices()
        # Pre-select top 3 gainers + bottom 3 losers to keep Claude's input small
        sorted_stocks = sorted(all_stocks, key=lambda s: s.get("raw_change", 0), reverse=True)
        seen = set()
        stocks = []
        for s in sorted_stocks[:3] + sorted_stocks[-3:]:
            if s["ticker"] not in seen:
                seen.add(s["ticker"])
                stocks.append(s)
        # Use last trading day's date (skip weekends)
        last_trading = now.date()
        while last_trading.weekday() >= 5:  # 5=Sat, 6=Sun
            last_trading -= timedelta(days=1)
        # If sending before market close (before ~18:00 UTC), use previous trading day
        if now.hour < 18:
            last_trading -= timedelta(days=1)
            while last_trading.weekday() >= 5:
                last_trading -= timedelta(days=1)
        numbers_timestamp = last_trading.strftime("%-d %b %Y close")
        digest = process_with_claude(articles, stocks, today, numbers_timestamp, is_monday=is_monday)
        html = build_email_html(digest, today)

        import os as _os
        provider = _os.environ.get("EMAIL_PROVIDER", "mailchimp").lower()
        preview_email = _os.environ.get("PREVIEW_EMAIL", "").strip()

        if test_email:
            if provider == "zoho":
                from zoho_sender import send_test_email_zoho
                send_test_email_zoho(html, today, test_email)
            else:
                from mailchimp_sender import send_test_email
                send_test_email(html, today, test_email)
            log.info(f"Test email sent to {test_email} via {provider}")
        else:
            # Send preview copy before the main list
            if preview_email:
                try:
                    if provider == "zoho":
                        from zoho_sender import send_test_email_zoho
                        send_test_email_zoho(html, today, preview_email)
                    else:
                        from mailchimp_sender import send_test_email
                        send_test_email(html, today, preview_email)
                    log.info(f"Preview sent to {preview_email}")
                except Exception as pe:
                    log.warning(f"Preview send failed: {pe}")

            if provider == "zoho":
                from zoho_sender import send_via_zoho
                send_via_zoho(html, today)
            else:
                from mailchimp_sender import send_via_mailchimp
                send_via_mailchimp(html, today)
            log.info(f"Email sent to full list via {provider}")
            # Only update story memory on real sends, not test emails
            memory = mark_published(digest, memory)
            save_memory(memory)

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


# ── Entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_pipeline, "cron", day_of_week="mon-fri", hour=5, minute=45)
    scheduler.start()
    log.info("Scheduler started — pipeline runs Mon–Fri at 06:00 UTC")

    port = int(os.environ.get("PORT", 8080))
    log.info(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
