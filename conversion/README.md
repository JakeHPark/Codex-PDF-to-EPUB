# Conversion workflow and reusable tooling

Start with [AGENTS.md](../AGENTS.md): it defines source selection, mandatory
release gates and where to find detailed operating rules. This directory holds
book-independent methods; each book's reproducible recipe and evidence live
under `tmp/pdfs/<book>/`. The release runner orchestrates common checks and
book-specific validators; it does not replace extraction, source reconciliation
or actual proofreading.

## Documentation map

| Document | Purpose |
| --- | --- |
| [AGENTS.md](../AGENTS.md) | Operating contract, source/feature routing, release gates, output naming and maintenance policy. |
| This README | Pipeline ordering, source-specific execution and evidence handoffs. |
| [common/README.md](common/README.md) | Actual shared APIs, defaults, limitations, dependencies and test commands. |
| [guides/sources.md](guides/sources.md) | Authority, comparative editions, HTML/EPUB recovery, outlined text and academic papers. |
| [guides/ocr.md](guides/ocr.md) | Scan recovery, damaged text layers, conservative corrections and scholarly diacritics. |
| [guides/structure.md](guides/structure.md) | Boundaries, paragraphs, headings, dialogue, notes, indexes and references. |
| [guides/lists.md](guides/lists.md) | List identification, markers, nesting, continuations and image/column interruptions. |
| [guides/typography.md](guides/typography.md) | Font/pixel evidence, complete emphasis spans, quotations and punctuation. |
| [guides/illustrations.md](guides/illustrations.md) | Figures, tables, columns, sidebars, panels, masks, captions, spreads and crop QA. |
| [guides/mathematics.md](guides/mathematics.md) | Native mathematics, source outlines, failure inventory and visual release checks. |
| [guides/validation.md](guides/validation.md) | Cover, metadata, container, content, reader and visual verification. |

## Source-specific starting points

**Reliable digital PDF.** Inspect positioned spans and actual visible fonts.
Use embedded character/glyph evidence before OCR; `digital_pdf.py` can expose
special glyph semantics missed by size/baseline heuristics. Recover reading
order, notes and objects from geometry. Compare text and emphasis independently,
then inspect visible controls. Do not apply OCR spelling replacements to clean
text just because a shared normalizer exists.

**Scanned PDF.** Treat the hidden text layer as an imperfect transcription.
Inventory all pages and compare sparse or suspicious regions with rendered
images and independent OCR. Preserve word/line coordinates; recover missing
regions without replacing reliable text wholesale. Recover weight and slant
independently using calibrated pixel evidence where font metadata is absent.
Deskew text regions when necessary, preserving original illustration pixels.

**HTML or existing EPUB.** Verify complete coverage and edition first. Recover
semantic blocks, authored content and local assets while removing site or
converter material as appropriate. Inspect malformed loose text, auxiliary
spine items, inherited physical-page CSS and meaningful versus print-only
`br` elements. Avoid OCR spelling cleanup on clean structured text.

**Authority plus secondary transcription.** Inventory both and align passages
rather than relying on page numbers. Use the transcription to help recover
structure or obscured text only where the governing source supports it. Record
source-backed differences and unresolved readings. Check authority coverage
separately so a shared omission cannot pass.

These paths can coexist within one book. Selectable prose may sit beside an
outlined heading, a scanned plate, mathematical glyphs and a vector table.

## Pipeline and evidence handoffs

| Stage | Input → output | Required invariant |
| --- | --- | --- |
| Inspect | Original files → source/edition inventory and layout map | Physical page mapping verified; substantive content and deliberate omissions identified. |
| Recover | Source regions → positioned text, font/pixel evidence and original assets | Keep immutable source coordinates and provenance; do not infer completeness solely from selectable text. |
| Reconstruct | Independent streams → ordered complete blocks, lists, notes and object placements | One accounted role for each retained source fragment; headings and stream boundaries verified. |
| Correct and style | Complete blocks + reviewed decisions → corrected text and semantic spans | Narrow reproducible changes; OCR-only normalizer used only on OCR-derived prose; real compounds and mixed emphasis preserved. |
| Assemble | Blocks/assets → XHTML, navigation, note links, metadata and cover | No duplicate headings, remote assets, unresolved markers or stale derived captions/alternative text. |
| Audit again | Final structure → reviewed text/style/ownership findings | Reapply verified spans after transfers; resolve suspicious outliers and verify negative style boundaries. |
| Package and validate | EPUB → container/content/link reports and reader export | Checks consume the actual output path, not just working XHTML; all applicable AGENTS release gates pass. |
| Second pass and delivery | Complete packaged reading stream + reader preview + source → separate second-pass QA and final checksum | Mandatory fresh whole-book review after initial conversion/repairs; resolve findings, inspect special repairs, rerun final gates and report material limitations/editorial corrections. |

Keep a machine-readable or human-readable book QA record under its work directory.
Include the source edition, retained section/object inventories, correction
locations, check commands/results, reviewed exceptions, visual evidence, output
path and checksum. Existing books use different filenames and schemas; reuse a
suitable one rather than imposing an incompatible new format.

Run the shared packaged-text/style audit after assembly. For example:

```sh
python3 conversion/common/package_audit.py "output/epub/Title - Author.epub" \
  --report tmp/pdfs/book/package-audit.json \
  --phrases tmp/pdfs/book/reviewed-italic-phrases.json \
  --reviewed tmp/pdfs/book/reviewed-release-audits.json
```

For an initial inventory, omit the optional phrase/review files or add
`--inventory`; resolve defects and record source-supported exceptions before
running the release gate without that flag. Review records are JSON objects
with a `key` from the finding and a source location/reason. Phrase files contain
source-verified strings or objects with a `text` field. New or changed findings
must stop release. This audit supplements the independent source, container,
link, reader and visual checks; it does not replace them.

On rebuild, follow dependencies. A crop change can change text ownership; a
paragraph transfer can invalidate formatting; caption repairs can invalidate
alternative text; punctuation changes can invalidate note matching and reader
regressions. Regenerate affected evidence before final package/reader checks.
Never carry forward a successful report tied to an earlier output checksum.

## Release orchestration

For new books and substantive rebuilds, copy
[the configuration template](common/release.example.json) into the book's work
directory as `release.json`. Paths resolve from that file's directory; adapt all
example filenames and commands. List the authoritative sources and the recipe,
corrections and validation inputs that must remain unchanged during release.
Keep existing book-specific validators and add a small adapter for the runner's
[check report contract](common/README.md#release-runner).

1. Build the EPUB and complete the initial repairs.
2. Export the packaged EPUB with Calibre and perform the mandatory complete
   second pass. Inspect a reader-generated visual result against the source.
3. Store separate second-pass and visual-review records with the final EPUB hash,
   actual review scope/decisions and hashes of the evidence examined. Pending or
   unresolved reviews cannot pass. A command cannot substitute for these reviews.
4. Run the release runner. It checks the container and shared audit, regenerates
   Calibre text, invokes every configured validator and verifies the review records.
   If the fresh text differs from the reviewed export, review it again; do not
   merely update its hash. Resolve every failure, rebuilding when needed.
5. Verify the resulting receipt immediately before delivering the identical EPUB:

```sh
python3 conversion/common/release.py run tmp/pdfs/book/release.json
python3 conversion/common/release.py verify tmp/pdfs/book/release/release-report.json
```

All applicable gates in AGENTS.md must be represented. Only genuinely absent
body objects/layout can be marked not applicable, with a reason and reviewed
evidence; the cover and navigation still require checks. Failed runs replace
the old pass report. Receipts bind the EPUB, configuration, declared inputs,
review records, evidence, reader text, audit, command reports and logs by hash.
Changing any bound file invalidates the receipt. Use trusted configurations:
their command arrays execute programs on the local machine.

The runner verifies that checks ran and their evidence is current. It cannot
judge whether an adapter really reconciles the source or whether a recorded
visual review was thorough. Review those contracts and report limitations
honestly; never wrap an inventory-only report in a success receipt.

## Recover scan formatting with the shared tools

Use trustworthy evidence in this order: embedded source fonts/glyphs, verified
style-bearing OCR XML/hOCR, positioned scan pixels, then contextual overrides.
OCR metadata may identify slant reliably while getting weight wrong.

For one page, render and OCR the **same** image so boxes and pixels align:

```sh
mkdir -p tmp/pdfs/source-book/evidence
pdftoppm -f 12 -l 12 -r 150 -png -singlefile \
  "Source Book.pdf" tmp/pdfs/source-book/evidence/page-12
TESSDATA_PREFIX=conversion/common/tessdata tesseract \
  tmp/pdfs/source-book/evidence/page-12.png stdout -l eng --psm 3 \
  -c tessedit_create_hocr=1 -c hocr_font_info=1 \
  > tmp/pdfs/source-book/evidence/page-12.hocr
python3 conversion/common/detect_italics.py \
  tmp/pdfs/source-book/evidence/page-12.png \
  tmp/pdfs/source-book/evidence/page-12.hocr \
  --output tmp/pdfs/source-book/evidence/page-12-italics.json
```

The page number is an example. Use the correct source-page mapping and an
available compatible Python/Poppler/Tesseract installation; executable paths
vary by host. See [the helper catalog](common/README.md) for dependencies.

For a whole content range, resumable evidence can be produced with:

```sh
python3 conversion/common/batch_detect_italics.py \
  "Source Book.pdf" tmp/pdfs/source-book/italics \
  --first-page 10 --last-page 200 --dpi 200 --workers 4 \
  --pdftoppm /path/to/pdftoppm --tesseract /path/to/tesseract \
  --tessdata conversion/common/tessdata
```

Replace example ranges and executable paths. The runner caches per-page JSON
and removes temporary images/hOCR. Keep separately rendered review evidence as
needed. Invalidate caches when the source, page mapping or classifier changes;
resumability alone does not prove fresh evidence.

Call `mark_page_italics()` after page-local cleanup and before page concatenation.
Review coverage, weighted alignment and unmatched candidates, including rare
short words and roman controls. Its return contains private-use style markers:
escape prose, convert controlled markers to semantic markup, and reject any
markers left in the package. Final block/title boundaries still need review.
No classifier threshold is a universal justification to italicize a word.

## Verification commands and scope

Run shared tests when changing a helper or verifying its documented usage:

```sh
python3 -m unittest discover -s conversion/common -p 'test_*.py'
```

Run from the repository root with the dependencies in the helper catalog. This
checks shared code; **it does not validate any book**.

Each recipe must also run its own builder and validator, followed by a reader
export and complete-block/format checks. The generic reader step is:

```sh
ebook-convert "output/epub/Title - Author.epub" tmp/pdfs/source-book/reader.txt
```

Use that book's real paths and recipe order. Inspect reader-generated visual
output for repaired and representative layouts as required by AGENTS.md.
A text export cannot validate photographs, outlined equations or crop edges.

## Adding reusable methods

Promote only source-independent algorithms with a clear input/output contract,
conservative behavior and focused positive/negative tests. Document the actual
API and its limits in `common/README.md`. Put the general decision method in the
appropriate guide. Keep source-specific thresholds, names, crops, exact repairs,
fixtures and build/QA products in `tmp/pdfs/<book>/`.
