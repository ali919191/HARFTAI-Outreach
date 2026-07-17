"""
promote_prospect.py

Promotes one researched prospect into the live send pipeline (the Outreach
tab that send_and_followup.py watches).

This is the one manual gate between "we found this company" and "we're
allowed to email them" -- it refuses to promote unless the prospect's row
in the Prospects tab already has a Contact Name, a Business Email, and
Consent Check set to "Confirmed".

Usage:
    python promote_prospect.py "Frio Air Systems"
"""

import sys

from common import (
    get_workbook, get_sheet, PROSPECT_COLUMNS, COLUMNS,
    PROSPECT_STATUS_PROMOTED, CONSENT_CONFIRMED,
)


def main():
    if len(sys.argv) < 2:
        print('Usage: python promote_prospect.py "Company Name"')
        sys.exit(1)
    company_name = sys.argv[1]

    sh = get_workbook()
    prospects_ws = sh.worksheet("Prospects")
    rows = prospects_ws.get_all_records(expected_headers=PROSPECT_COLUMNS)

    match = None
    match_row_number = None
    for i, row in enumerate(rows):
        if str(row.get("Company", "")).strip().lower() == company_name.strip().lower():
            match = row
            match_row_number = i + 2
            break

    if not match:
        print(f"No prospect found with company name: {company_name}")
        sys.exit(1)

    if not match.get("Contact Name") or not match.get("Business Email"):
        print("Cannot promote: Contact Name and Business Email must be filled in on the Prospects tab first.")
        sys.exit(1)

    if match.get("Consent Check") != CONSENT_CONFIRMED:
        print(f'Cannot promote: Consent Check must be "{CONSENT_CONFIRMED}" (currently "{match.get("Consent Check") or "(blank)"}").')
        sys.exit(1)

    outreach_ws = get_sheet()
    existing_records = outreach_ws.get_all_records(expected_headers=COLUMNS)
    existing_emails = {str(r.get("Email", "")).strip().lower() for r in existing_records}

    new_email = str(match["Business Email"]).strip().lower()
    if new_email in existing_emails:
        print("This email is already in the Outreach tab -- skipping duplicate.")
        sys.exit(1)

    new_row = ["" for _ in COLUMNS]
    new_row[COLUMNS.index("ID")] = str(match.get("ID", ""))
    new_row[COLUMNS.index("Company")] = match["Company"]
    new_row[COLUMNS.index("Contact Name")] = match["Contact Name"]
    new_row[COLUMNS.index("Email")] = match["Business Email"]
    outreach_ws.append_row(new_row, value_input_option="RAW")

    prospects_ws.update_cell(match_row_number, PROSPECT_COLUMNS.index("Status") + 1, PROSPECT_STATUS_PROMOTED)

    print(f"Promoted {match['Company']} into Outreach as a new lead. It will send on the next scheduled run.")


if __name__ == "__main__":
    main()
