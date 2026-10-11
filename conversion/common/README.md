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
