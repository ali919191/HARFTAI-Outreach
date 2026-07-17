"""
setup_reporting_tabs.py

One-time setup for the 'Dashboard', 'HARFT Brief', and 'Lists' tabs,
recreating the reporting/reference layer from the old local-Excel tracker
inside the same Google Sheet.

Safe to re-run: each tab is only populated if it's currently empty, so this
won't stomp on anything you've since customized in the sheet.

Usage:
    python setup_reporting_tabs.py
"""

from gspread.utils import ValidationConditionType

from common import get_workbook, ensure_worksheet, col_letter, PROSPECT_COLUMNS, COLUMNS, CAMPAIGN_COPY_COLUMNS, COPY_STATUS_VALUES
from setup_outreach_formatting import COLORS, _rule


def setup_dashboard(sh):
    """Always refreshes the title/headers/formulas (no user data lives here,
    it's all computed) -- so this stays correct even if Prospects columns
    move around later."""
    ws = ensure_worksheet(sh, "Dashboard", [], rows=20, cols=8)

    company_col = col_letter(PROSPECT_COLUMNS, "Company")
    email_col = col_letter(PROSPECT_COLUMNS, "Business Email")
    prospect_status_col = col_letter(PROSPECT_COLUMNS, "Status")
    outreach_status_col = col_letter(COLUMNS, "Status")
    replied_col = col_letter(COLUMNS, "Replied")

    ws.update(range_name="A1", values=[["HARFT AI — Houston Outreach Command Center"]])
    ws.update(range_name="A3", values=[[
        "Prospects", "Researched (has email)", "Promoted", "Do Not Contact",
        "Sent", "Replied", "Bounced", "Parked",
    ]])
    ws.update(range_name="A4", values=[[
        f"=COUNTA(Prospects!{company_col}2:{company_col}1000)",
        f"=COUNTIF(Prospects!{email_col}2:{email_col}1000,\"?*\")",
        f"=COUNTIF(Prospects!{prospect_status_col}2:{prospect_status_col}1000,\"Promoted\")",
        f"=COUNTIF(Prospects!{prospect_status_col}2:{prospect_status_col}1000,\"Do Not Contact\")",
        f"=COUNTIF(Outreach!{outreach_status_col}2:{outreach_status_col}1000,\"Sent*\")",
        f"=COUNTIF(Outreach!{replied_col}2:{replied_col}1000,\"Y\")",
        f"=COUNTIF(Outreach!{outreach_status_col}2:{outreach_status_col}1000,\"Bounced*\")",
        f"=COUNTIF(Outreach!{outreach_status_col}2:{outreach_status_col}1000,\"No Response - Parked\")",
    ]], value_input_option="USER_ENTERED")
    ws.format("A1:H1", {"textFormat": {"bold": True, "fontSize": 14}})
    ws.format("A3:H3", {"textFormat": {"bold": True}, "wrapStrategy": "WRAP"})
    print("Dashboard tab refreshed.")


def setup_brief(sh):
    ws = ensure_worksheet(sh, "HARFT Brief", [], rows=20, cols=2)
    if ws.acell("A1").value:
        print("HARFT Brief already set up -- leaving it alone.")
        return

    rows = [
        ["Positioning", "Managed AI operations partner: designs, deploys, manages, monitors, and continuously improves AI inside the client's current software."],
        ["Core outcome", "More booked work and captured leads, faster service, and less manual office load -- without requiring a software switch."],
        ["What it runs", "Calls, lead qualification, appointment booking, follow-up, scheduling, dispatch, reporting, documentation, and internal knowledge."],
        ["Operating model", "Design -> Deploy -> Manage -> Optimize; human escalation oversight remains available for edge cases."],
        ["Compatibility", "Works with ServiceTitan, Jobber, HubSpot, Salesforce, GoHighLevel, Housecall Pro, Microsoft 365, Google Workspace, QuickBooks, and more."],
        ["Trust points", "24/7 call coverage; interactions logged and reviewable; security controls include MFA, RBAC, encryption, audit logging, vendor management, and incident response."],
        ["Primary CTA", "Get a personalized AI plan / book a strategy call."],
        ["Email guardrail", "Avoid ROI guarantees. Treat each listed pain point as a hypothesis to validate in discovery."],
        ["Outreach compliance", "Use confirmed business contacts, accurate sender and physical address, a working opt-out, and maintain a suppression list. Review applicable CAN-SPAM, Texas, HIPAA, and legal-marketing obligations before sending."],
    ]
    ws.update(range_name="A1", values=rows)
    ws.format("A1:A9", {"textFormat": {"bold": True}, "verticalAlignment": "TOP"})
    ws.format("B1:B9", {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"})
    print("HARFT Brief tab created.")


def setup_lists(sh):
    ws = ensure_worksheet(sh, "Lists", [], rows=20, cols=3)
    if ws.acell("A1").value:
        print("Lists already set up -- leaving it alone.")
        return

    ws.update(range_name="A1", values=[["Prospect Status", "Consent / suppression", "Sequence timing"]])
    ws.update(range_name="A2", values=[
        ["Research", "Required before send", "Day 1 -- Initial"],
        ["Queued", "Confirmed", "Day 4 -- Follow-up"],
        ["Promoted", "No consent", "Day 9 -- Close loop"],
        ["Do Not Contact", "Suppressed", ""],
        ["Closed", "", ""],
    ])
    ws.format("A1:C1", {"textFormat": {"bold": True}})
    print("Lists tab created.")


def setup_prospect_validation(sh):
    """Dropdowns on the Prospects tab for Status and Consent Check."""
    ws = sh.worksheet("Prospects")
    status_col = col_letter(PROSPECT_COLUMNS, "Status")
    consent_col = col_letter(PROSPECT_COLUMNS, "Consent Check")
    ws.add_validation(
        f"{status_col}2:{status_col}1000",
        ValidationConditionType.one_of_list,
        ["Research", "Queued", "Promoted", "Do Not Contact", "Closed"],
        showCustomUi=True,
    )
    ws.add_validation(
        f"{consent_col}2:{consent_col}1000",
        ValidationConditionType.one_of_list,
        ["Required before send", "Confirmed", "No consent", "Suppressed"],
        showCustomUi=True,
    )
    print(f"Prospects tab dropdowns set up (Status={status_col}, Consent Check={consent_col}).")


def setup_campaign_copy_validation(sh):
    """Dropdown + color-coding for the Copy Status column on Campaign Copy,
    so Kai's (or a human's) progress through Draft -> Needs Enhancement ->
    Enhanced -> Reviewed is visible at a glance. Safe to re-run: clears any
    conditional format rules this function previously added before re-adding."""
    ws = sh.worksheet("Campaign Copy")
    sheet_id = ws.id
    status_col = col_letter(CAMPAIGN_COPY_COLUMNS, "Copy Status")

    ws.add_validation(
        f"{status_col}2:{status_col}1000",
        ValidationConditionType.one_of_list,
        COPY_STATUS_VALUES,
        showCustomUi=True,
    )

    meta = sh.fetch_sheet_metadata()
    existing_rule_count = 0
    for s in meta["sheets"]:
        if s["properties"]["sheetId"] == sheet_id:
            existing_rule_count = len(s.get("conditionalFormats", []))
            break
    requests = [
        {"deleteConditionalFormatRule": {"sheetId": sheet_id, "index": 0}}
        for _ in range(existing_rule_count)
    ]

    idx = CAMPAIGN_COPY_COLUMNS.index("Copy Status")
    status_range = {"sheetId": sheet_id, "startRowIndex": 1, "startColumnIndex": idx, "endColumnIndex": idx + 1}
    requests += [
        _rule(status_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Reviewed"}]}, COLORS["green"], COLORS["green_text"]),
        _rule(status_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Needs Enhancement"}]}, COLORS["red"], COLORS["red_text"]),
        _rule(status_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Enhanced"}]}, COLORS["blue"], COLORS["blue_text"]),
        _rule(status_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Draft"}]}, COLORS["gray"], COLORS["gray_text"]),
    ]
    sh.batch_update({"requests": requests})
    print(f"Campaign Copy tab: Copy Status dropdown + color-coding set up (column {status_col}).")


def main():
    sh = get_workbook()
    setup_dashboard(sh)
    setup_brief(sh)
    setup_lists(sh)
    try:
        setup_prospect_validation(sh)
    except Exception as e:
        print(f"Skipped dropdown setup (Prospects tab may not exist yet): {e}")
    try:
        setup_campaign_copy_validation(sh)
    except Exception as e:
        print(f"Skipped Campaign Copy dropdown setup (tab may not exist yet): {e}")


if __name__ == "__main__":
    main()
