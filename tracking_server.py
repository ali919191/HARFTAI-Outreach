"""
tracking_server.py

Small public web service that:
  - Serves a 1x1 transparent pixel at /open/<tracking_id>.png and logs
    an "open" event to the Google Sheet. This is a best-effort signal
    only -- see README for why open tracking is approximate (Apple Mail
    Privacy Protection and Gmail's image proxy both pre-load images for
    many users, which can register as a false "open").
  - Handles /unsubscribe/<tracking_id> and marks that lead Opted Out so
    send_and_followup.py will never email them again.

This file needs to run somewhere with a public HTTPS URL (Render,
Railway, Fly.io, a small VPS, etc.) -- see README for deployment notes.
Point TRACKING_BASE_URL in your .env at wherever this ends up living.
"""

from flask import Flask, Response

from common import get_sheet, read_rows, update_cells, today_str, STATUS_OPTED_OUT

app = Flask(__name__)

# 1x1 transparent GIF
PIXEL_BYTES = bytes.fromhex(
    "47494638396101000100800000000000ffffff21f90401000000002c0000000001000100"
    "0002024401003b"
)


def find_row_by_tracking_id(tracking_id):
    sheet = get_sheet()
    for row_number, row in read_rows(sheet):
        if row.get("Tracking ID") == tracking_id:
            return sheet, row_number, row
    return sheet, None, None


@app.route("/open/<tracking_id>.png")
def track_open(tracking_id):
    sheet, row_number, row = find_row_by_tracking_id(tracking_id)
    if row_number:
        current_opens = int(row.get("Opens") or 0)
        update_cells(sheet, row_number, {
            "Opens": current_opens + 1,
            "Last Open Date": today_str(),
        })
    return Response(PIXEL_BYTES, mimetype="image/gif")


@app.route("/unsubscribe/<tracking_id>")
def unsubscribe(tracking_id):
    sheet, row_number, row = find_row_by_tracking_id(tracking_id)
    if row_number:
        update_cells(sheet, row_number, {"Status": STATUS_OPTED_OUT})
        return "<p>You've been unsubscribed and won't receive further emails from us.</p>"
    return "<p>We couldn't find that subscription -- you're safe either way.</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
