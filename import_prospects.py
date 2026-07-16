"""
import_prospects.py

One-time (safe to re-run) import of prospects_data.py into the 'Prospects'
tab. Existing prospects (matched by ID) are left untouched -- re-running
this only adds prospects that aren't there yet, so it's safe to add more
companies to prospects_data.py later and re-run.

Usage:
    python import_prospects.py
"""

from common import (
    get_workbook, ensure_worksheet, PROSPECT_COLUMNS,
    PROSPECT_STATUS_RESEARCH, CONSENT_REQUIRED,
)
from email_templates import SECTOR_CONFIG
from prospects_data import PROSPECTS


def main():
    sh = get_workbook()
    ws = ensure_worksheet(sh, "Prospects", PROSPECT_COLUMNS, rows=max(200, len(PROSPECTS) + 10))

    existing_ids = set()
    existing_records = ws.get_all_records(expected_headers=PROSPECT_COLUMNS)
    for row in existing_records:
        if row.get("ID"):
            existing_ids.add(str(row["ID"]))

    new_rows = []
    for i, p in enumerate(PROSPECTS):
        prospect_id = str(i + 1).zfill(3)
        if prospect_id in existing_ids:
            continue

        category, company, city, url, specialty, pain = p
        role = SECTOR_CONFIG.get(category, {}).get("role", "")
        cue = f"{specialty}; {city}"

        new_rows.append([
            prospect_id, category, company, city, url, specialty, pain,
            role, cue,
            "", "", "",  # Contact Name, Business Email, Contact Source -- filled in by research
            CONSENT_REQUIRED,
            PROSPECT_STATUS_RESEARCH,
            "Find decision maker and validate contact",
            "",
        ])

    if new_rows:
        ws.append_rows(new_rows, value_input_option="RAW")
        print(f"Added {len(new_rows)} new prospect(s) to the Prospects tab.")
    else:
        print("No new prospects to add -- Prospects tab is already up to date.")


if __name__ == "__main__":
    main()
