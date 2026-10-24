# PDF-to-EPUB operating manual

Produce a readable, source-faithful ebook with correct reading order, structure,
notes, typography and illustrations. An EPUB that merely opens is incomplete.
Treat extraction as source recovery. Keep every correction reproducible.

## Start here

1. Read this file and [the tooling workflow](conversion/README.md).
2. Identify the authoritative edition and source type using the table below.
3. Read the applicable detailed guides **before** implementing that stage.
4. Use the [release gates](#release-gates) on every conversion or rebuild.
   Read [validation details](conversion/guides/validation.md) before release.

The guides are part of this manual. Their separation reduces unrelated reading;
it does not make applicable instructions optional. Existing book recipes vary:
verify which checks they actually run rather than assuming a previous builder
already enforces the current manual. No single helper runs the whole workflow.

## Non-negotiable rules

- Preserve the governing source's prose, edition, translation and hierarchy.
  A cleaner transcription is evidence, not automatically the authority.
- Never assume one physical PDF page belongs to one chapter or one text stream.
- Preserve semantic structure rather than print geometry. Keep physical page
  numbers separate from printed folios and reflowed reader pagination.
- Preserve authored prefaces, introductions, forewords, acknowledgments and
  other substantive front matter. Omit generic advertisements, imprint matter
  and blank leaves unless needed or requested; record omissions individually.
- Do not silently rewrite prose. Confirm obvious source typos in context, repair
  them narrowly, record the source location and report editorial corrections.
  Preserve ambiguous wording, dialect, names and intentional notation.
- Generalize detection more aggressively than correction. A suspicious mark
  triggers review; it does not authorize a global replacement.
- Put a correction in the builder, never only in the generated EPUB. Keep
  source evidence, reviewed exceptions and regression assertions with the book.
- Validate the final package and a reader-generated export. Text coverage,
  structure, emphasis and image correctness need separate evidence.
- A reported defect triggers a whole-book search for the same failure class.
  Rebuild and revalidate after repair; do not patch only the example.

## Choose the source workflow

Classify by what the PDF actually contains, not its filename or selectable-text
status. A book can require several routes on different pages.

| Source or condition | Required approach | Detailed rules |
| --- | --- | --- |
| Complete authoritative HTML edition | Verify edition and every chapter; recover semantic markup and local illustrations; remove website chrome. | [Sources](conversion/guides/sources.md) |
| Existing EPUB or cleaned transcription plus an authority | Inventory both; align passages; retain only source-supported text and typography; rebuild damaged package/navigation as needed. | [Sources](conversion/guides/sources.md) |
| Reliable digitally typeset PDF | Use positioned characters, fonts, glyphs and baselines; compare retained text and emphasis; inspect tables, scripts and reading order. Do not run OCR spelling cleanup merely for consistency. | [Structure](conversion/guides/structure.md), [Typography](conversion/guides/typography.md) |
| Scan with an OCR text layer | Compare selectable text with rendered pages and independent OCR. Recover missing regions and typography from the image; retain coordinates. | [OCR](conversion/guides/ocr.md), [Typography](conversion/guides/typography.md) |
| Scan without usable text | OCR positioned regions; recover columns, independent streams and formatting; verify against pixels. | [OCR](conversion/guides/ocr.md), [Structure](conversion/guides/structure.md), [Typography](conversion/guides/typography.md) |
| Selectable PDF made from a damaged transcription | Distinguish corruption already visible in the source from new extraction errors. Use a matching original scan when available. | [Sources](conversion/guides/sources.md), [OCR](conversion/guides/ocr.md) |
| Outlined, image-only or designed text region | A blank extraction does not prove a blank page. Recover outlined prose by reviewed OCR; preserve designed pages as images when their arrangement is substantive. | [Sources](conversion/guides/sources.md#outlined-text-in-pdfs), [Illustrations](conversion/guides/illustrations.md) |

Before fresh OCR, check whether a complete, suitable structured edition exists.
Do not substitute another edition or translation merely because it is easier.

## Load rules for the book's features

| Feature or observed failure | Read before handling it |
| --- | --- |
| Chapter/part boundaries, paragraphs, dialogue, lists, notes, indexes, print references or keeping a source-page dedication together | [Structure](conversion/guides/structure.md) |
| Italics, bold, small capitals, fragmented styles, quotations, apostrophes, dashes or punctuation spacing | [Typography](conversion/guides/typography.md) |
| Columns, floating figures, tables, exercise plates, marginal notes, shaded panels, captions, image crops, spreads, decorative ornaments or drop caps | [Illustrations and layout](conversion/guides/illustrations.md) |
| Equations, scripts, fractions, stacked coefficients, overlaid operators or equation images | [Mathematics](conversion/guides/mathematics.md), including its failure inventory |
| Pāli, legacy transliteration fonts, detached accents or other scholarly diacritics | [OCR: transliterations](conversion/guides/ocr.md#pāli-and-other-scholarly-transliterations), plus typography rules |
| Academic papers, abstracts, positioned tables or figures | [Sources: academic papers](conversion/guides/sources.md#academic-papers-and-positioned-objects), plus applicable object/math rules |
| Cover, metadata, packaging, corrupt archives, reader checks or final review | [Validation](conversion/guides/validation.md) |

## Required order of work

1. **Inspect and inventory.** Determine page count, edition, text reliability,
   layouts and typefaces. Inspect representative and suspicious rendered pages.
   Inventory retained sections, notes, figures, tables, equations and omissions.
2. **Map ownership and boundaries.** Record physical pages and source regions.
   Split shared pages at verified headings. Identify body, notes, captions,
   sidebars and graphics as independent streams before ordering text.
3. **Recover text and style evidence.** Preserve original coordinates separately
   from joined text. Use trustworthy embedded fonts first; use independent OCR
   and calibrated pixel evidence where needed. Store ambiguous decisions.
4. **Reconstruct complete semantic blocks.** Join physical lines within prose,
   quotation paragraphs and list items; preserve real verse and dialogue breaks.
   Recover whole lists and continued panels. Place floats at safe boundaries.
5. **Apply reviewed corrections and formatting.** For OCR-derived text, call
   `apply_common_ocr_corrections` after extraction and again after joining.
   Recover complete emphasis spans after structural transfers; preserve genuine
   mixed styles. Apply prose typography across inline markup without losing links.
6. **Assemble and package.** Generate headings once, semantic XHTML, navigation,
   visible linked notes, local responsive assets and at least a minimal cover image.
7. **Perform a fresh whole-book second pass before delivery.** This is mandatory;
   do not wait for the user to request another proofread. After the first complete
   conversion and its repairs, review the entire packaged reading stream again,
   including preliminaries, notes and every chapter. Recheck OCR/spelling
   candidates, paragraph joins, lists, quotations, punctuation, repetitions,
   notation and emphasis in context. Check roman surroundings as well as styled
   words, and complete structures rather than repaired examples alone. Resolve
   findings against the source, repair the recipe and inspect the rebuilt reader
   result. Record the second pass separately in QA; reusing the first inventory,
   checking only reported defects or merely opening the EPUB does not count.
8. **Run every applicable release gate below on the final artifact.** After any
   change, rerun affected source/style/object checks, rebuild, then rerun package
   validation and reader export. A stale successful report is not evidence.

## Release gates

Keep a book-specific QA record with the output filename/checksum, checks run,
results, reviewed exceptions and remaining limitations. Mark a feature genuinely
absent as not applicable with a reason. Generating a candidate report is not the
same as resolving its findings. Do not claim a pass for an unperformed check.

| Gate | Required evidence |
| --- | --- |
| Edition and coverage | Every retained chapter/part/preliminary section and its actual opening accounted for; correct order; documented omissions; no unexplained excluded source text. |
| Text and structure | Retained source stream reconciled after documented changes; no duplicated headings, running heads, leaked folios or bleed-through; complete paragraphs, lists and notes in verified order. Character counts alone cannot pass this gate. |
| Textual sanity | Review period-word spacing, fused/split words, false hyphens, digit/letter confusion, unexpected capitals/scripts/symbols, punctuation clusters, unmatched brackets, repetitions and stranded fragments across the whole packaged text. Apply language-aware rules. |
| Whole-book second pass | Separate post-conversion proofreading record covering the complete packaged reading stream, with checks run, source-reviewed decisions, resulting repairs and final reader verification. No unresolved findings or unperformed checks represented as a pass. |
| Typography | Typographic prose quotes/apostrophes actually applied; measurements and notation classified separately; nested and continued quotations preserved. No unexplained partial-word styling, fragmented titles, short style outliers or style leaks. Test both emphasized and roman boundaries. |
| Objects and layout | Source inventory reconciled with packaged figures/tables/formulas; every crop edge and association reviewed; captions and derived alternative text agree; no duplicate prose inside assets; native quality and spread relationships verified where applicable. |
| Notes and links | Expected entries and reference occurrences checked separately, including repeated references; all forward/back/fragment targets resolve; notes remain readable. A count alone cannot prove correct note order or association. |
| Container and metadata | ZIP integrity; `mimetype` first and uncompressed; XML/XHTML well formed; manifest/spine/navigation/asset references resolve; title, author, language and cover correct; no source filenames, local paths or internal placeholders leaked. |
| Reader export | Export the **packaged EPUB** with Calibre; verify complete retained blocks and corrected contexts, headings, notes and list values. Check spaces and punctuation as well as alphanumeric coverage. |
| Visual review | Inspect cover, navigation, all section openings/transitions, note sections and representative quotations/lists/styles; inspect every special repair and applicable image/math cases against the source at usable reader sizes. Text export cannot prove graphical interiors. |
| Reproducibility and delivery | Repairs and exceptions live in the recipe; regressions pass against final output; QA evidence matches its checksum; deliver the actual rebuilt EPUB and report material limitations or source editorial corrections. |

Use shared detectors from [the helper catalog](conversion/common/README.md),
plus book-specific checks. Run the shared packaged-text/style audit as a release
gate: every finding must be repaired or individually source-reviewed; an
inventory-only report is not a pass. Know their limits: the curly-quote audit
does not flag ordinary ASCII quotes; a word-only comparison ignores punctuation; image
counts do not prove crop completeness; font metadata does not prove visible
formatting. Add explicit checks for those gaps.

## Files and output names

```text
AGENTS.md                       # operating contract and routing
conversion/README.md             # engineering workflow
conversion/guides/              # detailed general rules, grouped by topic
conversion/common/              # book-independent code and focused tests
input/                          # supplied source material; preserve originals
tmp/pdfs/<book>/                # recipe, corrections, validators, evidence,
                                # covers, extraction, caches and reader QA
output/epub/                    # final deliverables
```

Book-specific builders, fixtures, OCR drivers, thresholds, covers and overrides
belong under `tmp/pdfs/<book>/`. Only genuinely book-independent algorithms and
tests belong in `conversion/common/`. General instructions must remain outside
`tmp/`; promote methods rather than a book's particular spelling corrections.
The diagram is a layout convention, not a requirement to relocate user files.

Name output `Title - Author.epub` by default. For two authors use
`Title - Author, Author.epub`; for three or more use
`Title - First Author et al.epub`. Keep credited names and order; do not invent
abbreviations. Replace only filename-unsafe characters. Use the identical path
in builder, validator and delivery link. An explicit user filename overrides this.

## Correction and documentation maintenance

For every reader report, find the defect in the package and source, identify
its cause, audit that failure class throughout the book, repair the recipe,
add positive and negative regressions where useful, rebuild, validate and inspect
the reader result. Update the relevant topical guide when there is a reusable
lesson. Safe shared repairs require constrained matching and focused tests,
including valid lookalikes; ambiguous repairs remain book-specific.

Keep one authoritative rule per topic. Extend its section rather than appending
a chronological lesson at the end of this file. Put policy and release gates
here, source/feature procedures in `conversion/guides/`, orchestration in
`conversion/README.md`, and actual APIs, defaults, tests and limitations in
`conversion/common/README.md`. Reconcile obsolete or conflicting rules when
updating; do not let an old blanket omission or automatic-correction rule
survive beside its narrower replacement.
