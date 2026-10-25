"""Cross-book audits for EPUB defects that are unsafe to autocorrect blindly."""

from __future__ import annotations

from dataclasses import dataclass
import html
import json
import re
import zipfile
from pathlib import Path


TAG_RE = re.compile(r"<[^>]+>")
ENDNOTE_LIKE_RE = re.compile(r"\S*[.!?][‘’'](?:\*+)?")


@dataclass(frozen=True)
class QuoteIssue:
    position: int
    character: str
    reason: str
    context: str


def visible_text(markup: str) -> str:
    return html.unescape(TAG_RE.sub("", markup))


def find_typographic_quote_issues(
    text: str, *, report_unclosed: bool = True
) -> list[QuoteIssue]:
    """Find impossible curly-quote nesting while preserving apostrophes.

    A closing single quote is treated as an apostrophe when it follows a word
    and no single quotation is currently open.  Consequently valid nesting
    such as ``“He called it ‘no,’”`` passes, while ``“co-act,’”`` and a raised
    note digit OCRed as ``attached.’`` are flagged for layout review.
    """
    stack: list[tuple[str, int]] = []
    issues: list[QuoteIssue] = []

    def add(position: int, char: str, reason: str) -> None:
        issues.append(QuoteIssue(
            position,
            char,
            reason,
            text[max(0, position - 36):position + 37],
        ))

    def close_quote(position: int, char: str, quote_type: str) -> None:
        matching = next(
            (index for index in range(len(stack) - 1, -1, -1)
             if stack[index][0] == quote_type),
            None,
        )
        if matching is None:
            add(position, char, f"closing {quote_type} quote has no matching opener")
            return
        if matching != len(stack) - 1:
            add(position, char, f"closing {quote_type} quote crosses an unclosed nested quote")
        # Resynchronize at the matching opener so one malformed cluster does
        # not turn every later quotation in the chapter into a false positive.
        del stack[matching:]

    for position, char in enumerate(text):
        if char == "“":
            stack.append(("double", position))
        elif char == "‘":
            stack.append(("single", position))
        elif char == "”":
            close_quote(position, char, "double")
        elif char == "’":
            previous = text[position - 1] if position else ""
            following = text[position + 1] if position + 1 < len(text) else ""
            # Classify internal contractions before consulting the quote stack.
            # A nested quote may contain "I'm" without ending at its apostrophe.
            if previous.isalnum() and following.isalnum():
                continue
            # A possessive inside a quoted title is not its closing delimiter:
            # ‘Haddocks’ Eyes’. Without this, a missing final single closer
            # appears balanced. Ambiguous capitalized dialogue is reviewable.
            if stack and stack[-1][0] == "single":
                before = re.search(r"\b[A-Z][A-Za-z]*s$", text[:position])
                if before and re.match(r"\s+[A-Z][a-z]", text[position + 1:]):
                    continue
            if stack and stack[-1][0] == "single":
                stack.pop()
                continue
            # Internal contractions/possessives, leading elisions (`’Twixt`,
            # `’gainst`), and abbreviation possessives (`Ph.D.’s`) are
            # apostrophes even though the glyph is also a closing quote.
            if previous.isalnum() or following.isalnum():
                continue
            close_quote(position, char, "single")
    if report_unclosed:
        for quote_type, position in stack:
            add(position, "“" if quote_type == "double" else "‘", f"unclosed {quote_type} quote")
    return issues


def find_endnote_like_punctuation(text: str) -> list[str]:
    """Inventory punctuation-shaped marker candidates; never rewrite them."""
    return [match.group(0) for match in ENDNOTE_LIKE_RE.finditer(text)]


def find_period_word_spacing_issues(text: str) -> list[dict]:
    """Flag periods touching a following Unicode letter; never autocorrect.

    Pass the visible text of each paragraph/block, joining inline spans but
    keeping separate blocks separate. Abbreviations, domains, filenames and
    technical identifiers are deliberate review candidates, not safe rewrites.
    Digit-to-digit decimals are excluded; ``1.An`` is still detected.
    """
    return [
        {"position": m.start(), "context": text[max(0, m.start()-45):m.end()+65]}
        for m in re.finditer(r"\.(?=[^\W\d_])", text)
    ]


def find_orphan_symbol_issues(text: str) -> list[dict]:
    """Flag implausibly isolated symbols for review, without rewriting them.

    Copyright notices and mathematical uses deliberately remain candidates.
    A numeric degree value is excluded, but a lone degree sign in prose is not.
    Pass readable block text, excluding actual markup and formula objects.
    """
    pattern = re.compile(r"[©®§†‡¤■□¶<>]|(?<!\d)°|[.!?][ \t]+(?:[-—,:;][ \t]*){2,}")
    return [
        {"position": match.start(), "symbol": match.group(),
         "context": text[max(0, match.start()-50):match.end()+60]}
        for match in pattern.finditer(text)
    ]


def find_ocr_punctuation_issues(text: str) -> list[dict]:
    """Review candidates only: abbreviations and foreign numerals may be valid.

    Pass complete readable blocks so emphasis boundaries cannot hide defects.
    Source inspection decides which punctuation or capitalization to restore.
    """
    import unicodedata

    patterns = [
        ("comma before possible sentence start", r",\s+(?:[A-Z][a-z]+\b|[AI]\b)"),
        ("isolated apostrophe", r"(?<!\S)['‘’](?!\S)"),
        ("conflicting punctuation", r"[,;:]\s*\.|[.!?][”’\"')\]]*[ \t]+,|,{2,}"),
        ("period before lowercase", r"(?<!\.)\.(?!\.)\s+[a-z]"),
        ("trademark symbol", r"[™℠]"),
        ("internal word symbol", r"(?<=[A-Za-z])[*^](?=[ \t]*[A-Za-z])"),
        ("embedded exclamation mark", r"(?<=[A-Za-z])!(?=[A-Za-z]|-[ \t\r\n]*[A-Za-z])"),
        ("space before closing quote", r"[ \t\u00a0]+(?:”|’(?=$|[\s\d,.;:!?—–”)\]]))"),
        ("period-apostrophe cluster", r"\.['’](?=\s|$|[,;:])"),
        ("possibly fused not a", r"\bnota\b"),
    ]
    issues = []
    # Review only: Latin `nota`, real mixed-case brands and foreign quotation
    # conventions must not be rewritten by an English OCR spelling rule.
    for match in re.finditer(r"\b[A-Za-z]{4,}\b", text):
        token = match.group()
        upper = sum(c.isupper() for c in token)
        lower = len(token) - upper
        if upper >= 3 and 0 < lower <= 2 and upper / len(token) >= .75:
            issues.append(dict(position=match.start(), symbol=token,
                               reason="lowercase outlier in uppercase word",
                               context=text[max(0, match.start()-50):match.end()+60]))
    for opener, closer in [("«", "»"), ("‹", "›")]:
        stack = []
        for position, char in enumerate(text):
            if char == opener:
                stack.append(position)
            elif char == closer:
                if stack:
                    stack.pop()
                else:
                    issues.append(dict(position=position, symbol=char,
                                       reason="unpaired guillemet",
                                       context=text[max(0, position-50):position+61]))
        for position in stack:
            issues.append(dict(position=position, symbol=opener,
                               reason="unpaired guillemet",
                               context=text[max(0, position-50):position+61]))
    # Inspect each complete dot run, not just adjacent pairs: a legitimate
    # sentence stop plus ellipsis has four dots, but mixed spacing can hide
    # malformed forms such as ". . ..". These remain review-only candidates.
    for match in re.finditer(r"\.(?:[ \t\r\n]*\.)+", text):
        run = match.group()
        count = run.count('.')
        gaps = re.findall(r"(?<=\.)[ \t\r\n]*(?=\.)", run)
        reasons = []
        if count == 2 or count > 4:
            reasons.append("suspicious ellipsis dot count")
        if any(gaps) and not all(gaps):
            reasons.append("mixed ellipsis spacing")
        if count >= 4 and re.search(r"[!?][”’\"')\]]*[ \t]*$", text[:match.start()]):
            reasons.append("redundant stop beside ellipsis")
        for reason in reasons:
            issues.append(dict(position=match.start(), symbol=run, reason=reason,
                               context=text[max(0, match.start()-50):match.end()+60]))
    # A legitimate inner closing single quote does not close its outer double.
    # This is a candidate only: source layout may intentionally continue a quote.
    if text.lstrip().startswith('"') and text.count('"') % 2 and re.search(r"[.!?]['’]\s*$", text):
        issues.append(dict(position=len(text.rstrip())-1, symbol=text.rstrip()[-1],
                           reason="unclosed outer double quotation", context=text[-120:]))
    for reason, pattern in patterns:
        for match in re.finditer(pattern, text):
            issues.append(dict(position=match.start(), symbol=match.group(), reason=reason,
                               context=text[max(0, match.start()-50):match.end()+60]))
    for position, char in enumerate(text):
        if ord(char) > 127 and unicodedata.category(char) == "Nd":
            issues.append(dict(position=position, symbol=char, reason="non-ASCII digit",
                               context=text[max(0, position-50):position+61]))
    return sorted(issues, key=lambda issue: issue['position'])


def find_ocr_slash_issues(text: str) -> list[dict]:
    """Review slash-shaped letters and asymmetric lexical slash spacing.

    Prose only: paths, code, ratios and verse separators need classification,
    not automatic removal. URLs are excluded; real slash compounds remain.
    """
    issues = []
    patterns = [
        ("slash-shaped word letters", r"(?<![\w/])[A-Za-z]+//(?=$|[\s.,;:!?—–”’\"')\]])"),
        ("slash-shaped initial letter", r"(?<![\w/:])/[A-Za-z]+\b"),
        ("slash-shaped final letter", r"\b[A-Za-z]+/(?=$|[-.,;:!?—–”’\"')\]])"),
        ("asymmetric lexical slash spacing", r"\b[A-Za-z][A-Za-z’-]*/[ \t]+(?=[A-Za-z])"),
    ]
    urls = [m.span() for m in re.finditer(r"\b\w+://\S+", text)]
    for reason, pattern in patterns:
        for match in re.finditer(pattern, text):
            if any(a <= match.start() < b for a, b in urls):
                continue
            issues.append(dict(position=match.start(), symbol=match.group(), reason=reason,
                               context=text[max(0, match.start()-50):match.end()+60]))
    return sorted(issues, key=lambda issue: issue['position'])


def find_degree_glyphs(text: str) -> list[dict]:
    """Inventory every degree-like glyph, including numeric ones, for review.

    A real 30° angle and OCR of a French superscript e are both candidates;
    this deliberately does not infer the intended letter or physical unit.
    """
    return [dict(position=m.start(), symbol=m.group(),
                 context=text[max(0, m.start()-40):m.end()+45])
            for m in re.finditer('[°º]', text)]


def validate_epub_policies(
    epub: str | Path,
    *,
    omit_front_matter: bool = True,
    expected_note_references: int | None = None,
    unresolved_marker_characters: str = "°®©",
    audit_typographic_quotes: bool = False,
    quote_issue_report: str | Path | None = None,
) -> None:
    """Enforce cross-book packaging policies on the final EPUB container."""
    with zipfile.ZipFile(epub) as archive:
        xhtml = {
            name: archive.read(name).decode("utf-8")
            for name in archive.namelist() if name.endswith(".xhtml")
        }
    combined = "\n".join(xhtml.values())
    if omit_front_matter:
        front_members = [name for name in xhtml if Path(name).stem.casefold() in {"front", "front-matter", "frontmatter"}]
        if front_members or re.search(r">\s*Front Matter\s*<", combined, re.IGNORECASE):
            raise AssertionError(f"front matter was required to be omitted: {front_members}")
    leaked = sorted(set(combined) & set(unresolved_marker_characters))
    if leaked:
        raise AssertionError(f"unresolved marker glyphs in packaged XHTML: {leaked}")
    if any("\ue000" <= char <= "\uf8ff" for char in combined):
        raise AssertionError("private-use conversion placeholders leaked into packaged XHTML")
    if expected_note_references is not None:
        actual = combined.count('epub:type="noteref"')
        if actual != expected_note_references:
            raise AssertionError(f"expected {expected_note_references} note references, found {actual}")

    if audit_typographic_quotes or quote_issue_report is not None:
        quote_issues = []
        for name, value in xhtml.items():
            if Path(name).name in {"nav.xhtml"}:
                continue
            for issue in find_typographic_quote_issues(
                visible_text(value), report_unclosed=False
            ):
                quote_issues.append((name, issue))
        if quote_issue_report is not None:
            report_path = Path(quote_issue_report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(
                json.dumps(
                    {
                        "count": len(quote_issues),
                        "records": [
                            {
                                "member": name,
                                "position": issue.position,
                                "character": issue.character,
                                "reason": issue.reason,
                                "context": issue.context,
                            }
                            for name, issue in quote_issues
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )
        if audit_typographic_quotes and quote_issues:
            sample = [
                f"{name}: {issue.reason}: {issue.context!r}"
                for name, issue in quote_issues[:8]
            ]
            raise AssertionError(
                f"{len(quote_issues)} mismatched typographic quotes: {sample}"
            )

    ids_by_member = {
        name: set(re.findall(r'\bid="([^"]+)"', value)) for name, value in xhtml.items()
    }
    for source_name, value in xhtml.items():
        for target_name, fragment in re.findall(r'href="([^"#]+\.xhtml)#([^"]+)"', value):
            resolved = str(Path(source_name).parent / target_name)
            if resolved not in ids_by_member or fragment not in ids_by_member[resolved]:
                raise AssertionError(f"broken fragment link from {source_name}: {target_name}#{fragment}")
