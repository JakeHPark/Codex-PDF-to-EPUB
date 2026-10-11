"""Shared application of reviewed, layout-derived endnote evidence.

Detection and human review remain book-specific because a raised glyph cannot
be decoded safely from its Unicode character alone.  Once evidence has been
reviewed, however, indexing it, replacing the damaged token, and preserving
inline emphasis are mechanical and should be identical in every builder.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
import json
import re


def load_reviewed_records(path: str | Path) -> list[dict]:
    """Load evidence and reject incomplete or nonnumeric review decisions."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError(f"marker evidence has no records list: {path}")
    for record in records:
        missing = {"page", "raw_token", "selected", "reviewed"} - record.keys()
        if missing:
            raise ValueError(f"marker evidence missing {sorted(missing)}: {record!r}")
        if record["reviewed"] is not True or not re.fullmatch(r"\d+", str(record["selected"])):
            raise ValueError(f"unreviewed marker evidence: {record!r}")
    return records


def index_records_by_page(records: Iterable[dict]) -> dict[int, list[dict]]:
    """Group markers without assuming that a page contains only one marker."""
    indexed: dict[int, list[dict]] = {}
    for record in records:
        page = int(record["page"])
        copied = dict(record)
        copied.setdefault("ordinal", len(indexed.get(page, ())) + 1)
        indexed.setdefault(page, []).append(copied)
    for page, page_records in indexed.items():
        ordinals = [int(record["ordinal"]) for record in page_records]
        if len(ordinals) != len(set(ordinals)):
            raise ValueError(f"duplicate marker ordinal on page {page}: {ordinals}")
    return indexed


def replace_visible_token(
    text: str,
    raw: str,
    restored: str,
    replacement_suffix: str,
    *,
    page: int,
    normalizer: Callable[[str], str] | None = None,
    inline_markers: tuple[str, ...] = (),
) -> str:
    """Replace one reviewed token while retaining embedded private-use markup."""
    variants = [raw]
    if normalizer is not None:
        normalized = normalizer(raw)
        if normalized != raw:
            variants.append(normalized)
    marker_class = re.escape("".join(inline_markers))
    match = None
    for variant in variants:
        if inline_markers:
            pattern = rf"[{marker_class}]*" + rf"[{marker_class}]*".join(
                re.escape(char) for char in variant
            ) + rf"[{marker_class}]*"
        else:
            pattern = re.escape(variant)
        match = re.search(pattern, text)
        if match:
            break
    if match is None:
        raise AssertionError(f"reviewed endnote token not found on page {page}: {raw!r}")

    styled = match.group(0)
    marker_positions: list[tuple[int, str]] = []
    visible_count = 0
    for char in styled:
        if char in inline_markers:
            marker_positions.append((visible_count, char))
        else:
            visible_count += 1
    rebuilt: list[str] = []
    for position in range(len(restored) + 1):
        rebuilt.extend(char for at, char in marker_positions if at == position)
        if position < len(restored):
            rebuilt.append(restored[position])
    replacement = "".join(rebuilt) + replacement_suffix
    return text[:match.start()] + replacement + text[match.end():]


def restore_page_records(
    text: str,
    page: int,
    records_by_page: dict[int, list[dict]],
    *,
    restored_text: Callable[[dict], str],
    replacement_suffix: Callable[[dict], str],
    normalizer: Callable[[str], str] | None = None,
    inline_markers: tuple[str, ...] = (),
) -> str:
    """Apply every reviewed marker on a page in recorded reading order."""
    for record in records_by_page.get(page, ()):
        text = replace_visible_token(
            text,
            record["raw_token"],
            restored_text(record),
            replacement_suffix(record),
            page=page,
            normalizer=normalizer,
            inline_markers=inline_markers,
        )
    return text
