from __future__ import annotations

import re
from urllib.parse import urlparse


def normalize_name(name: str) -> str:
    return " ".join(name.casefold().split())


def extract_domain(website: str) -> str:
    if not website:
        return ""
    if "://" not in website:
        website = "https://" + website
    try:
        parsed = urlparse(website)
        domain = parsed.netloc.lower()
        domain = re.sub(r"^www\.", "", domain)
        return domain
    except Exception:
        return website.lower().strip()


def is_duplicate_by_name(
    name: str,
    existing_names: list[str],
) -> bool:
    normalized = normalize_name(name)
    return any(normalize_name(e) == normalized for e in existing_names)


def is_duplicate_by_domain(
    website: str,
    existing_websites: list[str],
) -> bool:
    domain = extract_domain(website)
    if not domain:
        return False
    for existing in existing_websites:
        if domain == extract_domain(existing):
            return True
    return False
