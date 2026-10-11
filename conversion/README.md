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
