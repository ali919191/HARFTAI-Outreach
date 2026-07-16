"""
send_and_followup.py

Run this once a day (via cron / Task Scheduler). For every lead in the
Google Sheet it decides whether to send the initial email or the next
follow-up, embeds an open-tracking pixel + unsubscribe link, and updates
the sheet with what it did.

It will NOT send to anyone marked Replied / Bounced - Hard / Opted Out /
No Response - Parked -- those are treated as closed out of the sequence.

Recommended order: run check_replies_bounces.py first (or make sure it
runs frequently throughout the day) so this script never follows up on
someone who already replied.
"""

import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import gspread

from common import (
    get_workbook, read_rows, update_cells, new_tracking_id, today_str,
    parse_date, days_from_now, ZOHO_EMAIL, ZOHO_APP_PASSWORD,
    ZOHO_SMTP_HOST, ZOHO_SMTP_PORT, SENDER_NAME, BUSINESS_ADDRESS,
    TRACKING_BASE_URL, FOLLOWUP_DAYS, MAX_STEPS, PARK_AFTER_DAYS,
    STATUS_NEW, STATUS_SENT_PREFIX, STATUS_PARKED, TERMINAL_STATUSES,
    SHEET_TAB_NAME, CAMPAIGN_COPY_COLUMNS,
)
from email_templates import STEP_TEMPLATES


def load_campaign_copy(sh):
    """Return {company_name: {'subject': ..., 0: body, 1: body, 2: body}}
    from the 'Campaign Copy' tab, or {} if that tab doesn't exist yet
    (e.g. generate_campaign_copy.py hasn't been run)."""
    try:
        ws = sh.worksheet("Campaign Copy")
    except gspread.WorksheetNotFound:
        return {}

    lookup = {}
    for row in ws.get_all_records(expected_headers=CAMPAIGN_COPY_COLUMNS):
        company = row.get("Company")
        if not company:
            continue
        lookup[company] = {
            "subject": row.get("Subject", ""),
            0: row.get("Email 1 (Day 1)", ""),
            1: row.get("Email 2 (Day 4)", ""),
            2: row.get("Email 3 (Day 9)", ""),
        }
    return lookup


def personalize(text, contact_name):
    """Fill in the [First name] / [Sender] placeholders left unresolved in
    Campaign Copy rows (they can't be resolved until send time, since the
    prospect's real contact name isn't known when the copy is generated)."""
    return (
        text.replace("[First name]", contact_name or "there")
            .replace("[Sender]", SENDER_NAME)
    )


def build_message(to_email, subject, body_text, tracking_id):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SENDER_NAME} <{ZOHO_EMAIL}>"
    msg["To"] = to_email

    unsubscribe_link = f"{TRACKING_BASE_URL}/unsubscribe/{tracking_id}"
    pixel = f'<img src="{TRACKING_BASE_URL}/open/{tracking_id}.png" width="1" height="1" style="display:none">'

    html_body = body_text.replace("\n", "<br>") + (
        '<br><br><hr style="border:none;border-top:1px solid #ddd">'
        f'<p style="font-size:11px;color:#888">{BUSINESS_ADDRESS}<br>'
        f'<a href="{unsubscribe_link}">Unsubscribe from these emails</a></p>'
        f"{pixel}"
    )

    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def send_email(msg, to_email):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(ZOHO_SMTP_HOST, ZOHO_SMTP_PORT, context=context) as server:
        server.login(ZOHO_EMAIL, ZOHO_APP_PASSWORD)
        server.sendmail(ZOHO_EMAIL, [to_email], msg.as_string())


def decide_action(row):
    """Return the step number (0, 1, 2, ...) to send now, or None to do nothing."""
    status = row["Status"] or STATUS_NEW

    if status in TERMINAL_STATUSES:
        return None
    if str(row["Replied"]).strip().upper() == "Y":
        return None

    if status == STATUS_NEW or status == "":
        return 0

    if status.startswith(STATUS_SENT_PREFIX):
        current_step = int(row["Sequence Step"] or 0)
        next_action = parse_date(row["Next Action Date"])
        if next_action and next_action.date() <= datetime.now().date():
            if current_step < MAX_STEPS:
                return current_step + 1

    return None


def mark_stale_as_parked(sheet, rows):
    """After the final follow-up has sat unanswered for PARK_AFTER_DAYS, move
    it out of the active pipeline so your dashboard reflects reality."""
    for row_number, row in rows:
        status = row["Status"] or ""
        if not status.startswith(STATUS_SENT_PREFIX):
            continue
        current_step = int(row["Sequence Step"] or 0)
        if current_step < MAX_STEPS:
            continue  # sequence isn't finished yet
        last_sent = parse_date(row["Last Sent Date"])
        if not last_sent:
            continue
        days_elapsed = (datetime.now() - last_sent).days
        if days_elapsed >= PARK_AFTER_DAYS:
            update_cells(sheet, row_number, {"Status": STATUS_PARKED})


def main():
    sh = get_workbook()
    sheet = sh.worksheet(SHEET_TAB_NAME)
    campaign_copy = load_campaign_copy(sh)
    rows = read_rows(sheet)

    sent_count = 0
    for row_number, row in rows:
        step = decide_action(row)
        if step is None:
            continue

        company_copy = campaign_copy.get(row["Company"])
        if company_copy and company_copy.get(step):
            # Personalized copy from the Campaign Copy tab (sector-specific,
            # hand-editable). This is the primary path once a lead has been
            # promoted from Prospects.
            subject = company_copy["subject"]
            body = personalize(company_copy[step], row["Contact Name"])
        else:
            # Legacy generic fallback -- used for leads with no matching
            # Campaign Copy row (e.g. manually added leads or old test rows).
            template = STEP_TEMPLATES.get(step)
            if not template:
                continue
            subject = template["subject"].format(company=row["Company"])
            body = template["body"].format(
                contact_name=row["Contact Name"] or "there",
                company=row["Company"],
                sender_name=SENDER_NAME,
            )

        tracking_id = row["Tracking ID"] or new_tracking_id()
        msg = build_message(row["Email"], subject, body, tracking_id)

        try:
            send_email(msg, row["Email"])
        except Exception as e:
            update_cells(sheet, row_number, {"Notes": f"Send failed: {e}"})
            continue

        next_action_date = (
            days_from_now(FOLLOWUP_DAYS[step]) if step < len(FOLLOWUP_DAYS) else ""
        )

        update_cells(sheet, row_number, {
            "Status": f"{STATUS_SENT_PREFIX} {step}",
            "Sequence Step": step,
            "Last Sent Date": today_str(),
            "Next Action Date": next_action_date,
            "Tracking ID": tracking_id,
        })
        sent_count += 1

    # second pass: park anything whose sequence finished with no response
    rows = read_rows(sheet)
    mark_stale_as_parked(sheet, rows)

    print(f"Done. Sent/followed-up {sent_count} email(s).")


if __name__ == "__main__":
    main()
