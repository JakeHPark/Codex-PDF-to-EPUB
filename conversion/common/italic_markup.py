"""Align page-level italic evidence to extracted text and add safe markers."""

import difflib
import json
import re
import unicodedata
from pathlib import Path

EM_START = "\ue100"
EM_END = "\ue101"
WORD_RE = re.compile(r"[^\W_]+(?:[’'\-][^\W_]+)*", re.UNICODE)


def normalize_word(value):
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(char for char in value if not unicodedata.combining(char))
    return "".join(char for char in value if char.isalnum())


def mark_page_italics(text, page, evidence_directory):
    """Return text with private-use emphasis markers plus alignment statistics."""
    evidence = Path(evidence_directory) / f"{page:04d}.json"
    if not evidence.exists():
        return text, {"page": page, "evidence": False, "candidates": 0, "applied": 0}
    detected = json.loads(evidence.read_text(encoding="utf-8"))["words"]
    text, fused_repairs = repair_fused_word_boundaries(text, detected)
    source = list(WORD_RE.finditer(text))
    detected_words = [normalize_word(item["text"]) for item in detected]
    source_words = [normalize_word(match.group(0)) for match in source]
    matcher = difflib.SequenceMatcher(
        None, detected_words, source_words, autojunk=False
    )
    mapped = {}
    matched = 0
    for block in matcher.get_matching_blocks():
        for offset in range(block.size):
            detected_index = block.a + offset
            source_index = block.b + offset
            matched += 1
            if detected[detected_index]["likely_italic"]:
                mapped[source_index] = detected[detected_index]
    insertions = []
    for source_index in mapped:
        match = source[source_index]
        insertions.append((match.start(), EM_START))
        insertions.append((match.end(), EM_END))
    for position, marker in sorted(insertions, reverse=True):
        text = text[:position] + marker + text[position:]
    candidates = sum(item["likely_italic"] for item in detected)
    return text, {
        "page": page,
        "evidence": True,
        "source_words": len(source_words),
        "detected_words": len(detected_words),
        "matched_words": matched,
        "alignment": round(matched / max(1, len(source_words)), 4),
        "candidates": candidates,
        "applied": len(mapped),
        "fused_boundary_repairs": fused_repairs,
    }


def repair_fused_word_boundaries(text, detected):
    """Restore separators lost where adjacent PDF text/font runs were fused.

    PDF text layers sometimes expose ``TitlePlace`` even though the rendered
    page reads ``Title, Place``.  When consecutive source words and consecutive
    OCR words align, but the source contains no characters between them, use
    the OCR tokens' edge punctuation and a word space.  This deliberately does
    nothing when the source already has any separator.
    """
    source = list(WORD_RE.finditer(text))
    detected_words = [normalize_word(item["text"]) for item in detected]
    source_words = [normalize_word(match.group(0)) for match in source]

    # Find unambiguous one-to-many matches even when nearby OCR errors make the
    # word-level diff group a larger replacement. This catches, for example,
    # ``CalifornianApril`` against ``Californian,`` + ``April``.
    broad_insertions = []
    detected_groups = {}
    for detected_start in range(len(detected_words)):
        for width in range(2, 5):
            pieces = detected[detected_start:detected_start + width]
            if len(pieces) != width or len({item.get("line") for item in pieces}) != 1:
                continue
            key = "".join(detected_words[detected_start:detected_start + width])
            detected_groups.setdefault(key, []).append(pieces)
    for source_index, source_word in enumerate(source_words):
        candidates = detected_groups.get(source_word, [])
        if len(candidates) != 1:
            continue
        pieces = candidates[0]
        consumed = 0
        offsets = []
        observed_punctuation = False
        for left_piece, right_piece in zip(pieces, pieces[1:]):
            left_word = WORD_RE.search(left_piece["text"])
            right_word = WORD_RE.search(right_piece["text"])
            if not left_word or not right_word:
                offsets = []
                break
            consumed += len(left_word.group(0))
            if consumed >= len(source[source_index].group(0)):
                offsets = []
                break
            separator = left_piece["text"][left_word.end():] + " " + right_piece["text"][:right_word.start()]
            observed_punctuation = observed_punctuation or any(not char.isspace() for char in separator)
            offsets.append((source[source_index].start() + consumed, separator))
        if observed_punctuation:
            broad_insertions.extend(offsets)
    for position, separator in reversed(sorted(set(broad_insertions))):
        text = text[:position] + separator + text[position:]

    source = list(WORD_RE.finditer(text))
    source_words = [normalize_word(match.group(0)) for match in source]

    matcher = difflib.SequenceMatcher(None, detected_words, source_words, autojunk=False)
    pairs = []
    for block in matcher.get_matching_blocks():
        pairs.extend((block.a + offset, block.b + offset) for offset in range(block.size))

    insertions = []
    # One source token can contain two OCR words when a PDF font-run boundary
    # loses both punctuation and whitespace: ``WritingsOxford`` versus
    # ``Writings,`` + ``Oxford,``. Recover splits bracketed by normal matches.
    for tag, detected_start, detected_end, source_start, source_end in matcher.get_opcodes():
        if tag != "replace" or source_end - source_start != 1:
            continue
        if not 2 <= detected_end - detected_start <= 4:
            continue
        pieces = detected[detected_start:detected_end]
        if len({item.get("line") for item in pieces}) != 1:
            continue
        if "".join(normalize_word(item["text"]) for item in pieces) != source_words[source_start]:
            continue
        source_match = source[source_start]
        source_value = source_match.group(0)
        offsets = []
        consumed = 0
        valid = True
        for left_piece, right_piece in zip(pieces, pieces[1:]):
            left_word = WORD_RE.search(left_piece["text"])
            right_word = WORD_RE.search(right_piece["text"])
            if not left_word or not right_word:
                valid = False
                break
            consumed += len(left_word.group(0))
            if consumed >= len(source_value):
                valid = False
                break
            separator = left_piece["text"][left_word.end():] + " " + right_piece["text"][:right_word.start()]
            offsets.append((source_match.start() + consumed, separator))
        if valid:
            insertions.extend(offsets)

    for (detected_a, source_a), (detected_b, source_b) in zip(pairs, pairs[1:]):
        if detected_b != detected_a + 1 or source_b != source_a + 1:
            continue
        if detected[detected_a].get("line") != detected[detected_b].get("line"):
            continue
        left, right = source[source_a], source[source_b]
        existing_separator = text[left.end():right.start()]
        left_token = detected[detected_a]["text"]
        right_token = detected[detected_b]["text"]
        left_word = WORD_RE.search(left_token)
        right_word = WORD_RE.search(right_token)
        if not left_word or not right_word:
            continue
        trailing = left_token[left_word.end():]
        leading = right_token[:right_word.start()]
        if existing_separator:
            # OCR has distinct words but the text layer has punctuation with no
            # following space (often another font-run join such as ``,Grey``).
            if any(char.isspace() for char in existing_separator):
                continue
            if trailing == existing_separator and not leading:
                insertions.append((right.start(), " "))
            continue
        separator = trailing + " " + leading
        insertions.append((left.end(), separator))

    insertions = sorted(set(insertions))
    for position, separator in reversed(insertions):
        text = text[:position] + separator + text[position:]
    return text, len(broad_insertions) + len(insertions)


def escape_emphasis_markers(escaped_text):
    rendered = escaped_text.replace(EM_START, "<em>").replace(EM_END, "</em>")
    return re.sub(r"</em>(\s+)<em>", r"\1", rendered)


def plain_marked_text(text):
    return text.replace(EM_START, "").replace(EM_END, "")


def remove_verified_word_hyphens(text, repairs):
    """Remove only reviewed word hyphens, even across inline style markers.

    The caller supplies source-verified whole-word pairs. Keep emphasis markers
    in their original positions and reject repairs that change other characters.
    """
    for damaged, restored in repairs.items():
        if '-' not in damaged or damaged.replace('-', '') != restored:
            raise ValueError(f'Not a hyphen-only repair: {damaged!r}')
        positions = [i for i, c in enumerate(text) if c not in {EM_START, EM_END}]
        visible = ''.join(text[i] for i in positions)
        removals = set()
        for match in re.finditer(r'(?<!\w)' + re.escape(damaged) + r'(?!\w)', visible):
            removals.update(positions[i] for i in range(match.start(), match.end())
                            if visible[i] == '-')
        text = ''.join(c for i, c in enumerate(text) if i not in removals)
    return text


def visible_first_character(line):
    return plain_marked_text(line)[:1]


def remove_discretionary_hyphen(joined):
    if joined.endswith("-" + EM_END):
        return joined[: -(len(EM_END) + 1)] + EM_END
    if joined.endswith("-"):
        return joined[:-1]
    return None
