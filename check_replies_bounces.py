"""
check_replies_bounces.py

Run this frequently (e.g. every 30-60 min via cron) to scan the Zoho
inbox for:
  - Replies from leads on the sheet -> marks Replied = Y, Status = Replied,
    which stops the sequence for that lead.
  - Bounce notifications (from mailer-daemon/postmaster) -> marks
    Bounced - Hard or Bounced - Soft based on the bounce reason in the
    message body.

IMPORTANT LIMITATION: this can only see what lands in YOUR inbox --
actual replies and bounce/NDR notices. It cannot see whether a recipient
marked your email as spam or moved it to trash on their end. No sender-
side tool (not Zoho, Gmail, HubSpot, Mailchimp, etc.) has visibility into
that -- it happens entirely inside the recipient's own mailbox.
"""

import imaplib
import email
from email.header import decode_header

from common import (
    get_sheet, read_rows, update_cells, today_str,
    STATUS_REPLIED, STATUS_BOUNCED_HARD, STATUS_BOUNCED_SOFT,
    ZOHO_EMAIL, ZOHO_APP_PASSWORD, ZOHO_IMAP_HOST, ZOHO_IMAP_PORT,
)

HARD_BOUNCE_HINTS = ["user unknown", "no such user", "550", "does not exist", "invalid recipient", "address rejected"]
SOFT_BOUNCE_HINTS = ["mailbox full", "451", "452", "try again later", "temporarily deferred", "quota exceeded"]


def decode_str(value):
    if value is None:
        return ""
    parts = decode_header(value)
    out = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            out += text.decode(enc or "utf-8", errors="ignore")
        else:
            out += text
    return out


def get_body_text(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    continue
        return ""
    try:
        return msg.get_payload(decode=True).decode(errors="ignore")
    except Exception:
        return ""


def classify_bounce(body_text):
    lower = body_text.lower()
    if any(hint in lower for hint in HARD_BOUNCE_HINTS):
        return STATUS_BOUNCED_HARD
    if any(hint in lower for hint in SOFT_BOUNCE_HINTS):
        return STATUS_BOUNCED_SOFT
    return STATUS_BOUNCED_SOFT  # default to soft/retryable if the reason is unclear


def main():
    sheet = get_sheet()
    rows = read_rows(sheet)
    by_email = {
        row["Email"].strip().lower(): (row_number, row)
        for row_number, row in rows if row.get("Email")
    }

    imap = imaplib.IMAP4_SSL(ZOHO_IMAP_HOST, ZOHO_IMAP_PORT)
    imap.login(ZOHO_EMAIL, ZOHO_APP_PASSWORD)
    imap.select("INBOX")

    status, data = imap.search(None, "UNSEEN")
    ids = data[0].split()

    for msg_id in ids:
        status, msg_data = imap.fetch(msg_id, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        from_addr = decode_str(msg.get("From", "")).lower()
        subject = decode_str(msg.get("Subject", "")).lower()
        body_text = get_body_text(msg)

        is_bounce = (
            "mailer-daemon" in from_addr
            or "postmaster" in from_addr
            or "delivery status notification" in subject
            or "undelivered mail" in subject
            or "returned to sender" in subject
            or "failure notice" in subject
        )

        if is_bounce:
            matched_email = next((e for e in by_email if e in body_text.lower()), None)
            if matched_email:
                row_number, row = by_email[matched_email]
                bounce_type = classify_bounce(body_text)
                update_cells(sheet, row_number, {
                    "Status": bounce_type,
                    "Bounce Type": bounce_type.replace("Bounced - ", ""),
                    "Notes": f"Bounce detected {today_str()}",
                })
            continue

        matched = next((e for e in by_email if e in from_addr), None)
        if matched:
            row_number, row = by_email[matched]
            update_cells(sheet, row_number, {
                "Status": STATUS_REPLIED,
                "Replied": "Y",
                "Reply Date": today_str(),
            })

    imap.close()
    imap.logout()
    print(f"Checked {len(ids)} unseen message(s).")


if __name__ == "__main__":
    main()
