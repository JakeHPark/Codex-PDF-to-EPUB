"""Heading-aware section slicing for PDFs whose chapters share pages."""

from collections import Counter
import re
import unicodedata


def _heading_words(value):
    normalized = unicodedata.normalize("NFKD", value).casefold()
    normalized = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.findall(r"[a-z0-9]+", normalized)


def strip_opening_display_blocks(text, generated_title):
    """Remove every leading printed-title block covered by a generated title.

    Display headings often contain a main title and an italic subtitle separated
    by a blank line. A builder that removes only the first block leaves the
    subtitle as false opening prose. Preserve the historical one-block fallback
    for heavily damaged OCR, then remove further blocks only when all their
    normalized words are still accounted for by the generated section title.
    """
    blocks = [block for block in re.split(r"\n\s*\n", text.strip()) if block.strip()]
    if not blocks:
        return "", []
    remaining = Counter(_heading_words(generated_title))
    removed = [blocks.pop(0)]
    for word in _heading_words(removed[0]):
        if remaining[word]:
            remaining[word] -= 1
    while blocks:
        words = _heading_words(blocks[0])
        counts = Counter(words)
        if not words or any(counts[word] > remaining[word] for word in counts):
            break
        removed.append(blocks.pop(0))
        remaining.subtract(counts)
    return "\n\n".join(blocks).strip(), removed


def split_at_heading(text, heading_pattern):
    """Return the content before and after one printed heading.

    ``heading_pattern`` is book-specific because OCR can distort display type,
    but page ownership is generic: prose before the heading belongs to the
    preceding section and prose after it belongs to the new section.
    """
    # Formatting recovery may already have inserted private-use span markers.
    # Match against marker-free text, then translate the span back so the body
    # retains every marker outside the discarded printed heading.
    plain_chars = []
    plain_to_source = []
    for source_index, char in enumerate(text):
        if "\ue000" <= char <= "\uf8ff":
            continue
        plain_to_source.append(source_index)
        plain_chars.append(char)
    plain_to_source.append(len(text))
    plain = "".join(plain_chars)
    match = re.search(heading_pattern, plain, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        raise ValueError(f"section heading not found: {heading_pattern!r}")
    source_start = plain_to_source[match.start()]
    source_end = plain_to_source[match.end()]
    return text[:source_start].strip(), text[source_end:].strip()


def section_fragments(page_texts, sections, final_page):
    """Yield ``(section_id, fragments)`` using heading locations, not page edges.

    Sections are dictionaries with ``id``, ``start_page``, and an optional
    ``heading_pattern``.  The first section may omit a heading.  A boundary page
    is included on both sides and divided at the following section's heading.
    """
    for index, section in enumerate(sections):
        next_section = sections[index + 1] if index + 1 < len(sections) else None
        start_page = section["start_page"]
        stop_page = next_section["start_page"] if next_section else final_page
        fragments = []
        for page in range(start_page, stop_page + 1):
            value = page_texts[page]
            if page == start_page and section.get("heading_pattern"):
                _, value = split_at_heading(value, section["heading_pattern"])
            if next_section and page == next_section["start_page"]:
                value, _ = split_at_heading(value, next_section["heading_pattern"])
            if value.strip():
                fragments.append(value.strip())
        yield section["id"], fragments
