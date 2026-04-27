"""Slug generation for council deliberations.

Format: {YYYY-MM-DD}-{kebab-headline}
"""
from __future__ import annotations

import datetime
import re
import unicodedata

MAX_BODY_LEN = 60


def make_slug(headline: str, date: str | None = None) -> str:
    """Generate a deterministic, sortable slug from a headline.

    Args:
        headline: Free-text description of the deliberation.
        date: ISO date (YYYY-MM-DD). Defaults to today.

    Raises:
        ValueError: If headline is empty or contains no slug-able characters.
    """
    body = _kebab(headline)
    if not body:
        raise ValueError(f"headline produced empty slug: {headline!r}")
    body = body[:MAX_BODY_LEN].rstrip("-")
    if date is None:
        date = datetime.date.today().isoformat()
    return f"{date}-{body}"


def _kebab(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[‘’“”']+", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text
