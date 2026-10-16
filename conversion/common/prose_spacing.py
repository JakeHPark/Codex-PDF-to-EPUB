"""Constrained prose spacing repairs, including across inline XHTML markup."""
import re

OPEN_QUOTE = re.compile(r"(?<=[^\W_])(?=“)", re.UNICODE)
# A spaced ellipsis or dot progression is not a sentence full stop. Do not
# consume line breaks, spaces after digits (numeric notation), or math/code.
BEFORE_STOP = re.compile(r"(?<=[^\W\d_]|[’”\)\]])[ \t\u00a0]+(?=\.(?!\s*\.|\d))", re.UNICODE)
# Require at least three short integers and an explicit conjunction. This
# excludes decimal commas and thousands groups; formula/code nodes are barriers
# in the XHTML normalizer, and plain-text callers must supply prose only.
ENUMERATION = re.compile(r"(?<![\w.,])\d{1,2}(?:,[ \t]*\d{1,2})+(?:,[ \t]*|[ \t]+)(?:and|or)[ \t]+\d{1,2}(?![\w]|,\d)")


def spacing_edits(text):
    """Return nonoverlapping (start, end, replacement) edits in plain prose."""
    edits = [(m.start(), m.end(), " ") for m in OPEN_QUOTE.finditer(text)]
    edits += [(m.start(), m.end(), "") for m in BEFORE_STOP.finditer(text)]
    for group in ENUMERATION.finditer(text):
        edits += [(group.start()+m.end(), group.start()+m.end(), " ")
                  for m in re.finditer(r",(?=\d)", group.group())]
    return sorted(edits)


def normalize_prose_spacing(text):
    for start, end, replacement in reversed(spacing_edits(text)):
        text = text[:start] + replacement + text[end:]
    return text


def normalize_xhtml_prose_spacing(root):
    """Repair text-node boundaries without flattening emphasis or links.

    Accept an lxml root. Treat excluded inline objects as barriers, so a
    formula or code sample is never normalized as ordinary prose.
    """
    blocks = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "figcaption", "td", "th"}
    excluded = {"math", "svg", "pre", "code", "script", "style", "img", "br"}
    count = 0
    def local(e):
        return e.tag.rsplit("}", 1)[-1] if isinstance(e.tag, str) else ""
    def is_excluded(e):
        return local(e) in excluded or bool(set(e.get("class", "").split()) & {"math", "equation", "dot-pattern"})
    for block in root.iter():
        if local(block) not in blocks or any(is_excluded(a) for a in block.iterancestors()):
            continue
        if any(e is not block and local(e) in blocks for e in block.iter()):
            continue  # Nested paragraphs/cells are processed independently.
        slots = []
        def walk(e):
            if is_excluded(e):
                slots.append((None, None, "\0"))
                return
            if e.text:
                slots.append((e, "text", e.text))
            for child in e:
                walk(child)
                if child.tail:
                    slots.append((child, "tail", child.tail))
        walk(block)
        joined = "".join(s for _, _, s in slots)
        edits = spacing_edits(joined)
        count += len(edits)
        offset = 0
        for e, key, s in slots:
            end_offset = offset + len(s)
            if e is not None:
                changes = []
                for start, end, replacement in edits:
                    if start == end and offset <= start < end_offset:
                        changes.append((start-offset, start-offset, replacement))
                    elif start < end_offset and end > offset:
                        changes.append((max(start-offset, 0), min(end-offset, len(s)), replacement if start >= offset else ""))
                for start, end, replacement in reversed(changes):
                    s = s[:start] + replacement + s[end:]
                setattr(e, key, s)
            offset = end_offset
    return count
