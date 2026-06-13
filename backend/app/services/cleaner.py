import re
from collections import OrderedDict

NOISE_PATTERNS = [
    r"\b(cookie|privacy preference|terms of use|all rights reserved)\b",
    r"\b(login|sign in|subscribe|newsletter|cart|menu)\b",
    r"\b(skip to content|accept all|reject all)\b",
]

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def remove_noise(text: str) -> str:
    lines = []
    for line in re.split(r"[\r\n]+", text):
        cleaned = normalize_whitespace(line)
        if len(cleaned) < 25:
            continue
        if any(re.search(pattern, cleaned, flags=re.IGNORECASE) for pattern in NOISE_PATTERNS):
            continue
        lines.append(cleaned)
    return "\n".join(lines)

def deduplicate_sentences(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text)
    seen = OrderedDict()
    for part in parts:
        key = part.lower().strip()
        if len(key) > 20 and key not in seen:
            seen[key] = part.strip()
    return " ".join(seen.values())

def clean_website_text(text: str, max_chars: int = 20000) -> str:
    text = remove_noise(text)
    text = normalize_whitespace(text)
    text = deduplicate_sentences(text)
    return text[:max_chars]
