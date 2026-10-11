# Reusable conversion tooling

Only book-independent conversion code lives here. Book-specific builders,
validators, corrections, evidence, and intermediate products live under
`tmp/pdfs/`.

## Layout

- `common/detect_italics.py`: experimental but useful pixel-based italic detector.
- `common/tessdata/eng.traineddata`: reusable English OCR model.

## Recovering italics from a scan

Prefer style-bearing source data in this order:

1. Tagged PDF or trustworthy PDF font spans.
2. ABBYY XML or hOCR containing explicit italic/bold attributes.
3. Word bounding boxes aligned with rendered pixels.
4. Source-verified contextual overrides.

Render a page and produce hOCR from the same image:

```bash
pdftoppm -f PAGE -l PAGE -r 150 -png -singlefile \
  "Source Book.pdf" tmp/pdfs/page

TESSDATA_PREFIX=conversion/common/tessdata tesseract \
  tmp/pdfs/page.png stdout -l eng --psm 3 \
  -c tessedit_create_hocr=1 -c hocr_font_info=1 \
  > tmp/pdfs/page.hocr
```

Then classify likely italic spans:

```bash
python3 conversion/common/detect_italics.py \
  tmp/pdfs/page.png tmp/pdfs/page.hocr \
  --output tmp/pdfs/page-italics.json
```

The detector shears each word crop over a range of angles and measures how
strongly its dark pixels align into vertical strokes. Roman words generally
peak near zero; right-slanted italic words peak at a positive correction.
`slant` and `gain` are retained so borderline cases can be reviewed.

This is evidence generation, not an unattended rewrite step. Inspect candidate
spans against the rendered page, resolve OCR/token alignment, then emit semantic
`<em>` markup and add regression assertions. Short italic words may need context;
the detector only infers them when both neighboring words on the same line are
already strong italic candidates.

## Whole-book batch recovery

Analyze every content page with resumable per-page output:

```bash
python3 conversion/common/batch_detect_italics.py \
  "Source Book.pdf" tmp/pdfs/source-book/italics \
  --first-page FIRST --last-page LAST --dpi 200 --workers 4 \
  --tesseract /path/to/tesseract \
  --tessdata conversion/common/tessdata
```

The batch runner deletes each temporary rendering and hOCR file after writing
its JSON evidence. Repeating the command skips completed pages.

Builders can call `mark_page_italics()` from `common/italic_markup.py` after
page-local text cleanup and before pages are concatenated. The aligner uses OCR
word order rather than a global vocabulary, so the same word can remain roman
in one sentence and become `<em>` in another. Replace the private-use markers
with markup only after HTML escaping, merge adjacent emphasis spans, and write
the returned statistics to a book-specific report under `tmp/`.

Audit the report for page coverage, weighted alignment, unmatched candidates,
and unusually low-alignment pages. Finally render the finished EPUB through a
real reader and compare isolated short emphasis, titles, long italic passages,
notes, and roman controls with the corresponding PDF pages.
