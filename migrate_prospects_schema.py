"""
migrate_prospects_schema.py

One-time migration: rewrites the Prospects tab from the old 16-column
schema to the new 23-column schema (adds Contact Title, and Contact 2/3
Name+Title+Email for companies with more than one decision-maker found).

Safe to run because at the time this was written, no Prospects row had a
Contact Name or Business Email filled in yet -- there's no real contact
data to lose. It reads whatever's there under the OLD header names, and
rewrites it under the NEW layout. If you've already filled in some contact
info by hand before running this, it's preserved (Contact Name/Business
Email/Contact Source map straight across).

This is a one-shot script -- not meant to be re-run.

Usage:
    python migrate_prospects_schema.py
"""

from common import get_workbook, PROSPECT_COLUMNS

OLD_COLUMNS = [
    "ID", "Category", "Company", "Area", "Website", "Specialty",
    "Pain Hypothesis", "Target Role", "Personalization Cue",
    "Contact Name", "Business Email", "Contact Source",
    "Consent Check", "Status", "Next Action", "Notes",
]


def main():
    sh = get_workbook()
    ws = sh.worksheet("Prospects")

    header = ws.row_values(1)
    if header == PROSPECT_COLUMNS:
        print("Prospects tab is already on the new schema -- nothing to do.")
        return
    if header != OLD_COLUMNS:
        print("Prospects tab header doesn't match the expected old schema -- "
              "stopping without making changes so nothing gets scrambled. "
              f"Found: {header}")
        return

    old_rows = ws.get_all_records(expected_headers=OLD_COLUMNS)
    print(f"Read {len(old_rows)} row(s) under the old schema.")

    new_rows = []
    for row in old_rows:
        new_rows.append([
            row["ID"], row["Category"], row["Company"], row["Area"], row["Website"],
            row["Specialty"], row["Pain Hypothesis"], row["Target Role"], row["Personalization Cue"],
            row["Contact Name"], "", row["Business Email"], row["Contact Source"],
            "", "", "",  # Contact 2 Name/Title/Email
            "", "", "",  # Contact 3 Name/Title/Email
            row["Consent Check"], row["Status"], row["Next Action"], row["Notes"],
        ])

    ws.clear()
    ws.update(range_name="A1", values=[PROSPECT_COLUMNS] + new_rows)
    print(f"Migrated {len(new_rows)} row(s) to the new {len(PROSPECT_COLUMNS)}-column schema.")


if __name__ == "__main__":
    main()
