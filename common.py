"""
common.py
Shared configuration and Google Sheet helpers used by all three scripts.
"""

import os
import uuid
from datetime import datetime, timedelta

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# ---------------- Config (from .env) ----------------
ZOHO_EMAIL = os.environ["ZOHO_EMAIL"]
ZOHO_APP_PASSWORD = os.environ["ZOHO_APP_PASSWORD"]
ZOHO_SMTP_HOST = os.environ.get("ZOHO_SMTP_HOST", "smtp.zoho.com")
ZOHO_SMTP_PORT = int(os.environ.get("ZOHO_SMTP_PORT", 465))
ZOHO_IMAP_HOST = os.environ.get("ZOHO_IMAP_HOST", "imap.zoho.com")
ZOHO_IMAP_PORT = int(os.environ.get("ZOHO_IMAP_PORT", 993))

SENDER_NAME = os.environ.get("SENDER_NAME", "Ali Syed")
BUSINESS_ADDRESS = os.environ.get("BUSINESS_ADDRESS", "HARFT AI, Houston, TX")

GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
SHEET_TAB_NAME = os.environ.get("SHEET_TAB_NAME", "Outreach")

TRACKING_BASE_URL = os.environ["TRACKING_BASE_URL"].rstrip("/")

# Wait times BETWEEN touches, not absolute days from the first email.
# e.g. "4,9" = follow-up #1 four days after the initial email (if no reply),
# follow-up #2 nine days after follow-up #1 (if still no reply).
FOLLOWUP_DAYS = [int(x) for x in os.environ.get("FOLLOWUP_DAYS", "4,9").split(",")]
MAX_STEPS = len(FOLLOWUP_DAYS)  # number of follow-ups after the initial send

# How many days after the final follow-up (with no reply) before we stop
# showing it as "Sent" and mark it Parked so it's out of your active pipeline.
PARK_AFTER_DAYS = int(os.environ.get("PARK_AFTER_DAYS", 5))

# ---------------- Sheet schema ----------------
# This exact header row (in this order) must exist in row 1 of your sheet.
COLUMNS = [
    "Company", "Contact Name", "Email", "Status", "Sequence Step",
    "Last Sent Date", "Next Action Date", "Opens", "Last Open Date",
    "Replied", "Reply Date", "Bounce Type", "Tracking ID", "Notes",
]

STATUS_NEW = "New"
STATUS_SENT_PREFIX = "Sent - Step"
STATUS_REPLIED = "Replied"
STATUS_BOUNCED_HARD = "Bounced - Hard"
STATUS_BOUNCED_SOFT = "Bounced - Soft"
STATUS_OPTED_OUT = "Opted Out"
STATUS_PARKED = "No Response - Parked"

TERMINAL_STATUSES = {STATUS_REPLIED, STATUS_BOUNCED_HARD, STATUS_OPTED_OUT, STATUS_PARKED}


def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(GOOGLE_SHEET_ID)
    return sh.worksheet(SHEET_TAB_NAME)


def col_index(name):
    """1-indexed column number for a given header name."""
    return COLUMNS.index(name) + 1


def read_rows(sheet):
    """Return [(row_number, row_dict), ...] -- row 1 is the header, so data starts at row 2."""
    records = sheet.get_all_records(expected_headers=COLUMNS)
    return [(i + 2, row) for i, row in enumerate(records)]


def update_cells(sheet, row_number, updates: dict):
    """updates: {column_name: value}"""
    for name, value in updates.items():
        sheet.update_cell(row_number, col_index(name), value)


def new_tracking_id():
    return uuid.uuid4().hex[:12]


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(str(s), "%Y-%m-%d")
    except ValueError:
        return None


def days_from_now(n):
    return (datetime.now() + timedelta(days=n)).strftime("%Y-%m-%d")
