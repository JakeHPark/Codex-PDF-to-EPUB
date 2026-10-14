"""Conservative page-boundary cleanup shared by PDF-to-EPUB builders."""

from __future__ import annotations

import re


DEFAULT_HEADING = re.compile(
    r"^(?:chapter|part|book|section|interlude|prologue|epilogue|conclusion|notes|index)\b",
    re.IGNORECASE,
)
DETACHED_DEBRIS = re.compile(r"^[A-Z]{1,3}$")


def starts_indented_paragraph(
    line_left: float,
    *,
    body_left: float,
    first_line_indent: float = 12,
    tolerance: float = 1.5,
) -> bool:
    """Recognize paragraph indentation relative to the content's block edge.

    In hanging notes/lists, ``body_left`` is the continuation-text edge, not
    the number/bullet edge or the preceding line's bounding box. Comparing
    against that preceding box falsely splits the first wrapped line after a
    marker. Supply the current page's content edge for alternating margins.
    Classify headings, new entries, quotations and equations separately first.
    """
    return line_left >= body_left + first_line_indent - tolerance


def drop_detached_boundary_debris(
    previous_page: str,
    next_page: str,
    *,
    heading_pattern: re.Pattern[str] = DEFAULT_HEADING,
) -> tuple[str, list[str]]:
    """Drop a tiny detached tail only before an unmistakable structural heading.

    This catches marginal fragments such as ``PS`` that otherwise become
    ``PS CHAPTER 11``.  The candidate must be its own blank-line-delimited
    block, contain only one to three uppercase letters, and be followed on the
    next physical page by a recognized heading.  Ordinary prose is untouched.
    """
    next_lines = [line.strip() for line in next_page.splitlines() if line.strip()]
    if not next_lines or not heading_pattern.match(next_lines[0]):
        return previous_page, []
    blocks = re.split(r"(\n\s*\n)", previous_page.rstrip())
    if not blocks:
        return previous_page, []
    last = blocks[-1].strip()
    if not DETACHED_DEBRIS.fullmatch(last):
        return previous_page, []
    return "".join(blocks[:-1]).rstrip(), [last]
