"""Conservative OCR repairs shared by every PDF-to-EPUB conversion.

Only put a repair here when it is mechanically safe in ordinary prose.  A
book-specific name, quotation, citation, note marker, or ambiguous spelling
belongs beside that book's build material under ``tmp/pdfs/<book>/``.
"""

from __future__ import annotations

import re

try:
    from .prose_spacing import normalize_prose_spacing
except ImportError:  # Direct script/test imports from conversion/common.
    from prose_spacing import normalize_prose_spacing


# Exact strings with one defensible reading.  These are intentionally small
# and reviewable; this is not a general-purpose spell checker.
COMMON_EXACT_REPLACEMENTS = {
    "‘““": "“",
    # OCR engines often emit a printed double curly quote as two single curly
    # quotes. Identical adjacent opening or closing singles cannot represent
    # valid nested English quotation typography (nesting alternates styles).
    "‘‘": "“",
    "’’": "”",
    "dan gerous": "dangerous",
    "encour aged": "encouraged",
    "dom inant": "dominant",
    "imagina ble": "imaginable",
    "kind ofjustice": "kind of justice",
    "mest prodigious": "most prodigious",
    "th emselves": "themselves",
}

# Fused tokens repaired only when they occupy a complete word.  This prevents
# a short OCR signature from changing a legitimate substring of a longer word.
COMMON_TOKEN_REPLACEMENTS = {
    # On the verified Blake quotation in Life Is a Miracle, OCR read the
    # ampersand as `8c`. Keep this whole-token-only because `8c` can also be
    # meaningful in technical text.
    "8c": "&",
    "factbased": "fact-based",
    "ofliterature": "of literature",
    "selfknowledge": "self-knowledge",
    "teligion": "religion",
    "theirjargon": "their jargon",
    "upona": "upon a",
    "asystem": "a system",
    "Asystem": "A system",
    "Itis": "It is",
    "Iam": "I am",
    'It"s': "It's",
    'it"s': "it's",
    "Mosi": "Most",
    "mosi": "most",
    "Yoii": "You",
    "yoii": "you",
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

    # Italic ll can be read as two slashes. Require a complete prose token:
    # preserve a//b, a//2, paths, and a spaced floor-division operator.
    text = re.sub(r"(?<![\w/])a//(?=$|[\s.,;:!?—–”’\"')\]])", "all", text)

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

    # A primary double quotation is sometimes closed as single+double (and
    # occasionally single+double+single). Repair only a short quote with no
    # nested single opener, so valid nesting such as “He called it ‘no,’” is
    # untouched. This handles OCR forms like “co-act,’” and “a lover,’”’.
    text = re.sub(
        r"“([^“”‘\n]{0,240}?)([.,!?;:])’”(?!’?[°®©*])’?",
        lambda match: f"“{match.group(1)}{match.group(2)}”",
        text,
    )
    return normalize_prose_spacing(text)
