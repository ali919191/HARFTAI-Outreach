"""
hunter_email_finder.py

Thin wrapper around Hunter.io's Email Finder API
(https://hunter.io/api-documentation/v2#email-finder).

Given a person's name and a company domain, Hunter returns its best guess
at their work email plus a 0-100 confidence score. We only ever accept a
result at or above HUNTER_MIN_CONFIDENCE -- anything lower is treated as
not found, same policy as everywhere else in this project: no unverified
address ever gets written into the sheet.

This never raises -- any API error, timeout, or missing key is treated as
"not found" so callers (a one-off script or the scheduled research task)
can keep going without crashing.
"""

import re

import requests

HUNTER_FINDER_URL = "https://api.hunter.io/v2/email-finder"
HUNTER_MIN_CONFIDENCE = 70


def domain_from_url(url):
    """https://www.frioairsystems.com/ -> frioairsystems.com"""
    if not url:
        return ""
    m = re.search(r"https?://(?:www\.)?([^/]+)", url.strip())
    return m.group(1) if m else url.strip()


def find_email(full_name, domain, api_key):
    """Returns (email, score) if a confident match is found, else (None, None)."""
    if not api_key or not full_name or not domain:
        return None, None

    parts = full_name.strip().split()
    if not parts:
        return None, None
    first_name = parts[0]
    last_name = parts[-1] if len(parts) > 1 else ""

    try:
        resp = requests.get(
            HUNTER_FINDER_URL,
            params={
                "domain": domain,
                "first_name": first_name,
                "last_name": last_name,
                "api_key": api_key,
            },
            timeout=15,
        )
    except requests.RequestException:
        return None, None

    if resp.status_code != 200:
        return None, None

    try:
        result = resp.json().get("data", {})
    except ValueError:
        return None, None

    email = result.get("email")
    score = result.get("score")
    if email and isinstance(score, (int, float)) and score >= HUNTER_MIN_CONFIDENCE:
        return email, score
    return None, None
