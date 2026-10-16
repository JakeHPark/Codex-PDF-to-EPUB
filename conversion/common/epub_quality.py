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
        ("isolated apostrophe", r"(?<!\S)['‘’](?!\S)"),
        ("conflicting punctuation", r"[,;:]\s*\.|,{2,}"),
        ("period before lowercase", r"(?<!\.)\.(?!\.)\s+[a-z]"),
        ("trademark symbol", r"[™℠]"),
        ("internal word symbol", r"(?<=[A-Za-z])[*^](?=[ \t]*[A-Za-z])"),
        ("period-apostrophe cluster", r"\.['’](?=\s|$|[,;:])"),
    ]
    issues = []
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
