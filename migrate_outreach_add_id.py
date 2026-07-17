"""
migrate_outreach_add_id.py

One-time migration: adds an "ID" column as the new first column of the
Outreach tab, matching the Prospects/Campaign Copy ID for every row that
can be traced back to a Prospects company (matched by Company name, case-
insensitive -- the last time this codebase relies on name matching for
this). Rows with no match (e.g. a hand-added test row not in Prospects)
are left with a blank ID and are reported at the end so you can check them.

Preserves every existing row and column value exactly; only ID is added.

This is a one-shot script -- not meant to be re-run once the Outreach tab
is already on the new schema (it checks and exits cleanly if so).

Usage:
    python migrate_outreach_add_id.py
"""

from common import get_workbook, SHEET_TAB_NAME, COLUMNS, PROSPECT_COLUMNS

OLD_COLUMNS = [
    "Company", "Research", "Contact Name", "Email", "Send Approval", "Status", "Sequence Step",
    "Last Sent Date", "Next Action Date", "Opens", "Last Open Date",
    "Replied", "Reply Date", "Bounce Type", "Tracking ID", "Notes",
]


def main():
    sh = get_workbook()
    ws = sh.worksheet(SHEET_TAB_NAME)

    header = ws.row_values(1)
    if header == COLUMNS:
        print("Outreach tab already has the ID column -- nothing to do.")
        return
    if header != OLD_COLUMNS:
        print("Outreach tab header doesn't match the expected pre-ID schema -- "
              "stopping without making changes so nothing gets scrambled. "
              f"Found: {header}")
        return

    prospects = sh.worksheet("Prospects").get_all_records(expected_headers=PROSPECT_COLUMNS)
    id_by_company = {str(p["Company"]).strip().lower(): str(p["ID"]) for p in prospects if p.get("Company") and p.get("ID")}

    old_rows = ws.get_all_records(expected_headers=OLD_COLUMNS)
    print(f"Read {len(old_rows)} row(s) under the pre-ID schema.")

    new_rows = []
    unmatched = []
    for row in old_rows:
        company = str(row["Company"]).strip()
        pid = id_by_company.get(company.lower(), "")
        if not pid:
            unmatched.append(company)
        new_rows.append([
            pid,
            row["Company"], row["Research"], row["Contact Name"], row["Email"], row["Send Approval"],
            row["Status"], row["Sequence Step"], row["Last Sent Date"], row["Next Action Date"],
            row["Opens"], row["Last Open Date"], row["Replied"], row["Reply Date"],
            row["Bounce Type"], row["Tracking ID"], row["Notes"],
        ])

    ws.clear()
    # Clearing values doesn't clear stale per-cell number formats -- without
    # this, a column that used to hold dates can silently reformat a new
    # plain number into a date. Same fix as migrate_outreach_schema.py.
    ws.format(f"A2:{chr(ord('A') + len(COLUMNS) - 1)}1000", {"numberFormat": {"type": "TEXT"}})
    ws.update(range_name="A1", values=[COLUMNS] + new_rows, value_input_option="USER_ENTERED")
    print(f"Migrated {len(new_rows)} row(s) to the new {len(COLUMNS)}-column schema (ID added as column A).")

    if unmatched:
        print(f"\n{len(unmatched)} row(s) had no matching Prospects ID (left blank -- likely added by hand, not via Prospects):")
        for c in unmatched:
            print(f"  {c}")


if __name__ == "__main__":
    main()
