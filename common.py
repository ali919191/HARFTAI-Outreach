"""
common.py
Shared configuration and Google Sheet helpers used by all three scripts.
"""

import os
import time
import uuid
from datetime import datetime, timedelta

import gspread
from gspread.exceptions import APIError
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
HARFT_PHONE = os.environ.get("HARFT_PHONE", "+1 832 847 7198")

GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
SHEET_TAB_NAME = os.environ.get("SHEET_TAB_NAME", "Outreach")

TRACKING_BASE_URL = os.environ["TRACKING_BASE_URL"].rstrip("/")

# Optional -- Hunter.io Email Finder (free tier: 50 credits/month). Leave
# unset to skip email-finding entirely; everything else still works.
HUNTER_API_KEY = os.environ.get("HUNTER_API_KEY", "")

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
# "ID" matches the Prospects/Campaign Copy ID for any lead that originated
# there (via sync_prospects.py or promote_prospect.py) -- this is the
# reliable key used to match a row to its Campaign Copy across tabs. Blank
# for rows added by hand with no Prospects entry (e.g. an ad-hoc test row);
# those fall back to matching by Company name instead.
COLUMNS = [
    "ID", "Company", "Research", "Contact Name", "Email", "Send Approval", "Status", "Sequence Step",
    "Last Sent Date", "Next Action Date", "Opens", "Last Open Date",
    "Replied", "Reply Date", "Bounce Type", "Tracking ID", "Notes",
]

# "Research" (Yes/No, default No): set to Yes on a manually-pasted row with
# just a Company name and nothing else -- the scheduled research pass looks
# for this flag and fills in Contact Name/Email using free sources only
# (never Apollo -- that requires live per-call confirmation an unattended
# run can't get). Never sends anything by itself.
RESEARCH_YES = "Yes"
RESEARCH_NO = "No"

# "Send Approval" (Yes/No, default No): the final human gate. Even a fully
# populated, correctly-sequenced row will NOT be sent by send_and_followup.py
# unless this is Yes. You flip this yourself after reviewing the Campaign
# Copy that would actually go out.
SEND_APPROVAL_YES = "Yes"
SEND_APPROVAL_NO = "No"

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
# Generated once by generate_campaign_copy.py / sync_prospects.py, then
# hand-editable (or Kai-editable) per company. send_and_followup.py reads
# directly from this tab (matched by ID, falling back to Company name for
# legacy rows with no ID) and only falls back to email_templates.STEP_TEMPLATES
# if a company has no row here yet.
CAMPAIGN_COPY_COLUMNS = [
    "ID", "Category", "Company", "Subject",
    "Email 1 (Day 1)", "Email 2 (Day 4)", "Email 3 (Day 9)", "Copy Status",
]

# "Copy Status" tracks whether a row's copy is still the raw generated
# template or has been enhanced/reviewed by a human or an external service
# (e.g. Kai, which is given direct Google Sheets access to read and rewrite
# email bodies here). New rows default to NEEDS_ENHANCEMENT if they used the
# generic (non-sector) fallback copy, or DRAFT otherwise -- see
# email_templates.SECTOR_CONFIG. send_and_followup.py will NOT send a row
# whose matched Campaign Copy entry isn't REVIEWED yet -- that's the final
# human checkpoint, same philosophy as Send Approval on Outreach. Rows with
# no Campaign Copy entry at all (legacy STEP_TEMPLATES fallback) are exempt
# from this gate and are governed only by Send Approval, as before.
COPY_STATUS_DRAFT = "Draft"
COPY_STATUS_NEEDS_ENHANCEMENT = "Needs Enhancement"
COPY_STATUS_ENHANCED = "Enhanced"
COPY_STATUS_REVIEWED = "Reviewed"
COPY_STATUS_VALUES = [COPY_STATUS_DRAFT, COPY_STATUS_NEEDS_ENHANCEMENT, COPY_STATUS_ENHANCED, COPY_STATUS_REVIEWED]


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


def _is_rate_limit_error(err: APIError) -> bool:
    response = getattr(err, "response", None)
    if response is not None and getattr(response, "status_code", None) == 429:
        return True
    return "RESOURCE_EXHAUSTED" in str(err) or "Quota exceeded" in str(err)


def _update_cell_with_retry(sheet, row_number, col, value, max_attempts=4, base_delay=5):
    """Google Sheets write quotas are per-minute and easy to hit when a batch
    of rows fires several update_cell() calls back to back. Retries a 429
    with exponential backoff (5s, 10s, 20s, ...) before giving up."""
    for attempt in range(1, max_attempts + 1):
        try:
            sheet.update_cell(row_number, col, value)
            return
        except APIError as e:
            if not _is_rate_limit_error(e) or attempt == max_attempts:
                raise
            time.sleep(base_delay * (2 ** (attempt - 1)))


def update_cells(sheet, row_number, updates: dict):
    """updates: {column_name: value}"""
    for name, value in updates.items():
        _update_cell_with_retry(sheet, row_number, col_index(name), value)


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
