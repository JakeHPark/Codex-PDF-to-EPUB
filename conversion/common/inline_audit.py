"""DOM-aware review candidates for emphasis boundaries and displaced notes.

Findings require source review. This module never changes formatting or prose.
It reads semantic inline markup, not computed styles from external CSS.
"""
from __future__ import annotations

import re

BLOCKS = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'figcaption'}
SKIP = {'code', 'pre', 'math', 'svg', 'script', 'style'}
EP = '{http://www.idpf.org/2007/ops}type'


def local(element):
    return element.tag.rsplit('}', 1)[-1] if isinstance(element.tag, str) else ''


def _note(element):
    return (element.get(EP, '').split() and
            any(x in element.get(EP, '').split() for x in ['footnote', 'endnote'])) or element.get('role') in {'doc-footnote', 'doc-endnote'}


def _blocks(root):
    def visit(element, in_note=False):
        in_note = bool(in_note or _note(element))
        if local(element) in SKIP:
            return
        if local(element) in BLOCKS:
            yield element, in_note
        for child in element:
            yield from visit(child, in_note)
    yield from visit(root)


def inline_stream(element):
    """Return (character, italic, bold, linked-note-marker) tuples.

    Preserve br/object barriers and inherited semantic emphasis. A parent li
    containing block paragraphs is audited through those paragraphs instead.
    """
    out = []
    def visit(node, italic=False, bold=False, noteref=False, top=False):
        tag = local(node)
        if tag in SKIP or tag in {'img', 'br'} or (not top and tag in BLOCKS):
            out.append(('\n', False, False, False))
            return
        italic = italic or tag in {'em', 'i'}
        bold = bold or tag in {'strong', 'b'}
        noteref = noteref or 'noteref' in node.get(EP, '').split() or node.get('role') == 'doc-noteref'
        out.extend((c, italic, bold, noteref) for c in node.text or '')
        for child in node:
            visit(child, italic, bold, noteref)
            out.extend((c, italic, bold, noteref) for c in child.tail or '')
    visit(element, top=True)
    return out


def find_emphasis_issues(root, *, known_phrases=()):
    """Flag partial words, isolated spans, short gaps and dash-spanning styles.

    known_phrases contains already source-verified complete italic phrases;
    it detects incomplete occurrences, not whether a phrase deserves italics.
    Genuine isolated emphasis, internal puns and roman connectives will also
    be flagged. Retain individually reviewed exceptions in the book recipe.
    """
    issues = []
    def add(block, text, position, end, reason, style):
        issues.append(dict(block=block.get('id'), position=position, end=end,
                           token=text[position:end], reason=reason, style=style,
                           context=text[max(0, position-45):end+50]))
    for block, _ in _blocks(root):
        cs = inline_stream(block)
        text = ''.join(c for c, *_ in cs)
        words = list(re.finditer(r"[^\W\d_]+(?:[’'][^\W\d_]+)*", text))
        for style, index in [('italic', 1), ('bold', 2)]:
            letters = [row for row in cs if row[0].isalpha() and not row[3]]
            if len(letters) >= 8 and sum(row[index] for row in letters) / len(letters) >= .7:
                run = []
                for match in words + [None]:
                    roman = match is not None and not any(c[index] or c[3] for c in cs[match.start():match.end()])
                    if roman:
                        run.append(match)
                    else:
                        if 1 <= len(run) <= 3:
                            add(block, text, run[0].start(), run[-1].end(), 'roman outlier in mostly emphasized block', style)
                        run = []
            for match in words:
                flags = [c[index] for c in cs[match.start():match.end()]]
                if any(flags) and not all(flags):
                    add(block, text, *match.span(), 'partial-word emphasis', style)
            # Review every isolated styled word; vocabulary cannot decide which
            # of two identically spelled occurrences genuinely has emphasis.
            for i, match in enumerate(words):
                if not all(c[index] for c in cs[match.start():match.end()]):
                    continue
                neighbors = [words[j] for j in (i-1, i+1) if 0 <= j < len(words)]
                if neighbors and all(not any(c[index] for c in cs[n.start():n.end()]) for n in neighbors):
                    add(block, text, *match.span(), 'isolated emphasized word', style)
            for match in re.finditer(r'\S*[—–]\S*', text):
                if any(c[index] for c in cs[match.start():match.end()]):
                    add(block, text, *match.span(), 'emphasis at dash boundary', style)
            # Include consecutive weak words: a one-word fill misses "as a"
            # and "of St.". Punctuation and line/object boundaries stop a run.
            for i in range(1, len(words)-1):
                if not all(c[index] for c in cs[words[i-1].start():words[i-1].end()]):
                    continue
                for count in range(1, 4):
                    middle = words[i:i+count]
                    if len(middle) != count or i+count >= len(words):
                        break
                    after = words[i+count]
                    if any(len(m.group()) > 3 or any(c[index] for c in cs[m.start():m.end()]) for m in middle):
                        break
                    between = text[words[i-1].end():after.start()]
                    if re.search(r'[.!?;:“”\n—–]', between):
                        break
                    if all(c[index] for c in cs[after.start():after.end()]):
                        add(block, text, middle[0].start(), middle[-1].end(), 'short roman gap between emphasis', style)
                        break
        for phrase in known_phrases:
            for match in re.finditer(re.escape(phrase), text):
                flags = [row[1] for row in cs[match.start():match.end()]]
                if not all(flags):
                    add(block, text, *match.span(), 'incomplete reviewed italic phrase', 'italic')
    return issues


def find_unlinked_note_candidates(root):
    """Find bare symbol calls and citation-shaped note paragraphs in body text.

    Properly linked markers and semantic note containers are excluded. This
    cannot recover missing notes or distinguish every mathematical asterisk;
    source-region and numeric/symbolic inventories remain necessary.
    """
    issues = []
    for block, in_note in _blocks(root):
        if in_note:
            continue
        cs = inline_stream(block); text = ''.join(c for c, *_ in cs)
        patterns = [('note-shaped body paragraph', r"^\s*(?:[*†‡]|\d{1,3}[.)])\s*(?=See\b|Cf\.|Ibid\b|Editor[’']s [Nn]ote)"),
                    ('unlinked symbol note call', r'(?<=[\w.!?”’)])[*†‡]+(?=\s|$)')]
        for reason, pattern in patterns:
            for match in re.finditer(pattern, text):
                if any(row[3] for row in cs[match.start():match.end()]):
                    continue
                issues.append(dict(block=block.get('id'), position=match.start(),
                                   reason=reason, context=text[max(0, match.start()-45):match.end()+100]))
    return issues
