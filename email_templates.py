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


def build_campaign(category, company, city, specialty, pain):
    """Port of the campaign() function from build_outreach_tracker.mjs.

    Returns (subject, email1, email2, email3). [First name] and [Sender]
    are left as literal placeholders on purpose -- generate_campaign_copy.py
    writes them into the sheet unresolved, and send_and_followup.py
    substitutes real values at send time (once a real Contact Name exists,
    which it doesn't yet at generation time).
    """
    s = SECTOR_CONFIG.get(category)
    if not s:
        raise ValueError(f"No SECTOR_CONFIG for category: {category!r}")

    subject = f"{company}: a practical way to protect more inbound opportunities"

    email1 = f"""Hi [First name],

I came across {company} while looking at {specialty.lower()} providers in the {city} area. {pain}

HARFT AI runs managed AI operations for teams like yours—not another tool to learn. We design, deploy, and continuously improve AI that answers calls, qualifies requests, books appointments, follows up, and logs every interaction inside the systems you already use.

For {company}, the first use case would likely be making sure {s['hook']}, so your team can focus on the work that requires them. The goal is {s['metric']}, without replacing your current software or asking your team to become AI experts.

Would you be open to {s['cta']}?

Best,
[Sender]
HARFT AI
Houston | harftai.com

P.S. If someone else owns operations or intake, I'm happy to reach out to them instead."""

    topic = _TOPIC_BY_CATEGORY.get(category, _DEFAULT_TOPIC)

    email2 = f"""Hi [First name],

Following up on my note about {company}. This is not a chatbot subscription: HARFT designs the workflows, connects them to the software you already use, monitors quality, and improves them over time.

A useful starting point is often one workflow: answer and qualify every inbound request, then book or route it with a human escalation path when needed. Every interaction stays logged and reviewable.

Is improving {topic} a priority this quarter?

Best,
[Sender]"""

    email3 = f"""Hi [First name],

Last note from me. If {company} is already confident that every important call and web lead is captured, qualified, followed up, and visible to the team, I'll close the loop.

If not, HARFT can map one high-value workflow and show what managed AI operations would look like alongside your existing tools—no platform replacement required.

Should I send a short example, or is there a better person to speak with?

Best,
[Sender]

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
{sender_name}""",
    },
    1: {
        "subject": "Re: Capturing after-hours HVAC calls for {company}",
        "body": """Hi {contact_name},

Following up in case my note last week got buried. Happy to keep this brief: we're holding a few spots left in our pilot batch (implementation fee waived), and I'd love 15 minutes to see if after-hours calls are something worth solving for {company}.

Best,
{sender_name}""",
    },
    2: {
        "subject": "Re: Capturing after-hours HVAC calls for {company}",
        "body": """Hi {contact_name},

Last note from me on this -- I don't want to clutter your inbox. If missed after-hours calls aren't a priority right now, no worries at all. If it becomes one, happy to pick this back up any time.

Best,
{sender_name}""",
    },
}
