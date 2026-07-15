"""
email_templates.py
Subject/body text for each step of the sequence. Edit the wording freely --
just keep the {placeholders}.
"""

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
