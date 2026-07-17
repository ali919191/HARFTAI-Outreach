"""
find_emails.py

For every Prospects row that has a Contact Name but no Business Email,
tries Hunter.io's Email Finder to find a verified email at the company's
domain. Only accepts results at or above HUNTER_MIN_CONFIDENCE (70) --
anything lower is left blank rather than risk a bad address hitting your
Zoho sending reputation.

If a matching Company also exists in Outreach, its Email cell is updated
too, so both tabs stay in sync.

Safe to re-run: only processes rows still missing an email, so it won't
re-spend credits on companies it already resolved.

Requires HUNTER_API_KEY in .env (free tier: 50 credits/month, no card
required -- see README for how to get one). Does nothing if it's unset.

Usage:
    python find_emails.py
"""

from common import get_workbook, PROSPECT_COLUMNS, COLUMNS, SHEET_TAB_NAME, HUNTER_API_KEY
from hunter_email_finder import find_email, domain_from_url, HUNTER_MIN_CONFIDENCE


def main():
    if not HUNTER_API_KEY:
        print("HUNTER_API_KEY not set in .env -- nothing to do. See README for setup steps.")
        return

    sh = get_workbook()
    pros_ws = sh.worksheet("Prospects")
    pros_rows = pros_ws.get_all_records(expected_headers=PROSPECT_COLUMNS)

    out_ws = sh.worksheet(SHEET_TAB_NAME)
    out_rows = out_ws.get_all_records(expected_headers=COLUMNS)
    out_row_by_company = {r["Company"]: i + 2 for i, r in enumerate(out_rows) if r.get("Company")}

    checked = 0
    found = 0
    for i, row in enumerate(pros_rows):
        if not row.get("Contact Name") or row.get("Business Email"):
            continue
        domain = domain_from_url(row.get("Website"))
        if not domain:
            continue

        checked += 1
        email, score = find_email(row["Contact Name"], domain, HUNTER_API_KEY)
        row_number = i + 2

        if email:
            pros_ws.update_cell(row_number, PROSPECT_COLUMNS.index("Business Email") + 1, email)
            existing_source = row.get("Contact Source", "") or ""
            new_source = f"{existing_source} | Email via Hunter.io (confidence {score}%)".strip(" |")
            pros_ws.update_cell(row_number, PROSPECT_COLUMNS.index("Contact Source") + 1, new_source)
            found += 1
            print(f"Found: {row['Company']} -> {email} (confidence {score}%)")

            company = row["Company"]
            if company in out_row_by_company:
                out_ws.update_cell(out_row_by_company[company], COLUMNS.index("Email") + 1, email)
        else:
            print(f"No confident (>={HUNTER_MIN_CONFIDENCE}%) match: {row['Company']}")

    print(f"\nChecked {checked} contact(s) with a known name, found {found} email(s) at/above {HUNTER_MIN_CONFIDENCE}% confidence.")


if __name__ == "__main__":
    main()
