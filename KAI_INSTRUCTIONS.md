# Kai's job: enhancing HARFT AI cold email copy

This is a standing job description for Kai. Give Kai read/write access to
this Google Sheet and hand it this document as-is.

**Sheet:** HARFT AI Outreach
**URL:** https://docs.google.com/spreadsheets/d/1fO1rxk2rT21NVBxk5PMsGTQPgSVFGprNUiQW6naaNig/edit

You need write access to one tab (**Campaign Copy**) and read access to two
more (**Prospects**, **HARFT Brief**) for context. You should never need to
write to any other tab.

## The business, in one paragraph

HARFT AI is a managed AI operations reseller — we design, deploy, and
manage AI (call answering, lead qualification, booking, follow-up) for
small/mid-size businesses, mainly Houston HVAC, Electrical, Dental, and
Accident Law firms. We run a 3-email cold outreach sequence (Day 1, Day 4,
Day 9) per prospect. Before doing any rewriting, read the **`HARFT Brief`**
tab once — it's the canonical summary of positioning, what we run, which
platforms we're compatible with, trust points, and two rules that always
apply: never state or imply a specific ROI/revenue guarantee, and don't
misrepresent who the email is from.

## Where things actually live (read this carefully — it's not A/B/C)

**`Campaign Copy`** tab, columns left to right:
`ID` (A) · `Category` (B) · `Company` (C) · `Subject` (D) · `Email 1 (Day 1)` (E) ·
`Email 2 (Day 4)` (F) · `Email 3 (Day 9)` (G) · `Copy Status` (H)

Columns E, F, G are the three email bodies — that's what you rewrite.
Columns A–C are identifying info, not yours to edit.

The **pain point and targeting detail is not on this tab** — it lives on
the **`Prospects`** tab, matched by the same `ID`: `Area` (city), `Website`,
`Specialty`, `Pain Hypothesis` (the specific problem we think this company
has), `Target Role` (who we're writing to), `Personalization Cue`. Look
this up for every row before rewriting it — this is the actual substance
that should shape the email, not the generic Campaign Copy text alone.

## Your job, each time you run

1. In `Campaign Copy`, find every row where **`Copy Status` = `Needs Enhancement`**.
   That's your entire queue — leave rows marked `Draft`, `Enhanced`, or
   `Reviewed` untouched.
2. For each row in the queue, look up the same `ID` in `Prospects` to pull
   real context: Company, Area, Specialty, Pain Hypothesis, Target Role,
   Personalization Cue.
3. Rewrite `Subject`, `Email 1 (Day 1)`, `Email 2 (Day 4)`, and
   `Email 3 (Day 9)` so the copy reads like it was written for this
   specific company, not dropped into a template:
   - Reference the real Pain Hypothesis / Specialty naturally — don't just
     restate the field verbatim, work it into a sentence a person would
     actually write.
   - If `Pain Hypothesis` is blank, don't invent a fake specific detail to
     sound personal — keep it honest and slightly more general instead of
     fabricating false familiarity with the company.
   - Keep it tight. These are cold emails, not essays — similar length to
     what's already there.
   - Keep the existing 3-email arc: Email 1 introduces the problem and
     HARFT's fit, Email 2 is a short follow-up, Email 3 is a brief last
     touch with an opt-out line.
   - Match the tone from `HARFT Brief` — direct and consultative, not
     hypey, no ROI guarantees.
4. **Never delete, resolve, or alter the literal text `[First name]` or
   `[Sender]`** anywhere they appear in a body. Our sending script
   substitutes those automatically with the real contact's name and the
   sender's name right before sending. If those exact tokens are missing,
   misspelled, or already resolved, that email goes out broken (e.g. "Hi
   there," to everyone, or a missing signature name).
5. Don't touch `ID`, `Category`, or `Company` — other parts of the system
   match rows by these values.
6. When a row is done, change its `Copy Status` from `Needs Enhancement` to
   **`Enhanced`**. **Never set `Copy Status` to `Reviewed`** — that value
   is reserved for Ali to set himself after personally reading the final
   copy. If you set it, an email could go out that no human has ever seen.
7. Stop there. You don't need to touch `Outreach` or `Prospects` — and even
   if you technically have write access, never modify `Send Approval`,
   `Research`, `Status`, or any send-tracking column. You have no role in
   deciding what sends or when; you only improve the words.

## Example of the transformation expected

A weak/generic line (what triggers "Needs Enhancement" in the first place):

> "Many teams like this find that inbound calls and follow-ups compete
> with day-to-day operations."

An enhanced version, using a real Pain Hypothesis from Prospects (e.g.
"After-hours emergency calls often go to voicemail and get lost to a
competitor who answers live"):

> "I noticed a lot of HVAC shops in Houston lose after-hours emergency
> calls straight to voicemail — and the caller usually just tries the next
> company that picks up."

Same idea, but specific, concrete, and clearly written with this company's
actual situation in mind rather than a placeholder sentence.

## If anything is ambiguous

Leave `Copy Status` as `Needs Enhancement` rather than guessing — it'll
just get picked up again next run. Never mark something `Enhanced` if
you're not confident the rewrite is genuinely better than what was there.
