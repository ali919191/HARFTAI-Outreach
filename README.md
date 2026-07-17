# HARFT AI Outreach Agent

Automates daily outreach + follow-ups to your pilot-batch list, tracks
replies and bounces, and keeps your Google Sheet updated as a live
dashboard.

## How a company moves through the pipeline

```
Prospects tab (research/staging)  --sync_prospects.py-->  Outreach tab (live send pipeline)
       ^          \                                              |
       |           \--> Campaign Copy (generated same pass)      | send_and_followup.py /
  import_prospects.py                                            | check_replies_bounces.py
```

Every row carries the same `ID` across all three tabs (Prospects, Outreach,
Campaign Copy), so a company added once in `Prospects` is unambiguous
everywhere downstream — no more hunting for which row number matches which
company by name.

- **`Prospects`** — one row per researched company (currently 60, across
  HVAC/Electrical/Dental/Accident Law). Nothing here is ever emailed
  automatically. Fill in `Contact Name`, `Business Email`, and set
  `Consent Check` to `Confirmed` once you've found and vetted a real
  decision-maker.
- **`Campaign Copy`** — a personalized 3-email sequence per company
  (Day 1 / Day 4 / Day 9), generated once by `generate_campaign_copy.py` /
  `sync_prospects.py`. Hand-edit (or Kai-edit — see below) any cell here any
  time; the generator never overwrites a row that already exists, so edits
  are permanent. Each row has a `Copy Status` column (dropdown:
  `Draft` / `Needs Enhancement` / `Enhanced` / `Reviewed`) that tracks where
  that copy is in review. New rows default to `Needs Enhancement` if their
  Category fell back to generic (non-sector) copy, or `Draft` otherwise.
  **`send_and_followup.py` will not send a row unless its Campaign Copy
  entry is marked `Reviewed`** — this is a second, independent gate from
  `Send Approval` on Outreach; both must be satisfied. Rows with no Campaign
  Copy entry at all (the legacy generic fallback) are exempt and are
  governed by `Send Approval` alone, as before.

  **External copy review (e.g. Kai):** since this tab is the literal source
  `send_and_followup.py` reads from on every run, any service with Google
  Sheets access to this spreadsheet can rewrite a body here and have it go
  out as-is next send cycle — no code changes needed. If you point Kai (or
  anything else) at this tab, it needs to know:
  1. Only touch rows where `Copy Status = Needs Enhancement` (that's the
     queue), and set it to `Enhanced` when done rewriting a row.
  2. Never delete or resolve the literal strings `[First name]` and
     `[Sender]` inside a body — `send_and_followup.py` substitutes those
     with the real Contact Name and your sender name at send time. Removing
     them breaks personalization for that lead.
  3. It can freely rewrite Subject and any of the three email bodies for a
     row; it should not touch `ID`, `Category`, or `Company`.
  4. `Copy Status = Reviewed` (the value that actually clears a row to
     send) is meant to be set by a human after checking the final text —
     don't have Kai set this itself unless you intend that.
  5. For consistent tone/positioning, have Kai read the `HARFT Brief` tab
     before rewriting — it's the canonical summary of HARFT AI's pitch,
     compatible platforms, and compliance guardrails (e.g. avoid ROI
     guarantees).
- **`promote_prospect.py "Company Name"`** — the strict manual gate (legacy
  path). Refuses to run unless Contact Name + Business Email + a confirmed
  Consent Check are all set.
- **`sync_prospects.py`** — the normal path now. Run with no argument to
  pick up *every* Prospects row that isn't in Outreach yet, or
  `python sync_prospects.py "Company Name"` for just one. No consent check
  required (Send Approval is what actually gates a send, so this is safe to
  run freely): it adds the row to `Outreach` (`Research=Yes` if a Contact
  Name or Email is still missing, `No` if you already supplied both) and
  generates that company's Campaign Copy in the same pass, using whatever
  Category/Specialty/Pain Hypothesis is already on the Prospects row. An
  unrecognized Category falls back to generic (non-sector) copy instead of
  failing, so this works for any new company you add, not just
  HVAC/Electrical/Dental/Accident Law.
- **`Outreach`** — the live send pipeline `send_and_followup.py` and
  `check_replies_bounces.py` watch. Its first column, `ID`, is the same
  Prospects ID you'll see on that company's row in `Prospects` and
  `Campaign Copy` — `sync_prospects.py`/`promote_prospect.py` carry it over
  automatically, so you can always tell which rows across the three tabs
  belong to the same company at a glance, even if the Company text differs
  slightly (punctuation, capitalization). `send_and_followup.py` matches a
  row to its `Campaign Copy` by this ID first; it only falls back to
  matching by Company name for older/hand-added rows with no ID (e.g. the
  original `Test Co 1` test row), and falls back further to the old generic
  HVAC template if there's no Campaign Copy row at all. Two extra columns
  gate everything:
  - **`Research`** (Yes/No, default No) — for companies you paste directly
    into `Outreach` with just a Company name. Set to `Yes` and a scheduled
    task (`outreach-contact-research`, runs every 2 hours) looks up a
    decision-maker's name using free sources only (company site, BBB,
    Texas SOS, web search), then tries Hunter.io's Email Finder for a
    verified email once a name is known — never Apollo, since Apollo
    requires live per-call approval an unattended run can't get. It never
    sends anything or touches `Send Approval`.
  - **`Send Approval`** (Yes/No, default No) — the final human gate.
    `send_and_followup.py` will not send *anything* for a row, including
    follow-ups, unless this is `Yes`. Review the Campaign Copy that would
    actually go out, then flip it yourself.
- **`Dashboard` / `HARFT Brief` / `Lists`** — reporting and reference tabs,
  set up once by `setup_reporting_tabs.py`.

### Apollo.io connector — current limitation

The connected Apollo account is on Apollo's free plan, which blocks the
People Search, People Match, and Bulk Match endpoints entirely (both
single and batch calls fail with "not accessible on this free plan").
Organization-level contact research currently runs on free web research
instead (see `Research` column above). Apollo enrichment is still tried
first in any live chat session (never in the scheduled task), so nothing
needs to change here if the plan is ever upgraded.

### Finding verified emails — Hunter.io

Once a decision-maker's name is known (from `Prospects` or via the
`Research` flag), `find_emails.py` looks up a verified email through
Hunter.io's Email Finder. Free tier: 50 credits/month, no card required.

1. Sign up at [hunter.io](https://hunter.io) (free plan, no card).
2. In the dashboard, go to your account/API settings and copy your API key.
3. Add it to `.env`: `HUNTER_API_KEY=your-key-here`.
4. Run `python find_emails.py` — checks every `Prospects` row with a
   Contact Name but no Business Email, and mirrors any email it finds into
   the matching `Outreach` row too.

Only results Hunter itself scores at 70%+ confidence are ever written in;
anything lower is left blank rather than risk a bad address. The
scheduled `outreach-contact-research` task also calls Hunter automatically
(capped at 5 lookups per run) once it finds a name via free web research.

## What this can and can't see (read this first)

| Signal | Tracked? | Notes |
|---|---|---|
| Sent | Yes | Logged the moment the script sends it |
| Bounced | Yes | Hard (bad address) vs soft (mailbox full, temp issue), parsed from Zoho's bounce notice |
| Replied | Yes | Detected by scanning your inbox for a message from that lead's address |
| Opened | Approximate | A tracking pixel gives a signal, but Apple Mail Privacy Protection and Gmail's image proxy pre-load images for many users, so this can register a false "open." Treat it as a rough proxy, not a fact |
| Marked as spam / moved to trash | **Not visible to any sender** | This happens entirely inside the recipient's mailbox. No tool -- not this one, not HubSpot, not Mailchimp -- can see it. The closest proxy: no open + no reply + no bounce after the full sequence = likely filtered or ignored |

## 1. Set up the Google Sheet

Create a Google Sheet with a tab named `Outreach` (or set `SHEET_TAB_NAME`
in `.env`). Row 1 must contain exactly these headers, in this order:

```
Company | Contact Name | Email | Status | Sequence Step | Last Sent Date | Next Action Date | Opens | Last Open Date | Replied | Reply Date | Bounce Type | Tracking ID | Notes
```

Leave everything below row 1 blank except `Company`, `Contact Name`, and
`Email` for each of your 15 pilot companies -- the scripts fill in the rest.

### Optional: a "Summary" dashboard tab

Add a second tab called `Summary` with formulas like these (adjust the
range `2:1000` if your list is bigger):

```
Total leads        =COUNTA(Outreach!C2:C1000)
Emails sent         =COUNTA(Outreach!F2:F1000)
Opened at least once =COUNTIF(Outreach!H2:H1000,">0")
Replied             =COUNTIF(Outreach!J2:J1000,"Y")
Bounced             =COUNTIF(Outreach!D2:D1000,"Bounced*")
Opted out           =COUNTIF(Outreach!D2:D1000,"Opted Out")
Parked (no response) =COUNTIF(Outreach!D2:D1000,"No Response - Parked")
Reply rate          =Replied/Emails_sent (format as %)
```

### Optional: color-code the Status column

Select column D on the `Outreach` tab -> Format -> Conditional formatting
-> Custom formula is:
- `=$D2="Replied"` -> green
- `=$D2="Opted Out"` -> gray
- `=REGEXMATCH($D2,"Bounced")` -> red
- `=$D2="No Response - Parked"` -> gray
- `=REGEXMATCH($D2,"Sent")` -> yellow

Now you have a live, color-coded pipeline view without building a
separate dashboard app.

## 2. Get Zoho credentials

1. In Zoho Mail, go to Settings -> Mail Accounts -> IMAP Access and turn
   IMAP on.
2. Go to your Zoho Account security settings and generate an
   **app-specific password** (required if you have 2FA on, and
   recommended either way instead of your real password).
3. Put your Zoho email and that app password into `.env`.

## 3. Get Google Sheets API access

1. In Google Cloud Console, create a project (or use an existing one)
   and enable the **Google Sheets API**.
2. Create a **service account**, then create and download a JSON key
   for it. Save it as `service_account.json` in this folder.
3. Open your Google Sheet, click Share, and share it with the service
   account's email address (looks like
   `something@your-project.iam.gserviceaccount.com`) as an Editor.
4. Copy the Sheet ID out of the URL
   (`https://docs.google.com/spreadsheets/d/THIS_PART/edit`) into
   `GOOGLE_SHEET_ID` in `.env`.

## 4. Deploy the tracking pixel server

`tracking_server.py` needs a public HTTPS URL so the pixel and
unsubscribe link work from any inbox. Easiest free/cheap options:

- **Render** or **Railway**: connect this folder as a repo, set it to
  run `python tracking_server.py`, add your `.env` values (and upload
  `service_account.json`) as environment variables/secrets.
- **Fly.io**: similar -- a small always-on Flask app.
- A small existing VPS also works fine, behind Nginx + a free
  Let's Encrypt certificate.

Once deployed, put that public URL into `TRACKING_BASE_URL` in `.env`.

## 5. Install and configure

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env with your real values
```

## 6. Schedule the two automation scripts

On Linux/Mac (crontab -e):

```
# Check for replies/bounces every 30 minutes
*/30 * * * * cd /path/to/outreach_agent && /usr/bin/python3 check_replies_bounces.py >> logs/check.log 2>&1

# Send/follow-up once a day at 9am
0 9 * * * cd /path/to/outreach_agent && /usr/bin/python3 send_and_followup.py >> logs/send.log 2>&1
```

On Windows, set up two Task Scheduler tasks pointing at the same two
commands.

## 7. Compliance basics (worth doing regardless of tooling)

This is B2B cold outreach, so keep it CAN-SPAM-compliant:
- The templates already include your business address and an
  unsubscribe link in every email -- fill in a real `BUSINESS_ADDRESS`
  in `.env`.
- Once someone hits unsubscribe, `send_and_followup.py` will never
  email them again (Status becomes `Opted Out`, which is a terminal
  status the script skips).
- Keep subject lines honest -- avoid anything that misrepresents the
  email as a personal reply when it isn't.

## Files in this folder

| File | Purpose |
|---|---|
| `common.py` | Shared config + Google Sheet helpers (all tabs) |
| `email_templates.py` | Legacy generic template + `SECTOR_CONFIG`/`build_campaign()` used to generate Campaign Copy |
| `prospects_data.py` | Raw 60-company research list |
| `import_prospects.py` | One-time: loads `prospects_data.py` into the `Prospects` tab |
| `migrate_prospects_schema.py` | One-shot: migrated `Prospects` to the 23-column schema (Contact Title + Contact 2/3) |
| `migrate_outreach_schema.py` | One-shot: migrated `Outreach` to add `Research` and `Send Approval` |
| `migrate_outreach_add_id.py` | One-shot: added the `ID` column to `Outreach`, matched to Prospects by Company name |
| `generate_campaign_copy.py` | One-time per company: writes personalized 3-email sequences into `Campaign Copy` |
| `promote_prospect.py` | Legacy strict path: moves one vetted, consented prospect from `Prospects` into `Outreach` |
| `sync_prospects.py` | Normal path: auto-adds any new Prospects row to `Outreach` + generates its Campaign Copy |
| `setup_reporting_tabs.py` | One-time/re-runnable: builds/refreshes `Dashboard`, `HARFT Brief`, `Lists` tabs |
| `setup_outreach_formatting.py` | One-time/re-runnable: color-codes + adds dropdowns to `Outreach` |
| `hunter_email_finder.py` | Wraps Hunter.io's Email Finder API, enforces the 70%-confidence floor |
| `find_emails.py` | Re-runnable: finds verified emails for `Prospects` rows with a known name but no email |
| `send_and_followup.py` | Daily job: sends initial emails + follow-ups, using `Campaign Copy` when available |
| `check_replies_bounces.py` | Frequent job: detects replies + bounces |
| `tracking_server.py` | Public web service for the open pixel + unsubscribe (deployed on Render) |
| `requirements.txt` | Python dependencies |
| `.env.example` | Copy to `.env` and fill in |
