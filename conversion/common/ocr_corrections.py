"""Conservative OCR repairs shared by every PDF-to-EPUB conversion.

Only put a repair here when it is mechanically safe in ordinary prose.  A
book-specific name, quotation, citation, note marker, or ambiguous spelling
belongs beside that book's build material under ``tmp/pdfs/<book>/``.
"""

from __future__ import annotations

import re


# Exact strings with one defensible reading.  These are intentionally small
# and reviewable; this is not a general-purpose spell checker.
COMMON_EXACT_REPLACEMENTS = {
    "‘““": "“",
    "kind ofjustice": "kind of justice",
    "mest prodigious": "most prodigious",
    "th emselves": "themselves",
}

# Fused tokens repaired only when they occupy a complete word.  This prevents
# a short OCR signature from changing a legitimate substring of a longer word.
COMMON_TOKEN_REPLACEMENTS = {
    "factbased": "fact-based",
    "ofliterature": "of literature",
    "selfknowledge": "self-knowledge",
    "teligion": "religion",
    "theirjargon": "their jargon",
    "upona": "upon a",
}


def _preserve_initial_case(match: re.Match[str], lower_replacement: str) -> str:
    if match.group(0)[0].isupper():
        return lower_replacement[0].upper() + lower_replacement[1:]
    return lower_replacement


def apply_common_ocr_corrections(text: str) -> str:
    """Apply only cross-book OCR repairs with constrained matching."""
    for damaged, restored in COMMON_EXACT_REPLACEMENTS.items():
        text = text.replace(damaged, restored)
    for damaged, restored in COMMON_TOKEN_REPLACEMENTS.items():
        text = re.sub(rf"\b{re.escape(damaged)}\b", restored, text)

    # Whole-token matching is essential: `ina` is a common fusion of `in a`,
    # but the same letters are legitimate inside names such as `Karenina`.
    text = re.sub(
        r"\bina\b",
        lambda match: _preserve_initial_case(match, "in a"),
        text,
        flags=re.I,
    )

    # OCR can close the narrow gap between a pronoun and `have`.
    text = re.sub(
        r"\b(I|You|We|They|He|She|It)have\b",
        lambda match: f"{match.group(1)} have",
        text,
    )
    return text
