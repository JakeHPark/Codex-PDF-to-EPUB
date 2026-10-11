# Shared conversion helpers

`ocr_corrections.py` is the cross-book, brute-force OCR correction layer. Add
an entry only when the damaged form has one defensible repair in ordinary
prose. Prefer a whole-word or otherwise constrained rule whenever a damaged
token can also occur inside a valid word.

Examples:

- `ina` becomes `in a`, but `Karenina` remains unchanged.
- `Ihave` becomes `I have`.
- `selfknowledge` becomes `self-knowledge`.
- the impossible duplicated opening sequence `‘““` becomes one opening double
  quotation mark; plausible nested sequences are not changed.
- adjacent identical curly single quotation marks (`‘‘` or `’’`) become the
  corresponding double quotation mark; valid nested quotations alternate
  quote styles and therefore cannot require either identical pair.
- a primary double quotation ending in an OCRed single-plus-double cluster is
  normalized only when the short quoted span contains no nested single opener;
  valid nested forms such as `“He called it ‘no,’”` remain unchanged.

Keep ambiguous or source-dependent corrections out of this module. Names,
quotations, citations, superscript note markers, decorative typography, and
page-layout artifacts must remain with the relevant book under `tmp/pdfs/`
and should be backed by a rendered-page check and a regression assertion.

Call the common normalizer after page extraction and again after line/page
joining. Dehyphenation can create a fused token such as `selfknowledge` that
did not exist until the structural reconstruction step.

Run the focused checks with:

```sh
python3 conversion/common/test_ocr_corrections.py
```

Other shared safeguards:

- `endnote_recovery.py` applies reviewed layout evidence without assuming one
  marker per page and preserves inline emphasis markers while replacing a
  damaged token.
- `page_reconstruction.py` prevents a detached marginal fragment from being
  fused to a structural heading on the following physical page.
- `epub_quality.py` audits curly-quotation nesting, inventories punctuation
  that may be a damaged superscript, verifies every XHTML fragment link,
  rejects unresolved marker glyphs and private-use placeholders, enforces an
  expected note-reference count, and can require front matter to be absent.
  Pass a book-specific `quote_issue_report` path to retain ambiguous findings
  as a review queue under `tmp/`; use strict quote auditing only after that
  queue has been visually reviewed, because detection is safer to generalize
  than correction.

Run their focused checks with:

```sh
python3 conversion/common/test_conversion_quality.py
```
