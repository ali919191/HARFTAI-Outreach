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

# ---------------- Prospects tab schema ----------------
# Research/staging layer. Nothing here gets emailed automatically -- rows only
# become eligible for send_and_followup.py once promote_prospect.py copies
# them into the Outreach tab (which requires Contact Name + Business Email +
# a confirmed Consent Check first).
PROSPECT_COLUMNS = [
    "ID", "Category", "Company", "Area", "Website", "Specialty",
    "Pain Hypothesis", "Target Role", "Personalization Cue",
    "Contact Name", "Contact Title", "Business Email", "Contact Source",
    "Contact 2 Name", "Contact 2 Title", "Contact 2 Email",
    "Contact 3 Name", "Contact 3 Title", "Contact 3 Email",
    "Consent Check", "Status", "Next Action", "Notes",
]

# Primary contact is required to promote; Contact 2/3 are reference-only
# extra people found at the same company (e.g. an Apollo research pass),
# not separately emailable without their own promotion.

PROSPECT_STATUS_RESEARCH = "Research"
PROSPECT_STATUS_QUEUED = "Queued"
PROSPECT_STATUS_PROMOTED = "Promoted"
PROSPECT_STATUS_DNC = "Do Not Contact"
PROSPECT_STATUS_CLOSED = "Closed"

CONSENT_REQUIRED = "Required before send"
CONSENT_CONFIRMED = "Confirmed"
CONSENT_NONE = "No consent"
CONSENT_SUPPRESSED = "Suppressed"

# ---------------- Campaign Copy tab schema ----------------
# Generated once by generate_campaign_copy.py, then hand-editable per company.
# send_and_followup.py reads directly from this tab (matched by Company name)
# and only falls back to email_templates.STEP_TEMPLATES if a company has no
# row here yet.
CAMPAIGN_COPY_COLUMNS = [
    "ID", "Category", "Company", "Subject",
    "Email 1 (Day 1)", "Email 2 (Day 4)", "Email 3 (Day 9)",
]


def get_workbook():
    """Return the gspread Spreadsheet object (gives access to every tab,
    not just the Outreach tab that get_sheet() returns)."""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(GOOGLE_SHEET_ID)


def ensure_worksheet(sh, tab_name, headers, rows=200, cols=None):
    """Get a worksheet by name, creating it with a header row if missing.
    Leaves an existing tab untouched."""
    try:
        ws = sh.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab_name, rows=rows, cols=cols or max(len(headers), 1))
        if headers:
            ws.update("A1", [headers])
    return ws


def get_sheet():
    return get_workbook().worksheet(SHEET_TAB_NAME)


def col_letter(columns_list, name):
    """A1-notation column letter for a header name in a given columns list
    (e.g. col_letter(PROSPECT_COLUMNS, 'Status') -> 'U'). Use this instead of
    hardcoding letters -- schema changes then can't silently break formulas
    or validation ranges that reference a column by position."""
    idx = columns_list.index(name) + 1
    return gspread.utils.rowcol_to_a1(1, idx).rstrip("0123456789")


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
