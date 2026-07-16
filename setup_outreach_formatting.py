"""
setup_outreach_formatting.py

Adds color-coded conditional formatting to the Outreach tab so pipeline
state is visible at a glance, without opening each row.

What gets colored (all of this is real, sender-visible signal):
    Status column
        Sent...        -> yellow  (accepted by Zoho's SMTP server)
        Bounced...     -> red     (hard: bad address / soft: mailbox full, temp issue)
        Replied        -> green   (a message from that address landed in your inbox)
        Opted Out      -> gray    (clicked unsubscribe)
        No Response - Parked -> gray (sequence finished, no reply -- closest
                                       available proxy for "likely filtered
                                       or ignored")
    Opens column
        > 0            -> light blue (tracking pixel fired at least once --
                                       approximate, see README)
    Research column
        Yes             -> light blue (queued for the automatic research pass)
    Send Approval column
        Yes             -> green  (cleared to send)
        No              -> gray   (default -- nothing will be sent)

What will NEVER be colored, because no sender-side tool -- not this one,
not Gmail, not HubSpot, not Mailchimp -- can see it: whether a message was
actually delivered into the inbox (vs. silently dropped), marked as spam,
or deleted. That happens entirely inside the recipient's mailbox.

Safe to re-run: it removes any conditional format rules this script
previously added to the Outreach tab before re-adding them, so re-running
never piles up duplicates. It does not touch rules you've added yourself
in the Sheets UI on other tabs.

Usage:
    python setup_outreach_formatting.py
"""

from gspread.utils import ValidationConditionType

from common import get_workbook, SHEET_TAB_NAME, COLUMNS, col_letter

COLORS = {
    "green": {"red": 0.867, "green": 0.953, "blue": 0.910},
    "green_text": {"red": 0.090, "green": 0.420, "blue": 0.282},
    "red": {"red": 0.988, "green": 0.890, "blue": 0.882},
    "red_text": {"red": 0.635, "green": 0.169, "blue": 0.133},
    "gray": {"red": 0.933, "green": 0.933, "blue": 0.933},
    "gray_text": {"red": 0.4, "green": 0.4, "blue": 0.4},
    "yellow": {"red": 1.0, "green": 0.969, "blue": 0.867},
    "yellow_text": {"red": 0.396, "green": 0.290, "blue": 0.0},
    "blue": {"red": 0.890, "green": 0.941, "blue": 0.988},
    "blue_text": {"red": 0.090, "green": 0.463, "blue": 0.824},
}


def _rule(range_, condition, bg, fg):
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [range_],
                "booleanRule": {
                    "condition": condition,
                    "format": {
                        "backgroundColor": bg,
                        "textFormat": {"foregroundColor": fg, "bold": True},
                    },
                },
            },
            "index": 0,
        }
    }


def main():
    sh = get_workbook()
    ws = sh.worksheet(SHEET_TAB_NAME)
    sheet_id = ws.id

    # Clear any conditional formats already on this sheet before re-adding,
    # so re-running this script doesn't stack duplicate rules.
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

    def col_range(name):
        idx = COLUMNS.index(name)
        return {"sheetId": sheet_id, "startRowIndex": 1, "startColumnIndex": idx, "endColumnIndex": idx + 1}

    status_range = col_range("Status")
    opens_range = col_range("Opens")
    research_range = col_range("Research")
    approval_range = col_range("Send Approval")

    requests += [
        _rule(status_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Replied"}]}, COLORS["green"], COLORS["green_text"]),
        _rule(status_range, {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "Bounced"}]}, COLORS["red"], COLORS["red_text"]),
        _rule(status_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Opted Out"}]}, COLORS["gray"], COLORS["gray_text"]),
        _rule(status_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "No Response - Parked"}]}, COLORS["gray"], COLORS["gray_text"]),
        _rule(status_range, {"type": "TEXT_STARTS_WITH", "values": [{"userEnteredValue": "Sent"}]}, COLORS["yellow"], COLORS["yellow_text"]),
        _rule(opens_range, {"type": "NUMBER_GREATER", "values": [{"userEnteredValue": "0"}]}, COLORS["blue"], COLORS["blue_text"]),
        _rule(research_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Yes"}]}, COLORS["blue"], COLORS["blue_text"]),
        _rule(approval_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Yes"}]}, COLORS["green"], COLORS["green_text"]),
        _rule(approval_range, {"type": "TEXT_EQ", "values": [{"userEnteredValue": "No"}]}, COLORS["gray"], COLORS["gray_text"]),
    ]

    sh.batch_update({"requests": requests})
    added = len(requests) - existing_rule_count
    print(f"Applied {added} conditional formatting rule(s) to {SHEET_TAB_NAME} (replaced {existing_rule_count} old rule(s), if any).")

    # Yes/No dropdowns for Research and Send Approval.
    research_col = col_letter(COLUMNS, "Research")
    approval_col = col_letter(COLUMNS, "Send Approval")
    ws.add_validation(
        f"{research_col}2:{research_col}1000",
        ValidationConditionType.one_of_list,
        ["Yes", "No"],
        showCustomUi=True,
    )
    ws.add_validation(
        f"{approval_col}2:{approval_col}1000",
        ValidationConditionType.one_of_list,
        ["Yes", "No"],
        showCustomUi=True,
    )
    print(f"Dropdowns added (Research={research_col}, Send Approval={approval_col}).")


if __name__ == "__main__":
    main()
