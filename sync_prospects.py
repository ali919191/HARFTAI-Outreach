"""
sync_prospects.py

Watches the Prospects tab for any company that isn't in Outreach yet and
automatically:
  1. Adds it to Outreach as a new row -- Research is set to "No" if the
     Prospects row already has both a Contact Name and a Business Email
     (nothing left to look up), or "Yes" if either is missing (the
     scheduled research pass will fill in what's missing via free sources,
     then Hunter.io for a verified email).
  2. Generates its personalized 3-email Campaign Copy sequence (sector-aware
     via SECTOR_CONFIG, or a generic fallback if the Category isn't one of
     the configured verticals), so the copy is ready to review the moment
     the lead shows up in Outreach.

Nothing here ever sends an email or touches Send Approval -- that stays
"No" by default and is the one thing you flip yourself after reviewing the
Campaign Copy that would go out.

Safe to re-run: only acts on Prospects companies not already present in
Outreach (matched by Prospects ID -- the reliable key now carried through
Prospects -> Outreach -> Campaign Copy; falls back to Company name only for
legacy rows added by hand with no ID) and only adds Campaign Copy rows that
don't already exist (matched by Prospects ID).

Usage:
    python sync_prospects.py                  # sync every new Prospects row
    python sync_prospects.py "Townsquare Media"   # sync just one company
"""

import sys

from common import (
    get_workbook, ensure_worksheet, PROSPECT_COLUMNS, COLUMNS, CAMPAIGN_COPY_COLUMNS,
    SHEET_TAB_NAME, RESEARCH_YES, RESEARCH_NO, SEND_APPROVAL_NO,
    COPY_STATUS_DRAFT, COPY_STATUS_NEEDS_ENHANCEMENT,
)
from email_templates import build_campaign, SECTOR_CONFIG


def main():
    only_company = sys.argv[1].strip().lower() if len(sys.argv) > 1 else None

    sh = get_workbook()
    prospects_ws = sh.worksheet("Prospects")
    outreach_ws = sh.worksheet(SHEET_TAB_NAME)
    copy_ws = ensure_worksheet(sh, "Campaign Copy", CAMPAIGN_COPY_COLUMNS, rows=200)

    prospects = prospects_ws.get_all_records(expected_headers=PROSPECT_COLUMNS)
    outreach_rows = outreach_ws.get_all_records(expected_headers=COLUMNS)
    existing_ids = {str(r.get("ID", "")).strip() for r in outreach_rows if r.get("ID")}
    # Fallback for rows with no ID yet (shouldn't normally happen post-migration,
    # but keeps this safe against hand-added rows that share a company name).
    existing_companies = {str(r.get("Company", "")).strip().lower() for r in outreach_rows if r.get("Company") and not r.get("ID")}

    copy_rows = copy_ws.get_all_records(expected_headers=CAMPAIGN_COPY_COLUMNS)
    existing_copy_ids = {str(r.get("ID", "")) for r in copy_rows if r.get("ID")}

    new_outreach_rows = []
    new_copy_rows = []
    summary = []

    for p in prospects:
        company = str(p.get("Company", "")).strip()
        pid = str(p.get("ID", "")).strip()
        if not company:
            continue
        if pid and pid in existing_ids:
            continue
        if not pid and company.lower() in existing_companies:
            continue
        if only_company and company.lower() != only_company:
            continue

        contact_name = str(p.get("Contact Name", "")).strip()
        email = str(p.get("Business Email", "")).strip()
        research = RESEARCH_NO if (contact_name and email) else RESEARCH_YES

        row = ["" for _ in COLUMNS]
        row[COLUMNS.index("ID")] = pid
        row[COLUMNS.index("Company")] = company
        row[COLUMNS.index("Research")] = research
        row[COLUMNS.index("Contact Name")] = contact_name
        row[COLUMNS.index("Email")] = email
        row[COLUMNS.index("Send Approval")] = SEND_APPROVAL_NO
        new_outreach_rows.append(row)
        if pid:
            existing_ids.add(pid)
        else:
            existing_companies.add(company.lower())

        has_copy = True
        if pid and pid not in existing_copy_ids:
            subject, e1, e2, e3 = build_campaign(
                category=p.get("Category", ""),
                company=company,
                city=p.get("Area", ""),
                specialty=p.get("Specialty", ""),
                pain=p.get("Pain Hypothesis", ""),
            )
            status = COPY_STATUS_DRAFT if p.get("Category") in SECTOR_CONFIG else COPY_STATUS_NEEDS_ENHANCEMENT
            new_copy_rows.append([pid, p.get("Category", ""), company, subject, e1, e2, e3, status])
            existing_copy_ids.add(pid)
            has_copy = True
        elif not pid:
            has_copy = False

        summary.append((company, research, bool(contact_name), bool(email), has_copy))

    if new_outreach_rows:
        outreach_ws.append_rows(new_outreach_rows, value_input_option="RAW")
    if new_copy_rows:
        copy_ws.append_rows(new_copy_rows, value_input_option="RAW")

    if summary:
        print(f"Synced {len(summary)} new prospect(s) into Outreach:")
        for company, research, has_name, has_email, has_copy in summary:
            known = "+".join([n for n, v in [("name", has_name), ("email", has_email)] if v]) or "nothing yet"
            copy_note = "Campaign Copy generated" if has_copy else "NO Campaign Copy (missing Prospects ID)"
            print(f"  {company}: Research={research} (already had: {known}) -- {copy_note}")
    elif only_company:
        print(f'No matching, not-yet-synced prospect found for "{only_company}".')
    else:
        print("No new prospects to sync -- Outreach already has every company in Prospects.")


if __name__ == "__main__":
    main()
