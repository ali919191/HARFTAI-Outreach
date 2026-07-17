"""
email_templates.py
Subject/body text for each step of the sequence. Edit the wording freely --
just keep the {placeholders}.

STEP_TEMPLATES below is the original generic (HVAC-only, single-variant)
fallback -- send_and_followup.py only uses it for a lead whose Company name
has no matching row in the Campaign Copy sheet tab yet.

SECTOR_CONFIG / build_campaign() is the per-vertical templating logic ported
from build_outreach_tracker.mjs (the old local Excel generator). It's used
once, by generate_campaign_copy.py, to write personalized copy into the
Campaign Copy tab -- not called at send time.
"""

from common import HARFT_PHONE

# Shared sign-off block appended to every campaign email so the sequence
# reads as coming from a real person at a real company, not a bare "Best,".
# [Sender] resolves to SENDER_NAME (currently "Ali Syed") at send time.
_SIGNATURE = f"""Best,
[Sender]
HARFT AI
{HARFT_PHONE} | harftai.com"""

# ---------------- Per-vertical messaging config ----------------
# role  = who the email is addressed to (used for research, not interpolated)
# metric = the outcome promised
# hook   = the specific capability highlighted
# cta    = the ask
SECTOR_CONFIG = {
    "HVAC": {
        "role": "Owner, GM, or Operations Manager",
        "metric": "more booked service and replacement work",
        "hook": "every AC or heating call gets an answer—even after hours",
        "cta": "a 15-minute look at where calls or estimate follow-ups may be leaking",
    },
    "Electrical": {
        "role": "Owner, Service Manager, or Operations Manager",
        "metric": "more booked electrical jobs without a larger office team",
        "hook": "urgent and estimate calls are qualified and routed immediately",
        "cta": "a 15-minute look at the calls and follow-ups your office should not have to chase manually",
    },
    "Dental": {
        "role": "Practice Owner, Office Manager, or Director of Operations",
        "metric": "more booked new-patient visits with less front-desk strain",
        "hook": "patients can get answers and book around the clock",
        "cta": "a 15-minute review of the patient-access workflows that could be automated safely",
    },
    "Accident Law": {
        "role": "Managing Partner, Intake Director, or COO",
        "metric": "faster, more consistent intake without compromising the human handoff",
        "hook": "time-sensitive injury leads receive a compassionate immediate response",
        "cta": "a 15-minute review of where intake response time or follow-up could improve",
    },
}

_TOPIC_BY_CATEGORY = {
    "Dental": "patient access",
    "Accident Law": "intake response",
}
_DEFAULT_TOPIC = "call capture and follow-up"

# Used whenever a Prospects row's Category doesn't match one of the
# configured verticals above (e.g. a one-off lead outside the core HVAC/
# Electrical/Dental/Accident Law targeting). Generic enough to still read
# naturally; edit the resulting Campaign Copy row by hand for anything that
# needs sharper, sector-specific language.
_DEFAULT_SECTOR = {
    "role": "Owner, Operations Manager, or relevant decision-maker",
    "metric": "faster response and follow-up without adding headcount",
    "hook": "inbound calls and requests get an immediate, consistent response",
    "cta": "a 15-minute look at where response time or follow-up could improve",
}


def build_campaign(category, company, city, specialty, pain):
    """Port of the campaign() function from build_outreach_tracker.mjs.

    Returns (subject, email1, email2, email3). [First name] and [Sender]
    are left as literal placeholders on purpose -- generate_campaign_copy.py
    writes them into the sheet unresolved, and send_and_followup.py
    substitutes real values at send time (once a real Contact Name exists,
    which it doesn't yet at generation time).

    Never raises: an unrecognized Category falls back to _DEFAULT_SECTOR
    instead of blocking copy generation, since new prospect categories
    can be added to the sheet at any time. A blank Pain Hypothesis or Area
    falls back to a generic line instead of leaving a hole in the email.
    """
    s = SECTOR_CONFIG.get(category, _DEFAULT_SECTOR)
    specialty = (specialty or "").strip()
    city = (city or "").strip()
    pain = (pain or "").strip()

    subject = f"{company}: a practical way to protect more inbound opportunities"

    location_phrase = f"in the {city} area" if city else "in your market"
    specialty_phrase = f"{specialty.lower()} providers {location_phrase}" if specialty else f"providers {location_phrase}"
    pain_line = pain or (
        f"Many teams like this find that inbound calls and follow-ups compete with day-to-day operations."
    )

    email1 = f"""Hi [First name],

I came across {company} while looking at {specialty_phrase}. {pain_line}

HARFT AI runs managed AI operations for teams like yours—not another tool to learn. We design, deploy, and continuously improve AI that answers calls, qualifies requests, books appointments, follows up, and logs every interaction inside the systems you already use.

For {company}, the first use case would likely be making sure {s['hook']}, so your team can focus on the work that requires them. The goal is {s['metric']}, without replacing your current software or asking your team to become AI experts.

Would you be open to {s['cta']}?

{_SIGNATURE}

P.S. If someone else owns operations or intake, I'm happy to reach out to them instead."""

    topic = _TOPIC_BY_CATEGORY.get(category, _DEFAULT_TOPIC)

    email2 = f"""Hi [First name],

Following up on my note about {company}. This is not a chatbot subscription: HARFT designs the workflows, connects them to the software you already use, monitors quality, and improves them over time.

A useful starting point is often one workflow: answer and qualify every inbound request, then book or route it with a human escalation path when needed. Every interaction stays logged and reviewable.

Is improving {topic} a priority this quarter?

{_SIGNATURE}"""

    email3 = f"""Hi [First name],

Last note from me. If {company} is already confident that every important call and web lead is captured, qualified, followed up, and visible to the team, I'll close the loop.

If not, HARFT can map one high-value workflow and show what managed AI operations would look like alongside your existing tools—no platform replacement required.

Should I send a short example, or is there a better person to speak with?

{_SIGNATURE}

To opt out of future messages, reply "unsubscribe.\""""

    return subject, email1, email2, email3


# ---------------- Legacy generic fallback (HVAC-only, single variant) ----------------
STEP_TEMPLATES = {
    0: {
        "subject": "Capturing after-hours HVAC calls for {company}",
        "body": """Hello {contact_name},

I came across {company} while researching HVAC providers in the Houston area. Calls and estimate requests that arrive after hours or during peak season are often the ones that slip through.

HARFT AI runs managed AI operations for teams like yours -- we design, deploy, and continuously improve AI that answers calls, qualifies requests, books appointments, and logs every interaction inside the systems you already use.

As part of our launch, we're onboarding a pilot batch of 15 clients and waiving the implementation fee entirely (normally $3,000-$5,000). Would you be open to a 15-minute look at where calls or estimate follow-ups may be leaking?

Best,
{sender_name}
HARFT AI
{harft_phone} | harftai.com""",
    },
    1: {
        "subject": "Re: Capturing after-hours HVAC calls for {company}",
        "body": """Hi {contact_name},

Following up in case my note last week got buried. Happy to keep this brief: we're holding a few spots left in our pilot batch (implementation fee waived), and I'd love 15 minutes to see if after-hours calls are something worth solving for {company}.

Best,
{sender_name}
HARFT AI
{harft_phone} | harftai.com""",
    },
    2: {
        "subject": "Re: Capturing after-hours HVAC calls for {company}",
        "body": """Hi {contact_name},

Last note from me on this -- I don't want to clutter your inbox. If missed after-hours calls aren't a priority right now, no worries at all. If it becomes one, happy to pick this back up any time.

Best,
{sender_name}
HARFT AI
{harft_phone} | harftai.com""",
    },
}
