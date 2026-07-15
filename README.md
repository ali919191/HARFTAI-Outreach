# HARFT AI Outreach Agent

Automates daily outreach + follow-ups to your pilot-batch list, tracks
replies and bounces, and keeps your Google Sheet updated as a live
dashboard.

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
| `common.py` | Shared config + Google Sheet helpers |
| `email_templates.py` | Subject/body text for each step -- edit freely |
| `send_and_followup.py` | Daily job: sends initial emails + follow-ups |
| `check_replies_bounces.py` | Frequent job: detects replies + bounces |
| `tracking_server.py` | Public web service for the open pixel + unsubscribe |
| `requirements.txt` | Python dependencies |
| `.env.example` | Copy to `.env` and fill in |
