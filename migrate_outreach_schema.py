"""
migrate_outreach_schema.py

One-time migration: rewrites the Outreach tab from the old 14-column schema
to the new 16-column schema (adds Research after Company, Send Approval
after Email).

Preserves existing rows exactly (e.g. Test Co 1's real send history).
For any row that already has Status starting with "Sent" (i.e. it already
went out before this gate existed), Send Approval is set to Yes so its
in-flight follow-ups aren't retroactively blocked. Every other row gets
Send Approval = No and Research = No, matching the new defaults.

This is a one-shot script -- not meant to be re-run.

Usage:
    python migrate_outreach_schema.py
"""

from common import get_workbook, SHEET_TAB_NAME, COLUMNS, STATUS_SENT_PREFIX

OLD_COLUMNS = [
    "Company", "Contact Name", "Email", "Status", "Sequence Step",
    "Last Sent Date", "Next Action Date", "Opens", "Last Open Date",
    "Replied", "Reply Date", "Bounce Type", "Tracking ID", "Notes",
]


def main():
    sh = get_workbook()
    ws = sh.worksheet(SHEET_TAB_NAME)

    header = ws.row_values(1)
    if header == COLUMNS:
        print("Outreach tab is already on the new schema -- nothing to do.")
        return
    if header != OLD_COLUMNS:
        print("Outreach tab header doesn't match the expected old schema -- "
              "stopping without making changes so nothing gets scrambled. "
              f"Found: {header}")
        return

    old_rows = ws.get_all_records(expected_headers=OLD_COLUMNS)
    print(f"Read {len(old_rows)} row(s) under the old schema.")

    new_rows = []
    for row in old_rows:
        already_sent = str(row["Status"] or "").startswith(STATUS_SENT_PREFIX) or row["Status"] in ("Replied",)
        new_rows.append([
            row["Company"],
            "No",  # Research
            row["Contact Name"],
            row["Email"],
            "Yes" if already_sent else "No",  # Send Approval
            row["Status"], row["Sequence Step"],
            row["Last Sent Date"], row["Next Action Date"], row["Opens"], row["Last Open Date"],
            row["Replied"], row["Reply Date"], row["Bounce Type"], row["Tracking ID"], row["Notes"],
        ])

    ws.clear()
    # Clearing values doesn't clear stale per-cell number formats -- without
    # this, a column that used to hold dates can silently reformat a new
    # plain number (e.g. Sequence Step = 0) into a date like "1899-12-30".
    ws.format(f"A2:{chr(ord('A') + len(COLUMNS) - 1)}1000", {"numberFormat": {"type": "TEXT"}})
    ws.update(range_name="A1", values=[COLUMNS] + new_rows, value_input_option="USER_ENTERED")
    print(f"Migrated {len(new_rows)} row(s) to the new {len(COLUMNS)}-column schema.")


if __name__ == "__main__":
    main()
