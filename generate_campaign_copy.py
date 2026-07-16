"""
generate_campaign_copy.py

Generates a personalized 3-email campaign for every prospect in the
'Prospects' tab and writes it into the 'Campaign Copy' tab.

Safe to re-run: it only adds rows for prospects that don't have a Campaign
Copy row yet (matched by ID). It will never overwrite a row that's already
there, so any hand-editing you do in the sheet afterward is permanent --
this script won't touch it again. To force a full regeneration for one
company, delete its row in Campaign Copy and re-run.

Usage:
    python generate_campaign_copy.py
"""

from common import get_workbook, ensure_worksheet, PROSPECT_COLUMNS, CAMPAIGN_COPY_COLUMNS
from email_templates import build_campaign


def main():
    sh = get_workbook()
    prospects_ws = sh.worksheet("Prospects")
    copy_ws = ensure_worksheet(sh, "Campaign Copy", CAMPAIGN_COPY_COLUMNS, rows=200)

    prospects = prospects_ws.get_all_records(expected_headers=PROSPECT_COLUMNS)
    existing_ids = {
        row["ID"] for row in copy_ws.get_all_records(expected_headers=CAMPAIGN_COPY_COLUMNS)
        if row.get("ID")
    }

    new_rows = []
    skipped = 0
    for p in prospects:
        pid = p.get("ID")
        if not pid or pid in existing_ids:
            continue
        try:
            subject, e1, e2, e3 = build_campaign(
                category=p["Category"],
                company=p["Company"],
                city=p["Area"],
                specialty=p["Specialty"],
                pain=p["Pain Hypothesis"],
            )
        except ValueError:
            skipped += 1
            continue
        new_rows.append([pid, p["Category"], p["Company"], subject, e1, e2, e3])

    if new_rows:
        copy_ws.append_rows(new_rows, value_input_option="RAW")
        print(f"Generated campaign copy for {len(new_rows)} new prospect(s).")
    else:
        print("No new prospects need campaign copy -- Campaign Copy tab is up to date.")
    if skipped:
        print(f"Skipped {skipped} prospect(s) with an unrecognized Category (no SECTOR_CONFIG entry).")


if __name__ == "__main__":
    main()
