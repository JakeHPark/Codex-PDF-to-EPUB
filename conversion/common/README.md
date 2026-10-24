# Shared helper catalog

These helpers support [the conversion workflow](../README.md); they do not form
an automatic whole-book pipeline. [AGENTS.md](../../AGENTS.md) defines the
required release gates. Import and call the applicable helpers explicitly in
each book recipe, and validate the packaged result with book-specific evidence.

## Dependencies and tests

Use Python 3. Most helpers use the standard library. Pixel analysis also needs
Pillow; OCR hOCR parsing needs lxml; `scan_styles.py` needs NumPy; digital font
inspection needs fontTools and a compatible PyMuPDF document supplied by the
caller. Batch recovery invokes external Poppler and Tesseract executables.
`common/tessdata/eng.traineddata` supplies the bundled English OCR model;
other languages and scholarly alphabets need reviewed source-specific handling.

From the repository root, with these dependencies available:

```sh
python3 -m unittest discover -s conversion/common -p 'test_*.py'
```

Focused tests are listed below. Modules use both repository-qualified and
sibling imports; use discovery from the root, or explicitly provide the root
and `conversion/common` on `PYTHONPATH` when invoking an individual test.
Shared tests establish helper behavior, not the quality of a generated EPUB.

## Extraction, geometry and reading order

| Module / API | Input and output | Scope and limits | Focused tests |
| --- | --- | --- | --- |
| [section_boundaries.py](section_boundaries.py): `split_at_heading`, `section_fragments` | Page text + verified heading patterns/section map → section fragments. | Treat ranges as search bounds; split shared pages at headings. Missing expected headings fail instead of dropping unknown prefixes. | `test_conversion_quality.py` covers display stripping; shared-page splitting also needs each recipe's complete boundary assertions. |
| Same module: `strip_opening_display_blocks` | Opening text + generated title → text without represented display blocks. | Removes consecutive title/subtitle blocks only while words are accounted for by the generated title; preserve actual opening prose. | `test_conversion_quality.py` |
| [page_reconstruction.py](page_reconstruction.py): `starts_indented_paragraph` | Current line edge + continuation content edge → indent decision. | Measure from the block's text edge, not its number/bullet or preceding box. Caller classifies headings, lists and quotations first. | `test_page_reconstruction.py` |
| Same module: `drop_detached_boundary_debris` | Two page texts → cleaned preceding text + removed fragments. | Only tiny isolated uppercase tails before recognizable headings; not a general prose deletion rule. | `test_conversion_quality.py` |
| [digital_pdf.py](digital_pdf.py): `GlyphSemantics`, `recover_ligature`, `position_key` | Positioned font/glyph evidence → glyph semantics and text alignment keys. | Inspect supported CFF glyph names for small capitals/superscripts. Not all fonts expose them; absence is not proof of roman text. Does not OCR/rewrite prose. | Source-specific font and complete-stream checks; no dedicated shared test file. |
| Same module: `continues_wrapped_caption` | Adjacent positioned lines → caption continuation candidate. | Detect font-changing wrapped captions. Crop starts below the complete caption and stops before the next real subsection; review visually. | Source-specific crop and caption checks; no dedicated shared test file. |
| [sidebars.py](sidebars.py): `find_marginal_blocks` | Positioned lines + known main-prose IDs → marginal-block candidates. | Geometry and weighted font evidence support review; exclude captions, object labels and headings first. Does not choose semantic role or placement automatically. | `test_sidebars.py` |

## OCR text and spacing

### `ocr_corrections.py`

`apply_common_ocr_corrections(text)` applies constrained cross-book repairs to
**OCR-derived prose**. Call after extraction and again after line/page joining,
which may create a new fused token. Do not apply it to clean digital/HTML text
just to standardize the pipeline. Do not feed code or mathematics through it.

Rules include bounded forms such as `Ihave`, `ina`, `asystem`, `Itis`, `It"s`, `Mosi`,
`Yoii` and `selfknowledge`; valid substrings such as `Karenina`, `Otitis`,
`arthritis`, `Mosiac` and longer names must survive. These are OCR defaults,
not dictionary-based spelling correction; retain source-verified exceptions.
Whole-token `iato`/`Iato` becomes `into`/`Into`. A detached `a`/`A` is rejoined
only with the complete fragments `bolitionist`, `bolitionists` or `bolitionism`;
capitalization is preserved. Other detached initials remain review candidates,
and articles, logical symbols, longer tokens and all-capital identifiers survive.
Standalone prose `a//` is repaired to `all`; `a//b`, `a//2`, paths and spaced
division operators are preserved. Recalculate token-length style decisions
after a spelling/glyph repair, using the original positioned pixel evidence:
otherwise restored `all` can still fail a short-token emphasis filter.
The standalone `8c` ampersand repair needs source context because that token
can be meaningful in technical text.

Quotation-cluster rules cover demonstrated impossible OCR forms: duplicated
curly singles, malformed opening clusters, and a primary double-quote closer
when its span has no nested single opener. Valid nested quotations are protected.
This normalizer is **not** a complete straight-to-typographic quote converter.
Names, source-dependent glyphs, damaged note markers and ambiguous punctuation
remain positioned or contextual decisions in the book recipe.

Tests: `test_ocr_corrections.py`.

### `prose_spacing.py`

- `spacing_edits(text)` returns constrained edits.
- `normalize_prose_spacing(text)` applies them to plain prose.
- `normalize_xhtml_prose_spacing(root)` applies them across inline markup while
  preserving the DOM and respecting block, `br`, code and formula boundaries.

Repairs include a word fused to an opening curly double quote, a stray space
before a sentence stop, and missing comma spaces in a constrained enumeration
of at least three short integers with `and` or `or`. Preserve ellipses,
decimals, thousands groups and mathematical notation. The common OCR normalizer
calls the plain-text helper; clean structured sources can call the XHTML form
when an extraction defect is demonstrated. These are not general French or
multilingual punctuation-spacing rules.

Tests: `test_prose_spacing.py`.

## Formatting evidence and semantic spans

`navigation.py:heading_label(heading)` accepts an ElementTree or lxml heading
and returns a whitespace-normalized plain label without explicit EPUB
`noteref` or ARIA `doc-noteref` elements. It preserves their tails, surrounding
emphasis text, ordinary digits and unclassified superscripts, and leaves the
heading unchanged. Identify note calls before using it; it cannot recognize
an unmarked citation digit. Tests: `test_navigation.py`.

| Module / API | Contract | Required review | Tests |
| --- | --- | --- | --- |
| [detect_italics.py](detect_italics.py) CLI | Rendered image + hOCR from that same image → positioned slant/gain and likely-italic evidence. | Pixel evidence is not an unattended rewrite. Calibrate for the source; check short words, roman controls and complete spans. See CLI `--help`. | Source-specific visual calibration. |
| [batch_detect_italics.py](batch_detect_italics.py) CLI | PDF + physical range/executable paths → resumable per-page JSON. | Processes the full selected range; temporary renderings/hOCR are deleted. Completed JSON is reused, so invalidate stale caches when inputs change. | Source-specific page coverage and calibration. |
| [scan_styles.py](scan_styles.py): `measure_word` | Grayscale image + pixel box → stroke survival, slant, gain and ink count. | Needs NumPy; calibrate weight/slant separately at the same scale/type size. Thresholds and accepted styles belong to the book. | `test_scan_styles.py` |
| [italic_markup.py](italic_markup.py): `mark_page_italics` | Page text, physical page number and evidence directory → marked text + coverage/alignment/application statistics. | Aligns occurrences, not a global vocabulary; repairs constrained OCR-observed fused separators. Reads four-digit page JSON filenames. Missing evidence returns unchanged text with `evidence: false`; caller must enforce expected page coverage. | Book-specific alignment/style/coverage checks. |
| Same module: `escape_emphasis_markers`, `plain_marked_text` | Escaped/marked text → controlled markup or plain text. | Escape source text before turning internal markers into semantic tags. Reject leaked private-use markers in final XHTML. | Packaged-output marker and emphasis checks. |
| Same module: `remove_verified_word_hyphens` | Marked text + source-verified whole-word repairs → text retaining emphasis markers. | Rejects repairs changing anything except hyphens; check final whole-word emphasis, not just spelling. | `test_italic_repairs.py` |

The [workflow README](../README.md#recover-scan-formatting-with-the-shared-tools)
has runnable single-page and batch examples. The [typography guide](../guides/typography.md)
requires a second audit after joining and structural rewrites: complete titles,
short styled outliers, partly styled words, missing styles and negative roman
boundaries cannot be proven correct by classifier counts.

### `inline_audit.py`

`find_emphasis_issues(root, known_phrases=())` inspects semantic `em`/`i` and
`strong`/`b` across text/tail nodes. It reports partly styled words, isolated
emphasized words, roman outliers in mostly emphasized blocks, dash boundaries
and one-to-three short roman words between
emphasized spans. Supply source-verified complete italic phrases to detect
incomplete occurrences. `br`, images, code and math are barriers. It does not
resolve external CSS or infer whether a title/foreign phrase deserves emphasis.
Genuine emphasis, mixed-style puns and roman conjunctions remain review
candidates; never apply the findings as blanket corrections.

`find_unlinked_note_candidates(root)` reports bare symbol calls and note-shaped
body paragraphs such as `*See …`, excluding linked markers and semantic note
containers. It cannot locate missing source regions or prove note completeness.
Inventory numeric and symbolic notes independently in the positioned source.

Run these on the packaged XHTML after every rebuild. Gate release on resolving
findings or individually source-reviewing them. A book may persist a fingerprint
of each reviewed finding including its block text and style stream; new or
changed findings must fail until reviewed. A generated report alone is not a
pass, and a global exemption for a word or reason hides genuine regressions.
Tests: `test_inline_audit.py`.

`package_audit.audit_epub(epub, known_phrases=(), reviewed_keys=())` also checks
periods touching letters across inline styles (abbreviations and domains require
individual review). It runs these
style/note checks together with punctuation, slash and degree-glyph inventories
on the actual ZIP's XHTML. It also reports exclamation marks embedded between
letters, across inline markup;
those are source-review candidates, not automatic letter replacements.
It always runs the typographic quote checker
on semantic blocks, including unclosed openers and across inline styles.
Continued quotations need individual source-reviewed fingerprints; a closing
single mark after a word can otherwise conceal a missing double closer.
Capitalized plural possessives followed by a capitalized title word inside a
single quotation are treated as apostrophes, so `‘Haddocks’ Eyes` cannot falsely
balance a missing final single mark. Ambiguous capitalized speech attributions
remain source-review candidates, rather than automatic punctuation repairs.
It returns per-block fingerprints, all findings and
an `unreviewed_count`. Fingerprints include the block's complete text and style
stream, so a changed occurrence invalidates its earlier review. The standalone
`package_audit.py` CLI requires `--report`, accepts `--phrases` and `--reviewed`
JSON files, and exits nonzero for unresolved findings. `--inventory` only
collects candidates; it is not a release pass. This does not replace container,
source-coverage or reader validation. Tests: `test_package_audit.py`.

## Reviewed note recovery

[endnote_recovery.py](endnote_recovery.py) provides `load_reviewed_records`,
`index_records_by_page`, `replace_visible_token` and `restore_page_records`.
It applies **already reviewed** glyph decisions, supports multiple markers on
one page and preserves inline emphasis markers while replacing a visible token.

The caller supplies source positions, selected digits, punctuation decisions,
section association and semantic links. The helper does not determine what an
ambiguous glyph means or prove the ordered note sequence. Check entries,
reference occurrences, repeated references, forward/backlinks and reader output
separately. Tests: `test_conversion_quality.py`.

## Quality detectors and package-policy checks

[epub_quality.py](epub_quality.py) exposes:

| API | Detects / checks | Does not establish |
| --- | --- | --- |
| `find_typographic_quote_issues(text, report_unclosed=True)` | Curly quotation nesting and mismatched closers, with contextual apostrophe handling. | Does not flag straight ASCII prose quotes or convert them. Continued quotation reopeners, linked reference digits, literal notation and measurements need semantic handling/review. |
| `find_period_word_spacing_issues(text)` | Touching sentence-stop/word candidates. | Abbreviations, initials, domains and code can be valid; findings are not automatic replacements. |
| `find_orphan_symbol_issues(text)` | Suspicious isolated symbols. | Cannot distinguish a real degree sign or note marker from scan noise without source evidence. |
| `find_ocr_punctuation_issues(text)` | Punctuation-cluster candidates, mixed ellipsis spacing, two or more than four dots, redundant stops beside ellipses, unpaired guillemets, whole-token `nota`, and lowercase outliers in mostly uppercase words. | Review only; four dots can mean a sentence stop plus omission. `nota` can be Latin, mixed case can be intentional, and guillemets can continue across blocks. Does not rewrite text. Case threshold: at least three uppercase letters, one or two lowercase letters, at least 75% uppercase, ASCII-letter token of length four or more. |
| `find_ocr_slash_issues(text)` | Slash-shaped initial/final letters and asymmetric lexical slash spacing. | Paths, code, ratios and verse require semantic classification; only URLs are excluded automatically. |
| `find_degree_glyphs(text)` | Every `°`/`º`, including numeric occurrences. | Does not distinguish real angles/temperatures from an ordinal or note OCR error; source-review each use. |
| `find_endnote_like_punctuation(text)` | Punctuation-shaped possible note markers. | Does not recover digits, association or sequence. |
| `visible_text(markup)` | Lightweight tag stripping and entity decoding. | Not a semantic reader export. It does not reconstruct block/`br` spacing or separate note references; use a DOM-aware visible stream for those audits. |
| `validate_epub_policies(epub, ...)` | Selected marker/placeholder rules, optional note-reference count, optional quote report and local fragment targets in the actual package. | Not full ZIP/XML/manifest/spine/cover, completeness, typography or reader validation. Use the book validator for the remaining release gates. |

Important defaults and integration limits:

- `omit_front_matter=True` is a legacy filename/label check, **not the project's
  front-matter policy**. Pass `False` when preserving substantive opening material;
  enforce the actual retention/omission inventory separately. Never remove an
  authored preface to satisfy a helper default.
- `unresolved_marker_characters="°®©"` rejects those glyphs literally. Source-
  verified legitimate uses need a book-specific contextual audit and appropriate
  configuration; do not exempt an entire glyph class to hide unreviewed markers.
- Private-use placeholders are rejected. Convert internal emphasis/formula markers
  before calling package validation.
- `expected_note_references` counts serialized `epub:type="noteref"` occurrences.
  It does not prove ordering, unique entries, repeated-reference coverage or correct
  association. Add explicit DOM and source-inventory checks.
- `audit_typographic_quotes=False` by default. A `quote_issue_report` saves findings;
  strict auditing must be explicitly enabled. The package helper uses
  `report_unclosed=False`; call the standalone detector with reviewed semantic
  text if unclosed openers must also be checked. Resolve or individually account
  for findings rather than treating creation of the report as a pass.
- Audit across inline markup without inserting spaces within contractions. Preserve
  block and `br` boundaries; account for note-reference digits separately. Source-
  verified quotation reopeners across paragraphs are not missing closing marks.
- Add an explicit inventory of remaining ASCII `'`/`"` in prose, captions, headings,
  notes and relevant alternative text. Classify primes, code, symbolic strings,
  URLs and damaged numerical tokens separately. A successful curly-quote audit
  alone cannot enforce the typographic-quote rule.

Tests: `test_conversion_quality.py`, `test_period_spacing.py`,
`test_orphan_symbols.py`, and `test_ocr_punctuation.py`.

## Extending a helper

Shared detectors may be broad; shared corrections must be narrow, explainable
and tested against legitimate lookalikes. Keep book-specific thresholds, word
choices and reviewed exceptions outside this directory. Update this catalog
when an API/default changes, and add the reusable decision rule to the relevant
[guide](../README.md#documentation-map), rather than appending another unrelated
section to AGENTS.md.
