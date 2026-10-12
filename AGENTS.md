# PDF-to-EPUB Conversion Guide

This is the project’s durable operating manual for converting scanned or digitally typeset books from PDF to EPUB. It is written for future Codex/AI instances as well as human editors.

The goal is not merely to produce an EPUB that opens. The goal is a readable, structurally correct ebook that preserves the book’s prose, chapter boundaries, notes, and hierarchy without reproducing artifacts of the printed page.

Update this guide whenever an error reveals a reusable lesson. Book-specific corrections should remain in that book’s build script, but the detection method and general rule belong here.

## Core principles

1. Treat PDF extraction as source recovery, not format conversion.
2. Never assume that one PDF page belongs wholly to one chapter.
3. Preserve semantic structure rather than page geometry.
4. Do not silently rewrite the author’s prose. Automated corrections must be narrow and explainable.
5. Validate the packaged EPUB and a reader-generated text export, not only intermediate XHTML.
6. Keep conversion recipes reproducible. A correction belongs in the builder, not only in a generated EPUB.
7. Prefer exact, verified repairs when a broad rule could alter legitimate text.
8. Generalize detection more aggressively than correction. A shared audit may
   flag an ambiguous mark across every book; rewriting it still requires
   layout evidence or an unambiguous structural rule.

## Recommended project layout

```text
project/
├── Source Book.pdf
├── AGENTS.md
├── conversion/
│   └── common/                 # reusable, book-independent tools
│       ├── detect_italics.py
│       └── tessdata/
├── tmp/
│   └── pdfs/
│       └── source-book/          # book-specific working material
│           ├── build_epub.py
│           ├── validate_epub.py
│           ├── corrections.json
│           └── extracted-pages/
└── output/
    └── epub/
        └── Source Book.epub
```

Keep general instructions and reusable, book-independent tools outside `tmp/`. In this project, book-specific builders, validators, OCR drivers, covers, regression assertions, formatting evidence, and extracted material belong under `tmp/pdfs/`; only the generalized method is intended to remain as durable repository guidance.

## Prefer a complete structured web edition when available

Before starting OCR, check whether the user has supplied—or an authoritative
source offers—a complete HTML edition. Prefer that structured text when its
chapter coverage and provenance can be verified. Record the source URL and
inventory every chapter before building so a partial web mirror is never
mistaken for the whole book.

Treat web editions as source recovery too: remove site navigation, headers,
footers, advertisements, and other chrome while preserving the book's semantic
markup, paragraph order, emphasis, quotations, and chapter hierarchy. Download
all book illustrations into the EPUB; never hotlink remote assets. Keep each
image at its original position in the reading order and wrap it in a semantic
`<figure>` with an adjacent `<figcaption>`. Prefer the source caption; if it is
absent, use a meaningful source-provided description such as `alt` text and
flag generic or missing descriptions for review rather than inventing facts.
Use responsive image CSS so illustrations fit the reading viewport without
distortion.

Validation for HTML-derived EPUBs must prove that every expected chapter was
included, every local image reference resolves and appears in the manifest,
no remote image URL remains, and every content image renders inline with its
caption in a representative reader export or preview.

## End-to-end workflow

### 1. Inspect the source

Before building anything:

- Run `pdfinfo` to determine page count, metadata, and whether the PDF contains text.
- Extract representative pages with `pdftotext -layout`.
- Render suspicious pages to images when text order, notes, headings, or bleed-through are ambiguous.
- Identify front matter, chapter openings, part dividers, notes, bibliography, and index.
- Record physical PDF page numbers separately from printed page numbers.

Do not infer every boundary from a table of contents. Locate the actual heading on the actual PDF page.

### 2. Make an explicit section map

Store each section as an identifier, title, inclusive PDF-page range, and hierarchy level. For example:

```python
SECTIONS = [
    ("chapter-one", "I. Chapter One", 10, 24, 1),
    ("chapter-two", "II. Chapter Two", 25, 39, 1),
]
```

Check every transition page visually or from layout-preserving text. A chapter can begin halfway through a PDF page. In that case, split at the heading rather than assigning the complete page to either neighboring chapter.

Treat page ranges as search bounds, not ownership boundaries. Extract each physical page once, locate every printed heading with an explicit book-specific pattern, then give the text before that heading to the preceding section and the text after it to the new section. Generate the EPUB heading separately and discard the matched printed heading. `conversion/common/section_boundaries.py` implements this shared-page rule and deliberately fails when an expected heading cannot be found; do not fall back to removing everything before the first blank line. That fallback silently strands sentence continuations and duplicates headings.

After changing one boundary, audit all later boundaries. A single mistaken offset often becomes progressive drift, causing each later chapter to lose its opening and inherit the next chapter’s heading.

### 3. Extract page text conservatively

For each page:

- Remove running heads and isolated printed page numbers.
- Remove form-feed characters.
- retain paragraph-separating blank lines;
- join discretionary hyphens only when the evidence supports it;
- preserve block quotations and deliberate section breaks;
- exclude blank divider pages and reverse-side bleed-through.

Printed typography can confuse extractors. Drop caps and letter-spaced small capitals may become forms such as `A p pa R e n t ly`. Verify these against the rendered page and repair them explicitly.

Some PDF text layers also leak invisible font-run delimiters as standalone characters. Confirm them against the page image before removing them. For example, an isolated `*` may be an internal italic-run marker rather than a printed ornament; genuine scene breaks usually have a distinct repeated or centered form that should be retained.

### 4. Reconstruct paragraphs across pages

PDF line endings are not paragraph endings. Within a paragraph, join wrapped lines with spaces. Across a page boundary, continue the paragraph when the preceding text does not end with terminal punctuation or when the next block clearly begins with a lowercase continuation.

Common failure:

```text
predictable or

mechanical
```

Correct result:

```text
predictable or mechanical
```

Do not apply lowercase-continuation logic blindly to poetry, lists, headings, equations, or intentionally fragmentary prose.

### 5. Normalize only defensible OCR errors

Use three levels of repair:

1. **General rule:** safe across ordinary prose, such as collapsing repeated whitespace.
2. **Narrow pattern:** safe for a constrained form, such as personal pronouns fused to `have` (`Ihave` → `I have`).
3. **Exact substitution:** required for irregular decorative typography or ambiguous OCR.

Keep exact substitutions visible in a dictionary or correction file. Avoid broad dictionary-based “spell correction”; it can damage names, quotations, dialect, archaic spelling, and technical language.

OCR may mistake an ampersand for the standalone token `8c`. In the verified
Blake quotation in *Life Is a Miracle*, `..., 8c is productive ...` should read
`..., & is productive ...`. Apply this only as a whole-token correction and
confirm it against the rendered source; `8c` can be meaningful in technical
contexts. The shared correction dictionary records this narrowly bounded token
repair for future OCR conversions.

Put mechanically safe, cross-book repairs in
`conversion/common/ocr_corrections.py` and make every OCR-based builder call
`apply_common_ocr_corrections`. Keep book-specific and ambiguous corrections
under `tmp/pdfs/<book>/`. Add a focused test for each shared rule, including a
negative example when the damaged token can occur inside a valid word. Apply
the shared normalizer after extraction and again after structural line/page
joining, because dehyphenation can create new fused tokens.

Do not run OCR spelling or quotation repairs on clean digital PDF or HTML
text merely for consistency. Preserve the source unless the extraction itself
introduces a demonstrated defect. Decode saved HTML explicitly as UTF-8 when
that is its recorded encoding; a fragment without a charset declaration must
not be left to a parser's legacy-encoding default. Check for mojibake in the
packaged text as well as in a reader preview.

Pay special attention to:

- fused words (`selfknowledge`, `Ihave`);
- fused short phrases (`ina` for `in a`), which should be repaired with
  case-preserving whole-word matches so substrings in names such as `Karenina`
  are not damaged;
- false hyphenation at line or page breaks;
- spaces around em dashes;
- zero/O and one/I confusion;
- missing punctuation at page boundaries;
- OCR fragments from illustrations or verso bleed-through;
- headers inserted into prose.

Font changes can damage adjacent text as well as formatting. A PDF may render `*Complete Writings*, Oxford` correctly while its embedded text says `Complete WritingsOxford`: the comma and space disappeared exactly where italic and roman runs meet. Word-only italic alignment cannot restore characters that are absent from the text layer. Compare aligned OCR tokens and geometry with the embedded text; when one embedded token equals two or more consecutive OCR words, split it at the OCR word boundaries and restore only OCR-observed edge punctuation and spacing. Likewise, repair an empty separator between two otherwise aligned words from OCR evidence. `conversion/common/italic_markup.py` performs these constrained repairs before adding emphasis markers and reports the number applied.

Audit citations as a separate corpus after ordinary prose cleanup. Search packaged XHTML for implausible years (`1.999`), letter-for-digit dates (`April l` or `April i`), split publication words (`Re view`), malformed page labels, missing spaces after closing emphasis or commas, and titles whose `<em>` span stops midway. OCR is useful evidence, but do not replace whole citations blindly: it may fuse punctuation-heavy strings such as `1,1999,p.5;and`. Render every flagged citation, apply contextual corrections for ambiguous digits, and add the corrected full citation plus the malformed signatures to regression tests.

### 6. Generate semantic EPUB XHTML

Each navigable section should normally have:

- one generated `<h1>`;
- body paragraphs as `<p>`;
- quotations as `<blockquote>`;
- deliberate scene breaks as a semantic or styled divider;
- stable identifiers for notes and links.

Do not flatten dramatic dialogue into prose. When consecutive OCR lines begin
with speaker labels such as `FRIAR:` and `ROMEO:`, preserve each speech as a
separate paragraph inside a quotation/dialogue block. Preserve verse lineation
with semantic block structure or explicit line breaks where the source makes
it meaningful, and add a regression check against the collapsed speaker
sequence.

A single printed dramatic extract may be split into several OCR blocks by
blank lines between speeches. Group all contiguous speeches into one
`blockquote`; do not indent only the middle fragment. Every speech paragraph
must share the same block-level left edge, while `<br/>` may preserve verse
lines within a speech.

If the builder generates a chapter heading from the section map, remove the extracted printed heading from the body. Otherwise readers see a duplicated heading.

Part-title pages should contain the part heading only. Do not retain OCR from blank facing pages, ornamental backgrounds, or show-through text.

### Mixed text, tables, graphs, and diagrams

Inventory every numbered figure and table, every embedded image, and every
continued panel before assembly. Image extraction alone misses tables drawn
with text and ruling lines, vector diagrams, and labels placed over images.
Record each object's source page, bounding rectangle, caption, and reading-order
position. Account for rotated landscape pages and multipage continuations.

Use semantic HTML tables where row/column associations and merged headers can
be reconstructed and checked against the source. For complex statistical tables
or diagrams, a verified high-resolution crop is preferable to guessing cells or
flattening columns into prose. Preserve the entire object, including units,
legends, significance keys, and table notes. Keep a readable caption adjacent
to each responsive inline image; do not hotlink assets. Retain enough resolution
to enlarge dense panels. Document when tables remain images rather than
searchable, accessible HTML tables.

Exclude each captured object's text from the prose stream, but do not discard
ordinary text above or below it. A floating table or figure may interrupt a
sentence at a physical page break. Reconstruct the interrupted paragraph before
placing the float at the next safe paragraph boundary; do not force the reader
to resume mid-sentence in a new paragraph after a picture. Keep continued table
panels adjacent and label them as continuations, not as new tables.

For table crops, detect and keep every wrapped caption line as caption text,
even when the PDF changes fonts after the bold table number. Start the image at
the first table header/data row (or its top rule), never at a caption
continuation. End the image before the next numbered subsection heading and
its prose; heading fonts may be the same size as table text, so use both font
and heading structure. Place the extracted heading and opening prose after the
table in reading order. Compare the caption, crop top/bottom, and neighboring
text against the rendered PDF page to catch caption fragments and section text
leaking across those boundaries.

Validate object coverage against the inventory, inspect every crop edge for
clipped labels or leaked prose, and check representative narrow and wide objects
in a reader preview. Compare the retained prose separately from captured object
text, so a completeness check cannot quietly excuse missing text as graphics.

### Preserve substantive front matter

Do not apply a blanket "remove front matter" rule to a whole book. An earlier
general instruction to remove front matter applies only to generic publisher
material; this specific preservation rule takes precedence for authored sections.
Omit publisher advertisements, series lists, copyright/imprint pages, and blank
leaves when they are not part of the reading experience. Preserve authored
forewords, prefaces, introductions, prologues, and other substantive opening
sections, and put them in the book's original reading order before the main
chapters. Distinguish a standalone introduction in the preliminary pages from
a numbered Introduction that is already a main chapter; include both when the
source contains both. Check the contents page and the PDF pages themselves
before setting the extraction start page. Record explicitly which preliminary
sections were retained and which publisher matter was omitted.

### 7. Handle footnotes explicitly

Never leave a printed footnote embedded between ordinary prose paragraphs.

Detect note markers and note text while page structure is still available. Associate each note with its chapter and render it in a predictable location. Chapter-end notes are acceptable when page-local placement cannot be represented reliably.

Reader support for semantic popup footnotes is inconsistent. If notes must always be visible, render them as ordinary block content, for example:

```html
<section class="footnotes">
  <h2>Footnotes</h2>
  <div class="footnote" id="fn-chapter-1">
    <span class="footnote-number">1.</span>
    <p>Note text…</p>
  </div>
</section>
```

CSS should explicitly keep the note section and note blocks visible. Source asterisks used only as print markers should not remain in the prose after the note has been structurally separated.

### 8. Package correctly

An EPUB is a ZIP container with strict requirements:

- `mimetype` must be the first member;
- `mimetype` must be stored without compression;
- `META-INF/container.xml` must point to the package document;
- every manifest and spine reference must resolve;
- XHTML and XML must be well formed;
- navigation entries must match real sections;
- metadata, language, cover, and reading order must be present.

### 9. Validate at three levels

#### Container validation

Verify ZIP integrity, member order, compression rules, manifest references, spine references, XML parsing, and navigation targets.

#### Structural and textual assertions

Add regression assertions for every confirmed error. Examples:

```python
assert "predictable or mechanical" in text
assert "predictable or</p>\n<p>mechanical" not in text
assert "<p>7. Progress Without Subtraction</p>" not in text
assert "Apparently everywhere" in text
```

Also scan for suspicious paragraph boundaries where a paragraph ends without terminal punctuation and the next begins in lowercase.

#### Reader-level round trip

Use Calibre’s `ebook-convert` to export the finished EPUB to plain text. Search that export for:

- corrected phrases;
- duplicated headings;
- missing chapter openings;
- stray note markers;
- gibberish signatures;
- unexpected hyphenation;
- text that exists in XHTML but disappears in a reader conversion.

The packaged EPUB—not the build directory—is the artifact that must pass.

### 10. Perform visual spot checks

At minimum, inspect:

- cover and title page;
- table of contents;
- first paragraph of every chapter and part;
- pages surrounding every source boundary;
- all footnote sections;
- block quotations and section breaks;
- bibliography and index samples;
- any page whose extraction required a special repair.

## Correction-driven maintenance

When a reader reports an error:

1. Find the exact text in the packaged EPUB, unpacked XHTML, extracted page text, and source PDF.
2. Determine whether the defect comes from extraction, page assignment, paragraph reconstruction, normalization, XHTML generation, CSS, or reader behavior.
3. Decide whether the fix is general, narrowly patterned, or exact.
4. Put the fix in the reproducible builder.
5. Add a regression assertion when practical.
6. Rebuild the entire EPUB.
7. Run container validation, structural QA, and a reader-level round trip.
8. Update this guide if the error teaches a reusable lesson.

## Lessons established in this project

### False paragraph breaks

Page and OCR block boundaries can split a sentence even when the prose is continuous. Merge verified lowercase continuations and test the packaged result.

### Em-dash spacing

Extraction can introduce spaces adjacent to an em dash. Normalize verified prose forms consistently, while taking care around deliberately spaced display text.

### Footnote extraction

Print footnotes may be inserted into the main flow by PDF extraction. Separate them structurally, remove obsolete print markers, and force visible rendering when popup-note behavior is unreliable.

### Front matter

Omit generic front matter by default when converting a scanned book. Title, copyright, dedication, and other preliminary pages disproportionately contain decorative typography, sparse layouts, and bleed-through that OCR turns into broken text. Keep the cover, but begin the EPUB navigation and reading order at the first substantive section. Remove any generated front-matter document from the manifest, spine, and navigation as well as from the visible contents.

Retain front matter only when the user explicitly requests it or when a preliminary section contains substantively necessary material. In that case, visually verify every retained page and give it the same structural and formatting review as the main text; do not pass raw preliminary-page OCR through merely for completeness.

### Bleed-through and divider pages

OCR can turn faint reverse-side printing or decorative pages into convincing-looking gibberish. A mostly blank page is not necessarily usable text. Compare suspicious output with a page image and exclude it when appropriate.

Do not wait for a reader to find these pages. Before packaging, rank every included OCR page by word count, mean alphabetic-token length, and the proportion of one- or two-letter tokens. Render the outliers, especially pages at chapter ends and before part dividers. Maintain a book-specific set of visually verified blank/bleed-through pages and exclude them before paragraph assembly; never add their gibberish to a cleanup dictionary. Add distinctive OCR fragments from every excluded page to regression tests so a later range change cannot reintroduce them.

### Decorative initials

Large, spaced, or mixed-case opening letters may be extracted as multiple fragments. These irregular forms require source-verified substitutions rather than a broad whitespace rule.

### Generated versus extracted headings

If a chapter title is generated from metadata, strip the printed title from extracted body text. Check that it appears exactly once in a reader export.

Printed headings may consist of several blank-line-delimited display blocks,
such as a large main title followed by an italic subtitle. Do not remove only
the first block. Normalize the words of each consecutive opening block and
remove every block whose words are still accounted for by the generated title;
stop at the first block containing words outside that title. This preserves the
opening prose while preventing a subtitle from surviving as a duplicate body
paragraph. `conversion/common/section_boundaries.py` implements this rule.

### Cascading section-boundary drift

An incorrect start page can place a new chapter’s heading and opening paragraph at the end of the previous EPUB section, while the new section begins in mid-sentence or mid-word. Audit all downstream boundaries whenever one such error is found.

### Invisible notes

Semantically marked EPUB footnotes may be hidden or treated as popups by some readers. For notes that must remain visibly readable, use normal block elements with explicit CSS and retain semantic relationships only where reader behavior has been tested.

### Repeated quotation marks

OCR may duplicate a closing quotation mark, but repeated quote characters can also arise near nested quotations. Do not collapse every doubled quote globally. Verify the source and use an exact or tightly contextual repair, then add a regression assertion for the corrected phrase.

OCR may also mismatch quotation styles, such as a single opening mark paired with a double closing mark. Compare the phrase with the rendered source page before normalizing it; apostrophes and genuinely nested quotations make global quote substitution unsafe.

Run a stack-based typographic-quotation audit over every page before packaging.
Treat curly opening and closing marks structurally, ignore a right single mark
as an apostrophe only when it follows a word and no single quotation is open,
and flag mismatched or unclosed marks for page-image review. This distinguishes
valid nesting such as `“He called it ‘no,’”` from corrupt forms such as
`“co-act,’”` and `“all the world loves a lover,’”’` without globally replacing
quote clusters. `conversion/common/epub_quality.py` implements this audit.

Write ambiguous quotation findings to a book-specific review report under
`tmp/`. The report should be regenerated during validation and used to drive
rendered-page review; it is not itself permission to rewrite every flagged
mark. Switch the audit to release-blocking only after the report has been
reviewed or reduced to explicitly documented exceptions.

Normalize adjacent identical curly singles—`‘‘` to `“` and `’’` to `”`—in the
shared OCR layer. They are a common extraction of one printed double quote and
cannot be valid nested English typography, since nested quotation levels
alternate styles. Do not extend this into a general single-to-double quote
replacement; isolated marks still require stack context or page-image review.

A primary double quotation ending with the OCR cluster `,’”` or `,’”’` may be
normalized structurally when the quoted span contains no nested single opener:
retain the punctuation and one closing double quote. This fixes the pattern,
not a memorized phrase, while preserving a valid nested form such as
`“He called it ‘no,’”`.

### Apostrophes versus quotation marks

Do not infer punctuation from glyph shape alone. ASCII `'`, left and right
curly singles, and tiny raised note digits can collapse to the same OCR token.
An ASCII apostrophe is not automatically an endnote marker, and a curly right
single is not automatically legitimate punctuation. Classify each occurrence
from its role: internal contractions and possessives are apostrophes; balanced
single marks may delimit a nested quotation; a lone mark at the beginning of a
quotation that later closes with `”` may be a damaged double opener; and a
sentence-final mark above the baseline may be a numeric note reference.

Use a quotation-stack audit and sentence context to find candidates, then use
the rendered page and word geometry to decide ambiguous cases. Never globally
replace bare apostrophes with opening double quotes, never globally delete
apostrophes after punctuation, and never curl every ASCII apostrophe without
checking whether it is a quote delimiter or a note marker. Preserve reviewed
decisions in book-specific evidence, but keep this classification procedure and
its regression checks in the shared workflow.

### Stranded footnote-marker punctuation

Superscript note symbols may be OCRed as punctuation such as `!`, or as a combination such as `*!`. If later cleanup removes only the asterisk, it can leave a bizarre sentence ending such as `.!`. Confirm the source marker and preserve its note text, then remove the entire body marker before general punctuation cleanup. Scan the packaged EPUB for the stranded signature as a regression check.

Numeric endnotes can also be OCRed as an ASCII or curly apostrophe, with or without an asterisk: `denaturing.'*`, `attached.’`, and genuine closing quotation marks can all look deceptively similar in plain text. Textual shape alone must never decide whether such a mark is punctuation or a note. Before stripping symbols, inventory every sentence-final apostrophe-like candidate across the whole body. For each candidate, use its stored word box and baseline position, render a high-resolution crop, run digit-only OCR at several crop widths, and reconcile the result with the chapter's monotonic note sequence and the corresponding notes entry. Record every reviewed decision under the book-specific `tmp/` material, including whether a genuine closing quotation mark must remain. Support multiple recovered markers on one page without relying on the page number as a unique key.

Convert confirmed markers to the same semantic linked-superscript form as other numeric notes. Treat unconfirmed marks as punctuation candidates and resolve them from the rendered source and sentence context; do not globally delete ASCII or curly apostrophes after full stops. Add packaged-XHTML checks for all reviewed cases, for leaked raw marker clusters, for every note target, and for the expected whole-book reference count.

### Superscript numeric endnotes misread as symbols

Raised endnote digits can be OCRed as ordinary symbols such as `®`, `°`, or `©`. Finding even one is a whole-book audit trigger, not permission to patch only the reported sentence. Inventory every occurrence of those glyphs in body XHTML and in the page-level OCR, excluding verified legitimate uses such as a copyright notice in front matter.

Do not globally translate any one symbol into a digit: the same glyph may be legitimate elsewhere, and different raised digits can collapse to similar OCR output. Recover each occurrence from layout evidence. Re-render the affected page at high resolution, use the stored word bounding box to crop the right edge of the token, run digit-only OCR over several crop widths, and check the candidate against the monotonically increasing note sequence and the corresponding entry in the notes section. Crops that are too wide can absorb the word's final letter and invent a leading `1`, so retain the votes and the reviewed selection as book-specific evidence under `tmp/`.

Remove the entire OCR marker cluster, including false leading digits, quote shapes, asterisks, or question marks, while preserving genuine sentence punctuation and verified closing quotation marks. Represent the restored marker semantically as a linked superscript, for example `<a epub:type="noteref" href="notes.xhtml#note-id"><sup>9</sup></a>`, with a stable destination in the visible notes chapter. Validate every fragment target in packaged XHTML and confirm that reader text export retains the digit.

Make this release-blocking: all packaged XHTML—not only the main body—must contain zero unresolved `°`, `®`, or `©` marker glyphs (apart from individually verified legitimate uses), zero leaked internal placeholders, and the expected number of recovered `<sup>` references. Also inspect reader-exported text, because page-bottom bleed-through in the notes can be joined to a valid note on the following page and evade body-only checks. When a glyph class is discovered late, rebuild and rerun the check across the entire book rather than adding a single contextual exception.

### Running-head variants absorbed into prose

Running heads may be extracted at a physical page boundary and then joined into a continuing paragraph. Recognizers must tolerate folio variants such as `405` and `407.`, typographic apostrophe variants, and every running title actually used by the book. After conversion, scan body chapters (excluding the contents, notes, and index) for a page number followed by a known running title. When one failure is found, audit all chapters because the same incomplete header rule usually affects many pages.

### Formatting recovery from scanned books

For digitally typeset PDFs, first inspect embedded font glyphs as well as font
names, sizes, and baselines. Some fonts encode small capitals and superscript
digits as glyph variants (`N.sc`, `one.super`) while the text map returns an
ordinary lowercase letter or digit at the ordinary body size and baseline.
Size-based superscript detection misses these. `conversion/common/digital_pdf.py`
maps CFF glyph names from PyMuPDF's text trace back to positioned characters.
Use verified `.sc` variants for semantic small-cap spans and `.super` variants
for superscripts; reconcile numeric references with the complete notes sequence
and validate every forward and return link. Not every font exposes these names:
absence of a recognized glyph suffix is not proof of absent formatting.

Retain line coordinates until paragraphs and quotations have been reconstructed.
A single indented first line usually begins an ordinary paragraph; a sustained
inset across consecutive lines denotes a block quotation or list. Determine
the block first, then detect paragraph indents relative to that block's left
edge. Otherwise every quotation line becomes a separate paragraph and keeps
its broken hyphenation. Reconstruct multicolumn indexes column by column, not
by globally sorting all lines by their vertical position.

For digital sources, compare the complete retained character stream and italic
character stream with the packaged output, allowing only the explicitly
documented whitespace/dehyphenation transformations. Inspect all unusually
short paragraphs and any paragraph ending with a hyphen. Exact character
coverage does not prove correct paragraph grouping, so retain both checks.

Plain OCR normally discards italics, boldface, small capitals, and other inline styles. First inspect whether the PDF text layer, hOCR, or ABBYY XML contains reliable style metadata. If it does, convert those spans into semantic EPUB markup such as `<em>` and `<strong>`. If the available OCR assigns generic or meaningless fonts, do not infer formatting globally from capitalization or vocabulary.

For style-poor scans, maintain source-verified emphasis terms and contextual corrections. A short common word such as *the* must never be added to a global emphasis list: store the complete surrounding phrase and emphasize only the verified occurrence. Escape the prose first and then insert controlled semantic tags so OCR text cannot become arbitrary HTML. Prefer `<em>` over visual-only `<i>`, add regression assertions against the packaged XHTML, and expand the verified evidence as pages are reviewed. This recovers meaningful formatting incrementally without italicizing ordinary uses of ambiguous words.

This project also includes `conversion/common/detect_italics.py`, which uses hOCR word boxes aligned to rendered pixels. For each word it tests a range of horizontal shear corrections and measures how strongly dark pixels align into vertical strokes. Right-slanted italic words typically show a positive best slant and a meaningful improvement over the zero-slant score. Use its JSON output to prioritize and document review; do not apply its candidates blindly. Exclude running heads and marginal furniture, correct OCR tokens, join adjacent candidates into spans, and store approved results with the book-specific material under `tmp/`.

Run formatting recovery across every content page, not merely a representative sample. `conversion/common/batch_detect_italics.py` renders and analyzes pages independently, caches one compact JSON record per page, and deletes temporary images and hOCR. `conversion/common/italic_markup.py` aligns those page-level word records with the builder’s extracted page text, inserts occurrence-level emphasis markers, and reports alignment and application counts. This preserves the distinction between an italic occurrence and a roman occurrence of the same word.

Short words require a stricter classifier, not a global exception. The current detector uses the ordinary slant/gain threshold for words of four or more letters and substantially higher thresholds for two- or three-letter words. A short word inside a consistently italic run can also inherit the run classification. Retain exact contextual overrides only when image evidence cannot classify an isolated occurrence; do not use them as a substitute for the whole-book pass.

After application, require complete evidence-page coverage, high weighted token alignment, no leaked private-use markers, semantic `<em>` markup in packaged XHTML, and reader-rendered spot checks covering isolated emphasis, multiword titles, long italic passages, notes, and nearby roman controls. Running heads may be detected in the page image, but they should remain unmatched because the builder removes them before formatting alignment.

Marginal section numbers and ornamental boxes may be inserted into the first prose line by OCR. Remove them using a layout-specific pattern that requires the ornamental delimiter; do not delete ordinary Roman numerals appearing in prose.

### Durable tools versus temporary products

Do not leave reusable, book-independent algorithms or the general instruction manual in `tmp/`. Keep book-specific builders, validators, corrections, covers, fixtures, raw OCR, hOCR, unpacked EPUB trees, reader exports, caches, and exploratory measurements in `tmp/`. A useful technique discovered there should be generalized and documented here; only genuinely reusable code should be promoted to `conversion/common/`.

The reusable portion of endnote repair belongs in
`conversion/common/endnote_recovery.py`; only the reviewed glyph decisions and
source-specific closing punctuation belong under `tmp/`. Use
`conversion/common/page_reconstruction.py` before joining physical pages so a
detached marginal fragment cannot be absorbed into the next heading. Run
`conversion/common/epub_quality.py` against the final container to enforce
front-matter policy, marker cleanliness, note counts, and fragment targets.

## Completion checklist

- [ ] Every chapter and part starts on the correct source page.
- [ ] Every generated heading appears once in body reading order.
- [ ] No chapter starts in the middle of a word or sentence.
- [ ] No next-chapter heading remains at the end of the preceding section.
- [ ] No running heads or page numbers appear in prose.
- [ ] No known bleed-through gibberish remains.
- [ ] Paragraphs flow correctly across page boundaries.
- [ ] Verified discretionary hyphens are removed; real compounds remain hyphenated.
- [ ] Footnotes are separated from prose, numbered, and visible.
- [ ] Navigation and spine order match the book.
- [ ] Container and XML validation pass.
- [ ] Regression assertions pass.
- [ ] Calibre round-trip checks pass.
- [ ] Representative pages have been visually reviewed.

## Policy for future updates

Continue accepting reader corrections. Each time:

- repair the affected EPUB;
- look for the same defect throughout that book;
- inspect whether the defect exposes a broader process failure;
- add a narrow automated check or correction where safe;
- record the generalized lesson here without cluttering the guide with every isolated typo.
