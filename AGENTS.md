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

### EPUB output filenames

By default, name the final EPUB `Title - Author.epub`. Use the source's title
and credited author names in their original order. For two authors, use
`Title - Author, Author.epub`; for three or more, use
`Title - First Author et al.epub`. Preserve author names rather than inventing
abbreviations, and replace only characters that cannot safely appear in a
filename. Use the same output path in the builder, validator and delivery link.
An explicit filename requested by the user takes precedence over this default.

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
introduces a demonstrated defect or the source contains a very obvious typo
under the rule below. Decode saved HTML explicitly as UTF-8 when
that is its recorded encoding; a fragment without a charset declaration must
not be left to a parser's legacy-encoding default. Check for mojibake in the
packaged text as well as in a reader preview.

### Correct very obvious typos in the source

Correct an unmistakable typo even when it is printed in the source itself,
including in clean digital PDFs or structured text. Confirm the occurrence
against the source and check enough surrounding text to establish the intended
reading. Use a narrow, contextual correction in the book's reproducible builder,
record the original and replacement with the source location, and add a
regression check when practical. Report these editorial corrections to the user;
no separate confirmation is needed for a correction whose intended reading is
unambiguous. Preserve ambiguous wording, unusual spelling, dialect, names, and
valid nested punctuation rather than applying broad spelling or quote cleanup.

For example, a sentence ending `and 350 milliseconds, respectively.”` may
contain a stray closing double quote. If the surrounding text confirms that
there is no matching opener and any earlier quotation is already closed,
remove only the stray quote, retaining the full stop and any following note
reference. Likewise, an unmistakable misspelling such as `be a virture.` can
be corrected to `be a virtue.` Do not generalize either example into deleting
all quotes after full stops or rewriting every unfamiliar word.

Pay special attention to:

- periods immediately followed by a letter without a space, including a sentence
  ending in a number (`0 to 1.An impossible event`) or parenthesis
  (`(1999).Working group`). Audit visible paragraph text across inline markup,
  while keeping separate blocks separate. Treat matches as suspicious, not as
  automatic replacements: initials, abbreviations (`U.S.`, `Ph.D.`, `i.e.`),
  domains, filenames, section labels and code may legitimately contain touching
  periods and letters. Check context and add only verified sentence-spacing
  repairs to the builder. `find_period_word_spacing_issues` in
  `conversion/common/epub_quality.py` provides the shared detector;

- fused words (`selfknowledge`, `Ihave`);
- fused short phrases (`ina` for `in a`), which should be repaired with
  case-preserving whole-word matches so substrings in names such as `Karenina`
  are not damaged;
- false hyphenation at line or page breaks;
- spaces around em dashes;
- zero/O and one/I confusion;
- prices whose currency sign or digits have become letters (`SlOO` for `$100`)
  or gained internal spaces (`$1 1,000` for `$11,000`); flag these in monetary
  context and confirm against the scan before repairing, rather than globally
  replacing S, I, l, or O in names, codes, or ordinary words;
- missing punctuation at page boundaries;
- OCR fragments from illustrations or verso bleed-through;
- headers inserted into prose.

Foreign-language prose and names can contain detached spacing accents from
the PDF text map, such as `pre´pare´s` instead of `préparés`, or `Franc¸ois`
instead of `François`. Inventory these marks throughout body text, notes and
references when one is found. Recover the accent's base and direction from
context and source geometry where available, then use proper Unicode letters
or combining marks normalized to NFC. Accent order can vary, especially around
dotless i. Do not globally replace acute marks, backticks or cedillas: they may
be quotation delimiters or technical notation. Keep ambiguous repairs narrow
and check both packaged text and reader display.

Font changes can damage adjacent text as well as formatting. A PDF may render `*Complete Writings*, Oxford` correctly while its embedded text says `Complete WritingsOxford`: the comma and space disappeared exactly where italic and roman runs meet. Word-only italic alignment cannot restore characters that are absent from the text layer. Compare aligned OCR tokens and geometry with the embedded text; when one embedded token equals two or more consecutive OCR words, split it at the OCR word boundaries and restore only OCR-observed edge punctuation and spacing. Likewise, repair an empty separator between two otherwise aligned words from OCR evidence. `conversion/common/italic_markup.py` performs these constrained repairs before adding emphasis markers and reports the number applied.

Audit citations as a separate corpus after ordinary prose cleanup. Search packaged XHTML for implausible years (`1.999`), letter-for-digit dates (`April l` or `April i`), split publication words (`Re view`), malformed page labels, missing spaces after closing emphasis or commas, and titles whose `<em>` span stops midway. OCR is useful evidence, but do not replace whole citations blindly: it may fuse punctuation-heavy strings such as `1,1999,p.5;and`. Render every flagged citation, apply contextual corrections for ambiguous digits, and add the corrected full citation plus the malformed signatures to regression tests.

### 6. Generate semantic EPUB XHTML

When cleaning an existing EPUB or imported HTML, audit inherited Word/editor
styles as well as text. Fixed inch-based indents, oversized heading margins,
empty spacer paragraphs and fixed white backgrounds can make clean text
unreadable on narrow screens. Recover the intended roles from source classes,
neighboring content and the original edition: ordinary paragraphs, inset
quotations, attributions, verse, dialogue and deliberate section breaks. Replace
physical-page styling with modest relative spacing and semantic markup; do not
merely strip every class or join every short paragraph. Wrapped quotation lines
should flow as prose, while poems and separate speeches retain their boundaries.
Inventory substantive subheadings hidden inside larger sections and make them
navigable. Rebuild malformed package metadata and navigation rather than copying
unbound namespace prefixes, duplicate identifiers or mixed EPUB-version markup.
Check complete text order and emphasis coverage separately from visual layout.

Each navigable section should normally have:

- one generated `<h1>`;
- body paragraphs as `<p>`;
- quotations as `<blockquote>`;
- deliberate scene breaks as a semantic or styled divider;
- stable identifiers for notes and links.

A quotation continuing across paragraphs may reopen with a quotation mark at
each paragraph without closing until the final paragraph. Do not balance quotes
independently in each paragraph by inserting invented closers. Resolve
apostrophes within words before pairing single quotation marks; otherwise two
unrelated contractions can be mistaken for the boundaries of a quotation.
Verify repeated speech openings and the final closing mark against the source.

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

### Floating instructional panels and nested exercise lists

Count semantic figures separately from PDF image placements. One anatomical
illustration may consist of many bitmap tiles, vector paths, arrows, and text
labels. Inventory all these components before defining a crop; an extracted
bitmap alone is not proof that the complete illustration was recovered.

Captions can appear above, below, or beside their artwork. A short caption's
width does not define the panel width. Use verified separator rules, neighboring
panels, image placements, and labels to establish boundaries, with explicit
source-reviewed overrides for irregular layouts. Inspect every crop edge in
contact sheets made from the actual packaged assets. Check bitmap coverage
against placement rectangles, and inspect vector lines and labels separately;
complete bitmap coverage cannot detect a clipped vector label or leaked artwork
from a neighboring figure. Keep continued panels together in reading order.

An instructional panel may contain ordinary prose and nested numbered/lettered
steps around photographs. Recover those descriptions as semantic paragraphs and
lists. If the corresponding print text is removed from a rendered image, retain
the original step numbers and letters beside the pictures so readers can match
them to the reflowed descriptions. Perform removal on a copy of the source,
preserving photographs and diagram strokes, and verify the resulting assets.
Do not duplicate entire exercise descriptions inside images and as body text.

Measure list indentation relative to the current column's left edge. Alternating
page margins or a column change do not create a new nesting level. Preserve list
continuity and explicit numbering across pages; use full-width headings to split
column-reading bands, then read each column in order. Place floats at complete
paragraph or list-item boundaries, and check that combined multi-step panels do
not become children of only the final step. Validate legal list structure and
inspect representative numbered lists with nested alphabetic steps in a reader.

Small type outside a captured object can be substantive: qualifications,
footnotes, exercise cautions, and cross-references often use the same small fonts
as figure labels. Audit excluded lines by font and position before release.
Reconcile every exclusion with a captured object or an explicitly documented
omission; retained-text coverage alone cannot expose wrongly excluded notes.
Keep recovered notes visibly separate from the main paragraphs and preserve
their relationship to the relevant figure, table, or passage.

A source may already replace an illustration with an availability or rights
notice. Retain the notice and original caption, record the missing source
artwork, and report that limitation. Do not treat it as a failed extraction or
invent a substitute. Complex tables and blank assessment forms may remain
verified, enlargable images; document their lack of searchable cell text.

Compare the retained source character stream in verified reading order with
packaged prose, allowing only documented transformations. Check styling and
paragraph/list grouping separately, then verify that a reader export retains
every complete paragraph. Rebuild these checks after any crop or font-role
change, because changing object boundaries also changes which text is retained.

Apply complete-paragraph and list-entry formatting decisions after structural
repairs have joined all their fragments. A later transfer from another column
can append text with stale OCR styles, leaving a previously corrected entry
inconsistent again. Reapply the reviewed spans to the final joined text and
validate the packaged complete entry, including deliberately emphasized words
in its transferred tail.


### Sidebar notes are independent text streams

A marginal note can overlap the vertical span of ordinary prose or a list.
Never sort its lines together with neighboring body lines by height: that
interleaves two independent sentences and can split list items. Identify a
sidebar from its complete text block, sustained narrow width, smaller type,
and position relative to the main text column. Small type alone is insufficient;
figure labels, captions, table cells, and footnotes can share that font.

Read and join all wrapped lines within the sidebar first, preserving genuine
paragraphs, bullets, and emphasis. Render it as a visible semantic `<aside>`,
with restrained styling and no fixed width that makes it unreadable on a small
screen. For textbook sidebars, default to introductory placement: put a marginal
quotation or aphorism near the beginning of its source page's material, before
the first complete body paragraph, and after the generated section title when
it opens a section. If the page begins with a sentence continued from the
preceding page, finish that sentence/paragraph before inserting the sidebar.
Do not routinely defer introductory material to the page end or past an
author's closing sign-off. Treat explicit qualifications, cross-references,
and table/list notes as contextual exceptions: place them after the complete
paragraph or list they qualify, with source evidence recorded in the builder. A note that
qualifies a nested list belongs after that list, not inside its final bullet.
Do not reproduce print-only line breaks or describe an editorial sidebar as a
quotation. Remove a leading print-marker asterisk only after its role and
association have been confirmed; keep substantive asterisks elsewhere.

Do not limit recognition to one small font size, a list of page numbers, or
blocks already classified as notes. A pull quote or marginal commentary may use
larger type and initially be mistaken for body text or an inset quotation.
Inventory narrow blocks that occupy a separate horizontal region and overlap
main-column prose vertically, then review typography and neighboring content.
Treat italic/bold variants of the same font family as the same family when
using font differences as evidence. Weight font-family evidence by text length;
a tiny bullet or alphabetic marker in a different font does not define the
surrounding prose. Ordinary narrow exercise instructions must
remain list content, so record rejected candidates as well as confirmed ones.
`conversion/common/sidebars.py` implements this reusable candidate search;
its tests cover both margins, multiple sizes, inset quotations, and narrow
instructions that must not be reclassified.

Audit every similar marginal block when one failure is found. Compare main-body
reading order and sidebar text separately, and add checks that the recovered
note is one complete paragraph, neighboring sentences remain complete, and
list numbering/nesting continues correctly after the note. Verify placement
in a reader, because character counts can pass even when two text streams have
been interleaved.

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

For hanging notes and lists, measure paragraph indentation from the continuation
text's left edge, not from the note number, bullet, or previous line's bounding
box. A marker makes the first line's box extend farther left; comparing the next
line with that box falsely turns normal wrapping into a new paragraph. Determine
the content edge for each block and page, allowing for alternating margins, and
start a paragraph only at a genuine additional indent or another verified
structural boundary. `conversion/common/page_reconstruction.py` provides
`starts_indented_paragraph` for this content-relative check. Keep note labels
inline with the opening paragraph; preserve separate paragraphs, inset
quotations, verse, and displayed equations where the source supports them.

Audit the entire notes section when this failure appears. Check first-line
continuations even when the first line happens to end in punctuation, and flag
paragraphs stranded on a line-ending hyphen or followed by a lowercase
continuation. Character coverage alone cannot detect these breaks: assert that
representative multi-line opening paragraphs remain whole, that genuine second
paragraphs remain separate, and that reader export and visual preview agree.

A source may cite the same note more than once. Preserve those repeated
references rather than treating them as duplicate extraction or requiring a
strictly increasing reference sequence. Give every occurrence a unique anchor,
link all occurrences to the same note entry, and provide return links to each
occurrence when practical. Validate reference occurrences and unique note
entries as separate counts; restarting numbering in another chapter also needs
chapter-qualified note identifiers.

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

Every EPUB must include at least a minimal cover image, including academic
papers and other short works. Prefer a usable source cover; if none is supplied,
generate a simple, legible typographic cover with the correct title and author
(and subtitle when useful). Do not invent publisher branding or imply that a
generated cover is the original. An ordinary XHTML title page alone does not
satisfy this requirement. Embed the image locally, declare it in the manifest
with EPUB 3 `properties="cover-image"`, and put a responsive cover document
first in the spine. Include legacy cover metadata when needed for reader
thumbnails. Verify the packaged image, cover metadata, reading order, thumbnail
legibility and full-size rendering.

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

When repairing a corrupt EPUB, preserve a copy before changing the archive.
A truncated compressed entry may still yield its complete original contents:
accept such recovery only when the uncompressed length and original CRC both
match and the recovered document parses correctly. Repackage with valid ZIP
records, verify every member, and compare all recovered payloads byte for byte.
Do not ignore overlap/truncation warnings or silently discard an unreadable
entry. If exact recovery fails, rebuild a damaged navigation document from
verified surviving navigation/spine data and document that reconstruction.

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

### Recover bold from scans

An embedded OCR text layer may label every word with the same roman font even
when the printed questions are bold. Inspect actual pixels before trusting font
metadata. `conversion/common/scan_styles.py` measures stroke thickness through
one-pixel erosion and italic slant through shear/projection evidence. Render at
a fixed scale, calibrate with visually verified bold and roman samples of the
same type size, and retain positioned word/line scores for the whole book.
Thresholds belong in the book recipe; they depend on resolution, font, contrast,
and scan quality. Review roman controls as well as candidate bold lines.

Reconstruct full question or prompt paragraphs across lines and pages, then
wrap their text in `<strong>`; preserve nested `<em>` when a bold question also
contains italics. Statements can be bold prompts and ordinary prose can contain
question marks, so punctuation or wording alone cannot decide formatting.
Distinguish interview pullquotes and profile labels from question paragraphs.
Validate transitions between prompts and answers, continuation pages, source
character coverage, and rendered reader samples.

For inset blocks, consecutive indented lines are evidence only when their
vertical gaps and left edges establish one sustained block. A normal first-line
indent following a centered quotation must not be absorbed into the quotation.
Resolve block boundaries before paragraph indents, and measure indents relative
to that block's own left edge. Audit paragraph-ending discretionary hyphens even
when complete character coverage passes: coverage cannot detect a word split
between two paragraphs.

In quotation-stack audits, classify an internal contraction or possessive
apostrophe before consuming an open single-quote delimiter. `‘No. I’m busy.’`
contains an apostrophe inside a single quotation, not its premature closing mark.

### Repairs across inline formatting and profile fields

Review corrections on the visible character stream, not only on the raw markup.
An emphasis boundary can interrupt a damaged word, causing a plain string repair
to miss it. `conversion/common/italic_markup.py` provides
`remove_verified_word_hyphens`: it matches reviewed whole-word hyphen repairs
while ignoring internal emphasis markers, removes only the verified hyphen, and
preserves formatting. Check the complete reconstructed word's emphasis against
the source, including fragments on both sides of a physical line break. Never
remove all hyphens globally; legitimate compounds must remain. Test both the
packaged text and the complete expected `<em>` span for reported examples.

Audit mixed dash clusters such as `—-` and `-—` throughout the packaged book and
reader export, especially epigraph attributions. One printed dash can be
recognized as two different characters. Verify each flagged cluster against the
source and record narrowly scoped repairs; do not globally collapse every dash
sequence, because deliberate repeated dashes may be meaningful.

Repeated profile or questionnaire labels are structural boundaries even when
they end in punctuation. A regex word boundary after `?` does not match the
following space: use an explicit delimiter or lookahead appropriate to the
label instead. Start each profile field in its own paragraph and append wrapped
answer lines only to that field. When one merged field is reported, audit every
profile and every known label, count the expected fields, and assert that no
paragraph contains two separate labels. Check reader output and a rendered
profile as well as source character coverage; coverage alone cannot detect
merged fields.

### Use a secondary transcription as a reference

When a useful but imperfect transcription is available alongside a more
authoritative source, compare them regardless of format. The reference may be
an EPUB, cleaned-up OCR PDF, HTML edition, plain text, or another transcription;
the authority may be a scan, digital document, or revised edition. Establish
which source governs the requested edition from the user's instructions,
provenance, and edition information. Easier extraction, cleaner formatting, or
a newer file date alone does not establish textual authority.

Inventory chapters, preliminary sections, notes, bibliography, index, maps and
tables in both sources before assembly. Align corresponding passages using
headings and surrounding text, not page numbers alone. Do not assume that an
unchanged chapter title means unchanged prose, note numbering, or pagination.
Use the secondary transcription to recover semantic hierarchy, paragraph
structure, emphasis, spelling, or obscured characters only where the governing
source supports that reading. Check ambiguous differences against the source
image or layout; record unresolved readings rather than silently choosing the
cleaner transcription. Record verified matches, differences, and the provenance
of repairs in the reproducible conversion recipe. Never substitute a reference
chapter wholesale without verifying its complete agreement, import its errors,
or silently undo an author's revision.

Build metadata, navigation, notes, and any retained index targets for the governing source,
including material absent from the reference. Validate coverage against that
source separately from comparison with the secondary transcription, so shared
omissions or reference-only text cannot pass unnoticed.

For digital PDFs, reconcile the complete retained character stream and italic
stream with packaged XHTML, after documented ligature, whitespace and verified
line-break transformations. Keep separate coverage checks for notes and objects;
reordering a captured table into cells cannot excuse missing surrounding prose.
Recover raised note digits from actual spans/geometry, inventory every note, and
validate the full chapter sequence plus all forward and return links. A note
marker may sit a few points away from the usual margin; use its raised-number
span rather than one exact x coordinate to identify the entry.

Read tables by positioned characters when the extractor merges an adjacent
numeric cell into a label's text run. Reconstruct and verify wrapped row labels,
column headers, each value, and table notes; do not treat one PDF line or span as
one cell. Keep responsive maps adjacent to captions and verify them in a reader.

Determine list blocks before ordinary paragraph indents: list continuation lines
can share the same indentation as normal paragraph openings. Retain each whole
bullet or numbered item across lines, then use block boundaries and source gaps
to return to prose. Empty page anchors must not interfere with dehyphenation;
remove the last visible hyphen, not an intervening zero-width marker. Check every
expected print-page anchor when linking an index, including pages absent
from a sampled set of index references.

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

Large preliminary-section titles can sit in a margin and be extracted after
the page's body text. Audit opening-page display text independently of its PDF
block order and horizontal position. When a verified printed title matches the
generated heading, classify and remove it before prose ordering; a fallback
that treats every large front-matter font as body text can append “Preface” or
“Introduction” to an author's sign-off. Check every substantive preliminary
section for one correctly placed heading and no leaked title in body paragraphs.

### Cascading section-boundary drift

An incorrect start page can place a new chapter’s heading and opening paragraph at the end of the previous EPUB section, while the new section begins in mid-sentence or mid-word. Audit all downstream boundaries whenever one such error is found.

### Invisible notes

Semantically marked EPUB footnotes may be hidden or treated as popups by some readers. For notes that must remain visibly readable, use normal block elements with explicit CSS and retain semantic relationships only where reader behavior has been tested.

### Repeated quotation marks

OCR may duplicate a closing quotation mark, but repeated quote characters can also arise near nested quotations. Do not collapse every doubled quote globally. Verify the source and use an exact or tightly contextual repair, then add a regression assertion for the corrected phrase.

Audit duplicated opening quotes and a quotation beginning with digit `1` followed
by a first-person verb as well as duplicated closers. Check the attribution's
punctuation in context: a quoted statement followed by a speaker tag may need
a comma before the closing quote. When the passage crosses a page or column,
inspect both physical edges for a lost sentence dash before joining the prose.
These are source-review candidates, not global quote, digit, or period repairs.

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

Also distinguish measurement marks from quotations. In dimensions such as
`29” wide` or `4’5” tall`, the quote-shaped glyphs denote inches or feet and
must not be deleted as unmatched quotation marks. When their measurement role
is unambiguous, use Unicode primes (`29″`, `4′5″`); otherwise review the context.

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

When classifying small digits by baseline, exclude whitespace-only spans from
reference-baseline estimates. A PDF may position a separator at the preceding
superscript's height even though the surrounding words remain on the body
baseline. Otherwise a note marker or exponent can be misclassified as a
subscript. Distinguish scripts from note links using geometry, local notation,
and the complete note inventory, and test both roles in the reader output.
Separate font runs may also be returned as separate PDF lines at the same
height; reunite verified same-row fragments left to right before paragraph
reconstruction, especially in references. Check source-observed word gaps at
ligature/font boundaries and discard verified italic-correction spacing before
punctuation or variable primes without introducing spaces inside notation.

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

OCR style metadata can be partly useful: an engine may label essentially all
body text bold while still identifying many italic spans correctly. Verify
weight and slant independently against the scan, and audit unmarked passages
rather than assuming that every genuine italic run was detected. Preserve
source-supported missing emphasis with exact passage-level overrides.


For style-poor scans, maintain source-verified emphasis terms and contextual corrections. A short common word such as *the* must never be added to a global emphasis list: store the complete surrounding phrase and emphasize only the verified occurrence. Escape the prose first and then insert controlled semantic tags so OCR text cannot become arbitrary HTML. Prefer `<em>` over visual-only `<i>`, add regression assertions against the packaged XHTML, and expand the verified evidence as pages are reviewed. This recovers meaningful formatting incrementally without italicizing ordinary uses of ambiguous words.

This project also includes `conversion/common/detect_italics.py`, which uses hOCR word boxes aligned to rendered pixels. For each word it tests a range of horizontal shear corrections and measures how strongly dark pixels align into vertical strokes. Right-slanted italic words typically show a positive best slant and a meaningful improvement over the zero-slant score. Use its JSON output to prioritize and document review; do not apply its candidates blindly. Exclude running heads and marginal furniture, correct OCR tokens, join adjacent candidates into spans, and store approved results with the book-specific material under `tmp/`.

Run formatting recovery across every content page, not merely a representative sample. `conversion/common/batch_detect_italics.py` renders and analyzes pages independently, caches one compact JSON record per page, and deletes temporary images and hOCR. `conversion/common/italic_markup.py` aligns those page-level word records with the builder’s extracted page text, inserts occurrence-level emphasis markers, and reports alignment and application counts. This preserves the distinction between an italic occurrence and a roman occurrence of the same word.

Short words require a stricter classifier, not a global exception. The current detector uses the ordinary slant/gain threshold for words of four or more letters and substantially higher thresholds for two- or three-letter words. A short word inside a consistently italic run can also inherit the run classification. Retain exact contextual overrides only when image evidence cannot classify an isolated occurrence; do not use them as a substitute for the whole-book pass.

After application, require complete evidence-page coverage, high weighted token alignment, no leaked private-use markers, semantic `<em>` markup in packaged XHTML, and reader-rendered spot checks covering isolated emphasis, multiword titles, long italic passages, notes, and nearby roman controls. Running heads may be detected in the page image, but they should remain unmatched because the builder removes them before formatting alignment.

Marginal section numbers and ornamental boxes may be inserted into the first prose line by OCR. Remove them using a layout-specific pattern that requires the ornamental delimiter; do not delete ordinary Roman numerals appearing in prose.

### Hanging lists and publication credits

Recognize numbered and bulleted lists before ordinary paragraph indentation.
A hanging item's continuation lines are indented relative to its number; they
are not fresh paragraphs. Join wrapped words and sentences within each item,
start a new item only at a verified marker, and preserve continuations across
physical pages. Emit semantic lists with distinct items. Check the entire list
sequence in the packaged EPUB and reader export, including long items crossing
pages. Do not mistake endnotes, equation numbers, or years for list markers.

Determine quotation margins from sustained inset lines, since a PDF block
can contain both ordinary prose and a quotation. Reconstruct quotation
paragraphs relative to that inset. Audit every paragraph ending in a line-wrap
hyphen and review the next block; a lowercase continuation should not remain
stranded because indentation changed. Bibliographies may distinguish entries
by a modest extra baseline gap while every line shares the same left margin.
Do not treat every left-aligned reference line as a new citation. Verify the
source entry spacing and join wrapped publication names and words within each
entry before applying hanging-indent styling.

Numeric-only lines can be ordinary citation continuations, such as a volume
number and page range. Classify them from their font, baseline, left edge,
and entry spacing before equation detection. Never attach their digits to a
nearby author name. Audit the whole bibliography when one such fragment is
found; test complete citations and page ranges, since character-presence
checks can pass even when those characters occur in the wrong order.

Join wrapped heading lines when matching fonts, consecutive baselines, and
heading structure show that they form one title. Use the joined title in both
body and navigation; do not join a following numbered heading or Notes label.

Reconstruct index columns in source reading order and distinguish entry starts,
subentry starts, and their hanging continuations from verified indentation
levels. A PDF block's minimum left edge is not a reliable entry boundary.
Preserve subentry indentation in the EPUB and check transitions between columns
and pages, especially where one subentry continues at the next column's top. Do not
attach characters from whitespace-only PDF lines to nearby text. Sorting those
spacer characters by horizontal position can insert spaces inside valid words.

A chapter-opening publication or permissions credit below a separator rule is
paratext. Keep it in a distinct credit block near the chapter opening, and
remove it from the main prose stream before joining pages. Otherwise it can
split an unfinished sentence at the bottom of the opening page. Inventory and
verify every chapter's credit separator rather than applying a blanket bottom
margin cutoff, which could discard actual prose. Preserve chapter bylines too;
they must not be discarded with the generated chapter title.

Do not classify short ordinary words as mathematics merely because they occupy
a separate PDF text line. Fragments such as “In” can share the surrounding
prose baseline and should be merged before equation detection. Keep mathematical
operator names distinct. Decimal points in a math font do not require emphasis:
retain the number as continuous text and audit against forms such as
`0<em>.</em>7` in the packaged output.

### Mathematical expressions and equation images

Do not flatten two-dimensional notation into text. Binomial coefficients need
vertically stacked entries, fractions need their numerator and denominator,
and sums, integrals, matrices, accents, and scripts need their original
relationships. Use semantic text with emphasis and superscript/subscript markup
for simple notation when the source glyphs and baselines can be verified.
Treat mathematical powers, isotope numbers, and note references as distinct
roles; a raised digit is not sufficient evidence for a note link.

For complex digital-PDF formulas that cannot be reconstructed faithfully as
semantic mathematics, preserve isolated source glyph outlines in transparent
SVG. Select the actual glyph occurrences and necessary fraction/overbar rules;
do not crop a whole page's SVG or include neighboring prose. Verify that every
selected visible glyph is present. Math-extension fonts often report ordinary
text boxes for tall brackets or operators: measure the transformed glyph
outlines to determine the true image bounds, and leave a small safety margin.
Use those same ink bounds when associating raised and lowered pieces with a
prose baseline. Otherwise a fraction can be separated from its sentence or a
stacked coefficient can lose its lower entry. Do not group solely by the PDF's
text blocks: one expression may occupy many blocks and one block may contain
both prose and a formula.

Recognize list markers before mathematical-font classification. A bullet may
be encoded in the same symbol font as an equation and printed at a smaller
font size. Neither font family nor reduced size makes it a mathematical glyph
or superscript. A bullet item may contain only mathematics. Preserve it as a
semantic `<ul>/<li>` marker outside any
formula asset; do not center or scale it with the equation. Audit all bullets
in native math and image inventories when one such error is reported. Keep a
displayed equation introduced by an item's unfinished sentence inside that item.
A single PDF text block may contain ordinary prose followed by multiple bullet
items. Detect each marker at line level and reconstruct its hanging
continuations from their text edge; do not classify the whole block by its
first line. Reconcile the semantic item count with a source-marker inventory.

Classify a stacked coefficient from the whole tall fence and its vertical
center, not from the nearest upper entry alone. A numerator can lie within an
inline-attachment threshold of the preceding prose while the coefficient is
clearly displayed below it. Protect every entry, paired fence, equality sign,
and adjoining fraction in that display before attaching fragments to prose.
Check the source-character identities as a group, not merely whether the
finished image contains tall brackets: it can have intact brackets and still
lose its upper `m`. Regressions should prove that all formula entries occur in
the same display asset and none appear in the preceding sentence.

Connect formula components using actual glyph geometry, not only neighboring
positions in an x-sorted character list or similar baselines. A stacked fraction
can place its numerator between denominator script characters in that list.
Keep the complete expression in one outlined asset when linear ordering cannot
preserve it. Test numerator, denominator, fences, scripts, and drawn rules as a
group. Recognize equation labels with letter suffixes, such as `(11a)`, as
labels; an alphabetic suffix must not create a false prose anchor. Include
upright function names such as `exp` and `cov` when grouping their formulas,
and audit isolated ordinary-font formula fragments before release.

Determine whether an expression is inline or displayed before attaching its
scripts to prose. Compare the base-sized mathematical glyph baseline with the
prose baseline; a nearby raised script alone must not pull a centered display
into the preceding sentence. Confirm superscript versus subscript from source
positions, not from a flattened text export. TeX may construct a not-equal sign
from an overlaid negation stroke and equals glyph. Recover that construction as
`≠` in semantic text, or retain its complete source outlines; never export the
stroke as a separate `/` or combining mark beside an equals sign.

Inspect overlaid text glyphs as well as drawn rules for accents and bars.
A roman macron and mathematical letter can have nearly identical origins,
although extraction emits them as separate adjacent characters. Preserve them
as one outlined expression; for a verified Planck-constant construction,
recover `ℏ` as a single semantic symbol. Never leave a detached bar beside an
italic h. Check all occurrences of the same glyph construction.

Keep punctuation belonging to the surrounding sentence outside inline math
assets, including a following comma, colon, semicolon, or full stop. Preserve
punctuation internal to mathematical expressions. Formula images must have no
opaque background and must scale with surrounding text; check their baseline,
size, complete fences, and scripts in a reader preview. Audit all instances of
a discovered failure, not only the reported example. Include stacked
coefficients, inline fractions beside prose, labeled proof steps, large
operators, and neighboring punctuation in visual regression checks. Document
that outlined formulas retain appearance but are not searchable semantic math.

#### Source recovery and conservative native mathematics

A digital PDF can display an equation correctly while its text mapping emits
control characters, private-use characters, replacement characters, or the
wrong ordinary letter. Inspect embedded glyph names and positioned text traces
before trusting extracted Unicode. Recover a Unicode symbol only when the
glyph mapping and source appearance support it. Otherwise retain the actual
glyph outlines. Internal unknown-glyph placeholders must never leak into
visible EPUB prose or be presented as a trustworthy formula transcription.

Mathematical script fonts can map a calligraphic letter to an ordinary letter.
Replacing that glyph with roman or italic text loses information even when
the character count is correct. Accents, radicals, simultaneous upper and lower
scripts, and extension-font constructions also require more than a sequence
of `<em>`, `<sup>`, and `<sub>` tags. Use native markup only when it preserves
the verified notation; retain source outlines for constructions the native
renderer cannot reproduce. Font names and point-size thresholds are evidence,
not universal rules. Calibrate them for each source.

Select SVG glyph occurrences by their source identities and positions, not
by character value alone: the same letter may appear several times in a
formula or elsewhere on the page. SVG transforms and text-trace coordinates
can differ slightly through floating-point serialization. Use a small,
source-calibrated matching tolerance and assert that every selected visible
occurrence matched. Do not silently omit an unmatched glyph or enlarge the
tolerance enough to include a neighboring occurrence. Copy only the required
glyph definitions, occurrences, and verified rules into the isolated asset.

Formula boundaries also need spacing evidence. A raised numerator or tall
fence may have a different baseline from the adjacent word, so a same-baseline
spacing rule can produce `Step 1.` immediately touching its formula or a
closing fence touching `so`. Verify the horizontal gap at each whole-formula
edge and retain the sentence's separators as text. Do not invent spaces
inside an otherwise intact word from unusual font metrics or whitespace-only
PDF lines. Do not italicize punctuation merely because it came from a math
font; preserve the appropriate typography of variables, numbers, and operators.

#### Inventory of mathematical rendering failures found in this project

Use this inventory alongside the procedures above. A reported instance
triggers a whole-book search for its failure class. Detection can be shared;
ambiguous corrections still require source evidence. Do not treat the examples
as a global substitution dictionary.

| Failure mode | Evidence or symptom | Required prevention or check |
| --- | --- | --- |
| Broken PDF glyph mapping | A correct printed symbol extracts as a control character, private-use code, replacement glyph, or ordinary letter. | Compare glyph names, positions, and the rendered source; preserve outlines when Unicode recovery is uncertain; reject leaked internal placeholders. |
| Loss of mathematical letter shape | A script or calligraphic letter becomes an ordinary roman or italic letter. | Verify the actual glyph shape; retain the script-font outline unless equivalent semantic notation is demonstrated. |
| Ordinary prose mistaken for math | A short fragment such as `In` becomes an isolated image resembling `ln`. | Recover the prose row and baseline before detecting equations; inspect isolated short assets and compare their text with the source. |
| Citation numbers mistaken for equations | A bibliography volume or page range is centered, detached, or attached to an author's name. | Classify numeric-only continuations from font and entry geometry; test complete citations and their order, not just digit presence. |
| Bullet absorbed into a formula | The dot before `P(S)=1` is inside the render, scales with it, or becomes a superscript. | Recognize leading markers before font/size classification; keep semantic list markers outside native math and images; reconcile all source bullets with list items. |
| Mixed-block lists flattened or missed | One PDF block contains ordinary prose and several bullet items; wrapped items become separate paragraphs. | Detect markers at line level and join hanging continuations from the verified text edge; do not classify an entire block by its first line. |
| Formula detached from its list item | A displayed expression or its following sentence escapes the numbered or bulleted item. | Preserve the item's structure across equation events and page breaks; inspect the actual `<li>` contents and reader layout. |
| Display pulled into the preceding sentence | An isolated power or the upper `m` of a coefficient is appended to prose. | Classify the whole display using its ordinary-size glyphs, tall fences, and vertical center before attaching fragments to prose. |
| Stacked entry lost despite intact brackets | A coefficient image has tall fences but lacks its numerator or lower entry. | Assert ownership of every source entry in the same formula asset; compare the complete stack visually. Bracket height alone is insufficient. |
| Superscript/subscript or note-role confusion | `r_n` and `r^n` are confused, or a power/isotope digit becomes a note link. | Verify source baselines and meaning; classify mathematical scripts separately from note references; do not infer the notation from flattened text. |
| Fraction and script order scrambled | A fraction or `1/n^(3/2)` is split into assets or exported in x-sort order. | Group components by two-dimensional geometry; preserve numerator, denominator, exponent, and fences together when native ordering is inadequate. |
| Equation label creates a false prose anchor | A label such as `(11a)` or `(A13)` attracts parts of a display into a prose row. | Recognize numeric labels and alphabetic prefixes/suffixes structurally; keep the label associated with its complete equation. |
| Upright function name fragmented | Pieces of `exp` or `cov` become detached ordinary-font math images. | Include verified function tokens in their expression; audit ordinary-font-only formula assets and resolve every finding. |
| Tall glyph clipped | A bracket, large operator, or stacked coefficient loses its top or bottom because the reported text box is too short. | Measure transformed glyph outlines, include safety padding, and inspect all crop edges in a reader. |
| SVG glyph occurrence fails to match | Small coordinate differences omit a selected glyph; matching by letter value selects the wrong occurrence. | Match positioned occurrences with a calibrated tolerance and require complete matches; never silently drop a glyph or include its neighbor. |
| Drawn mathematical rule omitted | Numerator and denominator survive but their fraction bar, radical rule, or overbar disappears. | Inventory relevant PDF drawing paths separately from text; include and validate each required rule. |
| Overlaid operator split | A negation stroke and equals sign appear as `/=`, a combining mark, or separate pieces instead of `≠`. | Recover the verified composite symbol semantically or preserve all overlaid outlines; check every occurrence of the construction. |
| Accent or bar detached | The Planck constant becomes a separate macron plus italic `h`; hats, tildes, checks, or bars separate from their letter. | Inspect overlaid text glyphs as well as drawn paths; use verified `ℏ` or preserve the complete accented construction in one asset. |
| Sentence punctuation absorbed | A trailing comma, colon, semicolon, or full stop enters the formula image. | Classify punctuation by sentence role, keep external punctuation as text, and preserve genuine internal formula punctuation. |
| Font-run typography or spacing damaged | Decimal dots become emphasized, words touch formula edges, or spacing is inserted inside words. | Check packaged decimal spans and whole-formula edge gaps; preserve verified source separators and avoid inference from font family alone. |
| Opaque background or neighboring ink retained | A white rectangle appears behind math, or a whole-page SVG leaks nearby prose. | Use isolated transparent assets; reject opaque background elements and unrelated glyphs; inspect against the reader's background. |
| Formula scaled or aligned incorrectly | Inline math sits too high/low, is much larger than prose, or a display overflows the viewport. | Size inline assets relative to body text, derive alignment from the source baseline and full ink bounds, and preview both inline and displayed formulas at reader widths. |
| Coverage checks pass despite corrupt structure | All characters exist somewhere, but an upper entry is in prose, a fraction is split, or citation digits are reordered. | Track exclusive source-character ownership and expected formula groups/roles; add complete-expression and reading-order checks plus source-to-reader visual comparison. |
| Extracted alt text mistaken for accessible math | An outlined formula looks correct but its raw text map has scrambled order or unknown symbols. | Do not call that map a verified transcription; provide accessible mathematical text only after reconstruction and review, and document the limitations of outlined formulas. |

#### Release checks for mathematical content

Maintain a book-specific inventory of source formula locations, selected glyph
identities, drawn rules, inline/display roles, and surrounding prose. Require
every retained visible source character to have exactly one accounted role;
document intentional semantic replacement of markers and composite symbols.
For every confirmed failure, add an assertion about the complete expression
or structural relationship, rather than only checking that its letters occur
somewhere in the EPUB. Keep source-specific thresholds, reviewed exceptions,
and exact repairs in the book's reproducible builder and evidence files.

Validate the packaged assets and XHTML, then inspect a reader-generated export
and preview. Text round trips verify prose, citations, symbols represented as
text, list order, and links; they cannot prove the correctness of outlined
formula interiors. Inspect those visually against the source. Include all
newly repaired expressions and representative stacked coefficients, fractions
with exponents, simultaneous scripts, script letters, accented symbols, large
operators, equation labels, math-only list items, and sentence punctuation.
Inspect neighboring prose as well as the equation itself. A successful ZIP/XML
check, glyph count, transparent background, or text export alone is never
sufficient evidence that mathematical rendering is correct.

Inventory unnumbered diagrams too. Search for substantial vector paths and
visible image placements outside the numbered figure/table and equation
inventory, then review each candidate against its source page. An image
resource listed in the PDF is not proof that a visible illustration appears
on that page.

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
- [ ] For mathematical content, source formula groups, scripts, rules, and inline/display roles are verified.
- [ ] List markers and sentence punctuation remain outside mathematical renders.
- [ ] Mathematical assets are isolated, transparent, complete, and correctly sized and aligned.
- [ ] Repaired and representative equations match the source in a reader preview; text/character counts alone are not used as proof.
- [ ] Representative pages have been visually reviewed.

## Policy for future updates

Continue accepting reader corrections. Each time:

- repair the affected EPUB;
- look for the same defect throughout that book;
- inspect whether the defect exposes a broader process failure;
- add a narrow automated check or correction where safe;
- record the generalized lesson here without cluttering the guide with every isolated typo.

### Pāli and other scholarly transliterations

Treat diacritics as substantive letters, not decorative accents. For Romanized
Pāli, explicitly audit `ā ī ū ṅ ñ ṭ ḍ ṇ ḷ ṃ`, their capitals, and any additional
letters used in Sanskrit, Sinhala names, or cited languages. Do not restore a
word from an accentless dictionary or a familiar Buddhist term alone: similar
forms can have different meanings, and editions may use different spellings,
compound divisions, or transliteration conventions. The authoritative printed
source decides the reading; another transcription is alignment evidence.

A digitally typeset PDF can look correct while its selectable text is corrupt.
Legacy transliteration fonts may put `ā`, `ī`, or `ṇ` in code positions that
extract as unrelated Latin accents. Even a TrueType cmap or a glyph named
`aacute` can describe the legacy position rather than the printed character.
Inventory every non-ASCII character by font, make a labelled atlas of rendered
glyphs with word context, and verify the complete mapping, including rare
letters and capitals. Keep edition-specific maps and their page evidence in
the book's builder. Apply them only to the demonstrated font/encoding; preserve
genuine accents in French titles, German names, and other languages. Check
ordinary punctuation and apparently mathematical characters too, since a legacy
font may reuse those positions for letters.

When actual OCR is necessary, retain high-resolution word crops and compare
independent recognition with the source. Italics, tiny underdots, macrons,
overdots, and tildes need special attention. Classify combining marks by their
position relative to the base letter; do not turn every accent into a macron
or every `n` into a retroflex nasal. Normalize verified Unicode to NFC and
test both searching and reader display. Never remove diacritics merely to make
the ebook searchable. Use a Unicode font with the required glyph coverage if a
reader preview exposes missing letters or badly placed marks.

Recover emphasis independently from spelling. Align positioned source font
spans with the corrected text, including punctuation at run boundaries and
words split across lines. A Pāli word is not automatically italic, and an
italic span is not necessarily Pāli: English explanations, quotations, titles,
and bibliographic citations also have source typography. A structured reference
can contain correct words while inventing emphasis, losing it, or leaking
Markdown asterisks and editorial placeholders. Audit those separately, and
verify the whole retained italic character stream where the font evidence is
reliable. Do not carry the reference's extra abbreviations, rewritten wording,
or unfinished editorial notes into a source-faithful edition.

Keep genuine hyphens inside Pāli compounds and grammatical analyses. A physical
line-ending hyphen is only a candidate for removal; compare the complete word
with independent occurrences and the printed source before joining it. Retain
semantic verse lineation, numbered paragraphs, commentary notes, and internal
chapter/paragraph references. Pāli glossaries are substantive content, even
when a nonfunctional print-page index is omitted. Validate every glossary entry
and every note target, and inspect representative long italic terms, stacked
diacritics, verse, glossary columns, and dense tables in a reader. Record which
complex tables remain source images and therefore lack searchable interiors.

### Sentence dashes represented by ordinary hyphens

OCR may reduce sentence dashes to ASCII hyphens, and the source itself may use
ordinary hyphens for sentence punctuation. Do not replace all hyphens globally. Inventory hyphenated
tokens with their surrounding clauses, distinguishing lexical compounds,
numeric ranges, suspended compounds (`lower-middle- and middle-class`),
discretionary word breaks, and clause punctuation. Recover line-wrapped words
before deciding what the remaining hyphen means. Preserve compounds within a
longer construction: `parent-lover-friend-the` may contain two lexical hyphens
and one sentence dash. Compound recognition must work at each edge, rather than
classifying the entire token uniformly. Keep source-specific reviewed decisions
in the builder or a correction file, and audit both the converted dashes and the
hyphens retained. An unknown compound is a review candidate, not a safe general
rule for automatic replacement. Test genuine compounds, suspended compounds,
names, year/page ranges, and sentence dashes in the packaged reader export.

### Outlined text in PDFs

A PDF can contain ordinary selectable prose while rendering
chapter titles, interview dialogue, verse, or an entire index as vector outlines.
A blank text extraction is not evidence of a blank leaf. Inventory visible
vector paths and image placements across every page, and compare them with the
text boxes before setting section boundaries or deciding which pages to omit.
Recover outlined text from isolated, high-resolution crops and verify OCR
against those crops. Exclude decorative rules and underlines from that OCR;
a crop of an underline can otherwise duplicate the selectable paragraph above
it. Preserve dialogue speeches and verse lineation when reinserting the text.
When an outlined index is explicitly retained and cannot be faithfully
reconstructed as semantic text, preserve complete, sharp source panels and
document that limitation. Crop away
empty page margins, verify every panel, and constrain both image width and
height so a narrow, tall panel does not create blank pages in a reader export.

PDFs containing previously OCR'd text may also reproduce damaged note markers as
ordinary baseline characters. Re-rendering or running OCR again cannot restore
a digit that the PDF itself has already replaced with an apostrophe. Separate
source corruption from new extraction errors. Recover a marker only when the
surrounding passage, adjacent reference sequence, and corresponding note entry
support it; preserve and report uncertain source punctuation rather than inventing
a number. Recognize new note entries before joining physical pages: a page-top
`16.` is a new note even when its left edge matches a prose continuation. Split
multiple note entries inside a single PDF block using their line starts, then
check each chapter's complete note sequence and all generated link targets.

### Fused words and digit errors inherited from an OCR ebook

When a PDF was made from an OCR ebook, defects such as `ForJoe`, `importantto`,
`ofwhat`, or `6:3o` may already be present in both its selectable text and its
visible page. Compare the original page and positioned characters before blaming
paragraph joining or EPUB rendering. Re-OCRing that same defective page cannot
restore a space or digit that was absent when the PDF was produced.

Audit letter/digit mixtures in times, years, percentages and page references,
and unexpected internal capitals and fused short words. Detection may be broad;
corrections must use reviewed whole tokens or tightly constrained contexts. Do
not split every word beginning with `of`, `in` or `for`, and do not replace every
`o`, `i` or `l` with a digit. Legitimate words and names such as `office`,
`information` and `FitzGerald` must survive. Record clear repairs in the book's
recipe and verify the packaged reader text. Respect a user's instruction to
limit cleanup of a badly corrupted source; document ambiguous damage rather than
undertaking an unrequested reconstruction.

A grave accent/backtick may stand in for an opening single quotation mark in
OCR-derived prose (``My wife said, `Before ... houses.'``). Treat it as a quote
candidate, verify the complete quoted span, and restore a matching `‘…’` pair.
Do not repair only the opener while leaving a mismatched ASCII closer. Preserve
contractions, possessives and note-marker distinctions inside and beside the
quote; broad replacement of apostrophes is unsafe. Assert both the corrected
complete quotation and the absence of its damaged opener in the packaged EPUB
and reader export.

Also check for false spaces inside words, such as `de pendent` for `dependent`.
Confirm the reading from sentence context and the source, then use a reviewed
whole-phrase repair. Do not join short-word sequences globally: legitimate
phrases such as `a part` must remain separate. Check every occurrence of a
confirmed damaged form and add a regression assertion for its repaired context.

A false paragraph break may already be visibly typeset into an OCR-derived PDF,
not merely introduced by extraction. Audit incomplete prose paragraphs followed
by lowercase fragments within the same page as well as across page boundaries.
When sentence continuity is unambiguous, repair the paragraph in the builder even
if the source shows extra vertical spacing. Assert that the complete sentence
belongs to one paragraph; finding its words anywhere in the export is insufficient.
Keep verse, headings, lists and genuine quotations outside this joining rule.

### Auditing a recovered scan against a secondary transcription

An original scan can resolve errors already typeset into a secondary PDF or
EPUB. Align retained sections and passages, compare the complete word streams,
and preserve an inventory of disagreements and source-page evidence. The
scan's own OCR is independent evidence, not automatically correct: inspect the
printed pixels before accepting disagreements involving digits, names, wording,
or punctuation. Keep verified repairs in the reproducible book builder.

Word comparisons ignore punctuation and can miss defects shared by both OCR
versions. Audit separators between aligned words separately, especially missing
sentence dashes, hyphens substituted for dashes, genuine compounds turned into
dashes, suspended compounds, and punctuation touching quotation marks. Review
nested quotation openers and their matching closers together; replacing a
backtick alone can leave the closing single and double marks in reverse order.
Distinguish apostrophes within the quotation from its closing delimiter.

Reconcile every numeric note reference with its section's complete notes
sequence. Assert the ordered reference list, not merely the existence of note
targets or equality of distinct counts; omissions, duplicate markers, and false
references can otherwise cancel one another. Check paragraph continuations
across separate quotation containers as well as adjacent prose paragraphs.
When damaged nonsearchable panels are replaced by authoritative scan crops,
verify their full coverage and edges and document the retained accessibility
limitation.

### Print indexes in reflowable EPUBs

Omit a print index by default when its page-number references have no usable
destinations in the EPUB, especially when it would be retained only as scanned
images. A searchable ebook does not need a nonfunctional reproduction of print
page references. Remove the index from the reproducible builder, navigation,
spine, manifest, and packaged assets; do not merely hide its contents with CSS.
Record the omission and verify that no index document, image, or dangling link
remains in the finished EPUB.

A curated index can add value beyond literal text search by grouping concepts,
synonyms, and subtopics. Retain or rebuild it when the user requests it or when
its references can be converted to verified links to the relevant passages or
preserved print-page anchors. Do not treat reflowed reader page numbers as
equivalent to the original print pagination.

For a structured HTML source, inspect existing index links before deciding to
omit its index. If the references already target print-page anchors, preserve
those anchors at their original text positions, redirect links after splitting
chapters, and validate every destination. Hide only the visible folio labels;
retaining a functional index must not insert printed page numbers into prose.

### Academic papers and positioned objects

Preserve a paper's title, author, version/date, publication or working-paper
identifier, abstract, classification codes, and authored acknowledgments.
Separate institutional boilerplate and postal/contact details from substantive
front matter. Preserve numbered section/subsection hierarchy in both content
and navigation, and keep footnotes distinct from bibliographic references.

Inspect the abstract and preliminary pages visually even when the main text's
font metadata is reliable. A visibly italic title can be reported within an
ordinary roman-font span with no italic flag. Matching the extracted italic
stream cannot prove that all visible emphasis was recovered. Store a contextual,
source-verified formatting repair for such cases and test the packaged span;
do not describe missing metadata as evidence that the source uses plain type.

When reconstructing a table, group positioned cells into verified row bands
before extracting each row. A PDF may report each cell as a separate text line;
extracting the entire row once for every cell duplicates all its values. Check
expected row counts, every value's row/column association, and numeric-cell
coverage with multiplicity. Preserve multilevel headers and blank cells.

An embedded figure bitmap's native aspect ratio can differ from its printed PDF
placement. Inspect its transformation/placement rectangle before reusing the
raw asset. Preserve the verified printed appearance with a source-rendered crop
when necessary; retain labels and legends, and keep captions and figure notes
as adjacent text. Do not silently fix contradictions already present between a
figure's title, axes, and source note.

### Cleaning an existing EPUB with numbered remarks or arguments

Treat a found EPUB as a secondary transcription, even when its XHTML is well
formed. A complete sequence of headings does not establish textual completeness:
a converter can omit a quotation, the opening of a remark, or a whole paragraph
while retaining nearby numbers. Compare the text as well as the structure with
the matching source edition. Preserve the translation actually supplied; a
newer translation or an automatically translated web transcription is not an
interchangeable spelling reference.

Inventory the complete expected number sequence. Check for missing, duplicated,
and transposed digits; literal Markdown headings absorbed into paragraphs;
numbers misread as letters; and genuine numerical examples misclassified as
headings. Restore each boundary from the printed text and verify the ordered
sequence after packaging. Do not manufacture empty sections merely to make the
number count pass. Keep remark identifiers stable when splitting long content
files for reader compatibility.

Remove converter-added introductions, endorsements, and credits when requested,
including their navigation entries and unused associated assets. Preserve the
author's preface and substantive translator/editor notes. Credit a translator as
a translator in metadata, not as another author. Check the cover's edition and
translation claims against the actual text; replace a misleading borrowed cover
with an accurately labelled minimal cover.

In philosophical, linguistic, and mathematical examples, an intentionally odd
formula, meaningless symbol sequence, or mirrored word can be the subject of
the argument. Do not repair it into a conventional expression. Verify the
printed notation, preserve superscripts, subscripts, and negation signs, and
retain an unusual visual construction as a closely bounded source image when
plain text would lose its meaning. Inventory these objects separately from
ordinary illustrations: a text-only comparison can miss a wholly omitted
mirrored-word example or a progression represented only by dots.

Independent OCR is evidence rather than an automatic replacement for the old
transcription. Repeated first-letter confusions can turn valid words into other
valid words; apply repairs only at aligned, source-supported occurrences. Audit
punctuation independently: asterisks may be closing quotes, apostrophes, real
note markers, or deliberate symbols, while carets and underscores may be scan
noise. Review their page images and record contextual decisions instead of
replacing each character globally. Handwritten underlining can also distort
word OCR and italic measurements. Calibrate style detection on both marked and
unmarked source examples; do not extend one style measurement across a merged
OCR token containing both italic and roman words.


### Spacing at quotation and emphasis boundaries

Audit the visible prose stream across inline markup, not each text node in
isolation. An opening double quotation mark fused to a preceding word normally
needs a space: `the word“number”` becomes `the word “number”`. Likewise, remove
stray horizontal whitespace before a sentence full stop, including after an
emphasized span: `<em>conceptual confusion</em> .` becomes
`<em>conceptual confusion</em>.`. Preserve the emphasis and links while editing
their surrounding text; flattening the paragraph to repair spacing loses style.

Use `conversion/common/prose_spacing.py` for these constrained repairs. The
shared OCR normalizer invokes its plain-text form; builders recovering clean
digital text or existing EPUBs should invoke its XHTML form at final assembly
when these extraction defects are present. Preserve spaced ellipses, decimal
notation, deliberate dot patterns, code, and mathematics. Treat images and
formula spans as barriers rather than joining their neighboring text for a
prose correction. Do not globally remove every space before every punctuation
mark, or insert spaces around apostrophes and closing quotation marks. Test
positive examples across emphasis boundaries and negative notation examples,
then validate the packaged XHTML and reader-exported text.

When a punctuation audit finds definite defects, review the source and repair
them before release. Missing ellipses and closing quotation marks can coexist
with false paragraph breaks, including quotations interrupted by inline
pictures. Rejoin only source-confirmed continuations and preserve the pictures
at their semantic position. Record each exact repair and any obvious source
typo separately; do not dismiss all findings as ambiguous or balance every
quotation globally merely to clear the audit.


### Publisher EPUB tables in auxiliary documents

An EPUB may show an image of a table in its main article while supplying a
complete HTML table in a separate, non-linear document. Inventory these
auxiliary spine items before reconstructing or retaining image-only tables.
Compare every row, header, value, unit and note with the packaged table image.
When the semantic table is faithful, bring it into the main reading flow at
the original position, retain its caption and notes, and redirect every
cross-reference to the inline target. Remove redundant detail documents and
unused table images only after accounting for their contents and links. Check
all cells and emphasis against the original and inspect narrow reader output;
well-formed HTML alone does not establish a usable table layout.

When auditing punctuation in readable text, account for linked superscript
citations separately. Flattening a closing quotation mark directly against a
reference digit can make a valid quotation resemble an apostrophe inside a
word. Ignore the citation's digit for quotation classification, or insert an
audit-only separator around it; preserve the actual superscript and link in
the EPUB. Do not delete or rewrite the quotation to silence this false flag.

### Loose text and notes in malformed HTML

A web page can display complete notes while its parsed HTML leaves their text
outside paragraph elements, split between element text, sibling emphasis tags,
and element tails. Inventory those fragments before selecting only `p` nodes.
Reconstruct each note from its complete fragment range, preserve spaces at
inline boundaries, and give every reference a verified target and return link.
When copying a body paragraph whose tail belongs to the following note, detach
that tail after assigning it to the note; otherwise it can appear twice or be
mistaken for another body reference. Check ordered text and emphasis coverage,
including spaces between roman and italic runs, in both the package and reader
export. Do not silently omit content merely because the source markup is invalid.

### Note markers inside headings

A heading can contain a note reference in the middle of its wording. Retain
that reference and destination in the content heading, but omit the note digit
from its navigation label. Derive the label from a clone and remove only the
reference's text: preserve the removed element's tail (the words following the
marker) by attaching it to its preceding sibling or parent text. Deleting the
whole element without preserving its tail can silently truncate a chapter
title. Check the complete title around a middle-of-heading reference, as well
as the forward and return note links.

### Symbol-aware comparison and style recovery

A word-only comparison may report a false omission when a correctly transcribed
symbol has no word token: for example, a reference's `&` can disagree with an
OCR token `8c` even though nothing is missing. Inspect the complete character
span before inserting a supposedly absent word. Do the same for fractions,
ellipses, quotation marks and note markers, and audit separators independently
of words. An authoritative scan's OCR may contain handwriting or underlining;
its extra tokens are not evidence of missing authored text.

When recovering italics from scan pixels, OCR spelling and printed style are
separate questions. A uniquely aligned one-word gap between matching neighbors
can retain strong measured italic evidence even if the OCR misspells that word;
keep the verified transcription rather than copying the misspelling. Likewise,
reconcile two italic OCR fragments split at a printed discretionary hyphen with
the single joined word in the ebook. Record these positional decisions and
exclude marginal annotations; neither a global emphasis vocabulary nor an
unconstrained fuzzy match is an acceptable substitute.

Treat explicit XHTML `br` elements as line boundaries during punctuation audits
and as barriers during prose-spacing repairs. Concatenating verse lines without
a separator can invent defects such as `dark.When`; inserting a space into the
markup to satisfy that false audit does not fix the extraction method.
`conversion/common/prose_spacing.py` preserves this boundary.

### Soft line breaks in structured tables

HTML table cells may use `br` solely to wrap a name or phrase for print, for
example `Beauclerk or<br/>Beauclerc` or `Cal'dron not<br/>Cauldron`. When the
lineation has no semantic role, replace that break with an ordinary space while
preserving adjacent emphasis and text. Readers, copy/export paths, and text
extractors can otherwise concatenate the words when they flatten the cell.
Keep meaningful lineation in verse, addresses and comparable structured text.
Validate table phrases with whitespace collapsed to one space, not removed
entirely: a character-only comparison cannot detect `orBeauclerc`. Check both
packaged cell text and reader-exported text for the full separated phrase.

### Keep physical line evidence independent of joined text

Joining a discretionary hyphen must not change the original line's bounding
rectangle. Removing the continuation token and then recalculating that line's
left edge can make an ordinary continuation appear indented, creating false
paragraphs throughout a book. Retain the original physical line geometry and
use a separate character map for the joined text. Infer the body margin robustly
from ordinary full-width lines, allowing for page skew; a single dust speck at
the extreme left must not define the margin. Audit both unusually short
paragraphs and runs of lowercase continuations after reconstruction.

### Distinguish edition cuts from missing OCR lines

An older transcription may contain a passage absent from fresh OCR even though
the authoritative scan still prints it. Before classifying that difference as
an edition cut, inspect the source image, especially where consecutive text
lines have an unexpectedly large vertical gap. A second OCR pass using a
different segmentation mode can detect skipped lines independently; inventory
its proposed additions and verify them against the scan rather than inserting
them wholesale. Likewise, an OCR line with word boxes spanning several physical
lines can displace a phrase. Check its actual position on the page.

A secondary transcription can also have passages in the wrong order or under
the wrong chapter. Follow the authority's reading order, search nearby sections
for transcription evidence, and audit the remaining unmatched words inside
recovered passages. A high overall alignment score does not establish complete
text, correct order, or correct punctuation.

### Orphaned symbols and punctuation clusters

Audit the entire packaged text for symbols with no plausible role in their
surrounding prose, including isolated copyright or degree signs, angle brackets,
and clusters such as a full stop followed by a dash and semicolon. Scan noise
can produce ordinary-looking punctuation as well as unusual Unicode characters.
Flag these for source-image review, including occurrences in the middle of a
paragraph; do not inspect only paragraph endings. Preserve legitimate degrees,
copyright notices, mathematics, note markers and deliberate ornaments. Remove
confirmed artifacts in the reproducible builder and test their full contexts.
An unexpected symbol is an audit trigger, not permission to delete that symbol
globally or assume it is a missing numeric note.

### Language-aware punctuation spacing

In ordinary English prose, flag spaces immediately inside opening quotation
marks and before semicolons, colons, question marks and exclamation marks.
Repair verified extraction spacing across emphasis boundaries without flattening
the formatting. Apply rules for the passage's language: French normally uses
spacing before punctuation such as an exclamation mark, often a nonbreaking or
narrow nonbreaking space. Do not apply an English space-before-exclamation rule
globally to French passages or multilingual books. Preserve notation, verse
indentation and deliberate typography where those spaces have a role.

Audit spaces beside lexical hyphens separately from sentence dashes. A wrapped
compound such as `blue- stocking` may need `blue-stocking`, while a stray hyphen
between ordinary words may need removal and a clause dash may need an em dash.
An extra hyphen adjoining an em dash is suspicious; verify and repair the
complete cluster rather than treating the hyphen as a word-break marker.

### Dialogue, inscriptions and secondary headings

A secondary transcription may already have collapsed several printed dialogue
turns into one paragraph. Its paragraph boundaries are useful evidence but
cannot be the only source of structure. Check the first word and quotation
opener of each physical line, page-top continuations, and indentation against
the scan. Preserve each printed turn as a separate paragraph, while retaining
an attribution and a second quotation belonging to the same speech together.
Treat short displayed inscriptions and mottos as possible verse even when OCR
does not classify their lines as an inset block; preserve their lineation and
verify the complete opening/closing quotation pair, including ASCII closers.

When using a secondary transcription to supply missing text, classify extracted
part/chapter headings before accepting insertions at section boundaries. They
must not be appended to the preceding sentence when the EPUB already generates
those headings. Scan all body paragraphs for heading signatures after collation,
not just after initial PDF extraction.

When stray punctuation is found, also audit punctuation attached to short
function words (for example `a, book`) and hyphens or plus signs immediately
before ordinary words at former line starts. Dust, damaged type and line-edge
specks can create plausible punctuation; do not remove these marks globally,
since genuine clauses, dashes, compounds and mathematics can match the same
shapes. Review the source line and retain contextual exact repairs. At physical
page boundaries, a spurious full stop may conceal a continuation such as
`and so. / , forth.`. Compare both facing text fragments with the scan before
joining the paragraph; terminal punctuation alone is not proof of a boundary.

Also audit paragraph beginnings for stray punctuation or a single word that
completes the preceding sentence. Move a verified stranded final word back to
its sentence while preserving the following real paragraph; merging both whole
paragraphs would conceal a different structural error.

### Illustrated exercise lists and numbered subsection titles

For textbooks, inventory every printed list marker and reconstruct each complete
item before sorting it into reading order. Two adjacent descriptions may share
all their baselines while belonging to independent columns or cells. Do not
interleave their lines by vertical position, and do not infer a new list level
from a page-margin change or from crossing a fixed column threshold mid-word.
Use the source text block, hanging continuation edge, marker sequence and panel
boundaries together. A marker may be extracted alone on the same baseline as
its description, or two levels may share a line (`2. a.`); recover both levels
explicitly. Preserve verified numbering across pages and validate marker values,
nesting and the complete continuation text for every item, not only a sample.

A numbered short title can introduce a subsection rather than a list item.
Check the following paragraphs and the source hierarchy before classifying it.
Render a verified numbered subsection as a heading, retaining its number. When
an item has a separately printed label followed by explanatory prose, keep the
label and explanation in separate blocks even if both share one extracted PDF
text block; do not append the explanation to the title line.

In the specific case of an introductory list label followed by examples printed
one per line, preserve the first example on its own line as well. OCR/extraction
may put that first example in the label's text block while the remaining examples
form separate blocks. Reconstruct the examples as a nested semantic list when
the source supports it; do not split ordinary prose merely because it contains
`e.g.` or a physical line ending.

If an illustrated exercise plate is separated into reflowable items, complete
the separation: associate each picture or vector cell with its numbered exercise
and, where the source distinguishes them, its lettered variation. Do not leave
a combined plate attached to the final item, or split only the prose while
letting unrelated pictures drift together. Record source rectangles and explicit
step-to-image mappings; geometric proximity alone is insufficient when captions
sit below or beside their pictures. Preserve complete vector drawings, labels
and arrows, not only embedded bitmap resources. If one source illustration
serves several variations or an entire motion cycle, keep that shared relationship
explicit rather than inventing a one-to-one mapping. Audit complete artwork
coverage after splitting, and visually inspect every new crop and its association
in the packaged EPUB, along with narrow-screen reader examples.

A placed bitmap's rectangle can overlap another picture, causing a page-rendered
crop to contain a corner of the neighbor even though bitmap coverage is complete.
Inspect crop edges and use source-verified cell boundaries or narrowly recorded
cleanup masks to remove only the foreign fragment. Vector poses can also extend
below or beside their descriptions; the first caption line is not a safe crop
edge. Audit vector-path coverage as well as bitmap coverage after splitting a
plate, then visually check the result. Retain movement arrows and panel labels.

Audit every font run inside an exercise-description block, including smaller
qualifications. A parenthesis or a short alternative such as “or opposite sides”
may be printed at caption size while remaining part of the instruction. When
splitting illustrations, recover that text into its item's prose before removing
it from the image. Search for small text classified as artwork inside blocks
that otherwise contain list descriptions; ordinary prose coverage checks cannot
catch text that was wrongly excluded from the prose inventory.

### Wide justification gaps mistaken for paragraph breaks

Digital PDF extractors may return separate “lines” for words on the same
physical baseline when justified text has unusually wide spaces. In ordinary
prose, consecutive, horizontally ordered fragments within the same source block
and baseline belong to one physical line. Join them before interpreting their
horizontal positions as paragraph indents or column changes, preserving inline
formatting and the original row's left edge for the following wrapped line.
Do not extend this rule across independent table cells, exercise descriptions,
headings, or columns merely because they share a baseline.

Audit the packaged paragraph boundaries against positioned source lines. Flag
boundaries that split one physical prose line, as well as isolated short words
and lowercase sentence continuations. Verify candidates against the rendered
page and test the complete reconstructed sentence; text coverage alone can pass
while every word is present in the wrong paragraph.

### Stray OCR glyphs and contradictory punctuation

Audit the entire packaged text for unexpected Unicode scripts and non-ASCII
digits, even when the surrounding text is ordinary English. A Bengali digit
inside English prose, or trademark/service-mark symbols (`™`, `℠`) in an older
book, can be OCR interpretations of ink specks. Inventory every occurrence and
check the scan; preserve genuine foreign-language text, numerals, trademarks,
note markers and technical symbols. Never delete all non-Latin characters.

Flag isolated apostrophes between words (`in ' sentiment`), adjacent conflicting
punctuation (`person, .`, `them,.`, `want,,.`), and full stops followed by a
lowercase word (`lazy. and active`). These are review candidates, not automatic
global replacements. An apparent full stop may be a speck, a misread comma, or
a real sentence boundary with a misrecognized lowercase initial; it can also
split a word (`tur. bulent`). Compare the scan to decide whether to remove the
mark, restore another punctuation mark, join a word, or capitalize the next
word. Preserve abbreviations, initials, decimals, ellipses and deliberate
lowercase quotation openings. Record exact verified repairs and rerun the audit
across the whole book, including text split by emphasis markup.

### Keep source filenames out of EPUB metadata

Do not embed source-PDF filenames, local paths, download-site labels or temporary
working filenames in the package metadata, including `dc:source`, descriptions
and identifiers. Keep file provenance and conversion evidence in the external
book-specific build records. When bibliographic source metadata is useful, use
a proper edition citation or authoritative publication URL. Inspect all packaged
metadata fields before release; removing visible source credits alone is not
sufficient.

### Image-led books and designed quotation pages

Inspect how images are actually stored before promising direct photo extraction.
A PDF can consist entirely of one JPEG per page, even when the prose looks
cleanly typeset. In that case there are no separate original photograph objects
to extract. Preserve complete photographic plates and designed text pages by
copying the embedded image streams unchanged. Recover illustrations embedded
in prose pages by cropping the decoded page at native pixel coordinates and
saving losslessly; do not resize, repeatedly JPEG-compress, or render the PDF
at a lower resolution. Record source dimensions, crop rectangles and hashes,
and prove full-page assets are byte-identical and crop pixels match the source.
Do not claim to have recovered higher-resolution camera originals.

Treat large typographic quotations, calligraphic pages and graphic chapter
dividers as designed illustrations when their aesthetic arrangement is part of
the book or the user requests it. Keep them inline in the source reading order,
with sensible viewport sizing and semantic navigation. Do not turn OCR of those
pages into duplicate body paragraphs. Preserve full-page photographic captions
and any multi-panel arrangement already integral to the image. Identify dense
back matter retained as facsimiles in the book's conversion record.

In image-led books, marginal text that resembles a sidebar may actually caption
an adjacent, preceding, or following photograph. Classify it by function before
applying the default introductory-sidebar placement. Associate numbered figure
captions with their figure; keep “previous” and “overleaf” descriptions near the
referenced plate sequence. Extract caption text independently from narrative
prose so it cannot be joined into an interrupted sentence. When publisher matter
shares a page with a photograph or substantive illustration captions, omit only
the publisher material and retain the photograph and captions.

Audit crop boundaries against pale artwork and circular or irregular pictures.
A dark-pixel or color threshold measures strong ink, not the complete image:
light edges and small figure labels may extend well beyond its detected bounds.
Use the neighboring prose and white gutters as additional evidence, review every
new crop, and retain full-bleed edges at the page boundary. OCR prose columns and
margins separately after this classification; a whole-page OCR pass may merge a
small caption and a large drop-cap paragraph onto the same text line. Recover
verified drop capitals explicitly and audit every chapter's first sentence.

Caption columns can vary in width even within a repetitive book. Some
right-aligned captions extend much farther left than their neighbors, and some
outer-margin lines reach the page edge. Use the full available margin up to the
verified prose gutter, then audit OCR words touching crop edges. A plausible
OCR sentence is not evidence that its first or last words were fully captured.

### Continuous artwork across facing pages

Inventory double-page illustrations as logical spreads. When an image is meant
to continue from the left page onto the right, stitch the native pixels in that
order and embed one lossless image in both the EPUB and any requested image
archive. Do not leave the two halves separated by reflowed prose or export them
as duplicates alongside the joined result. Distinguish whole photographic pages
from image bands on prose pages: stitch only the artwork bands in the latter
case, retaining both pages' narrative and captions as semantic text.

Use a shared vertical source interval for matching bands, and verify that the
left and right halves meet at the correct height. Preserve full-bleed page edges
at the seam; do not invent missing artwork or crop away printed content to hide
a genuine gutter. Do not resize either half to force an alignment. Save joined
JPEG-derived pixels as PNG to avoid another lossy encoding, and validate each
half against the corresponding source pixels. Keep provenance, source-page
pairs, dimensions and checksums in an archive inventory. Confirm that the image
ZIP contains the same joined assets as the packaged EPUB, with no orphan halves.

### Figure labels, captions, and obsolete print directions

Inventory numbered illustrations as individual semantic objects, rather than
assuming that one horizontal picture band is one figure. Neighboring pictures
with different figure numbers need separate crops and their own adjacent
captions. Captions may be printed above, below, in a margin, or on a neighboring
page; reconcile every printed number with the image inventory before placement.
When one source caption describes a series, retain that description once and
associate every member explicitly, with linked figure labels if needed. Keep
multi-panel artwork that has a single source figure number together.

A reflowable caption must not duplicate a figure number already baked into its
image. Crop the artwork itself and exclude the external printed label, using
the white gutter between art and label. Preserve letters, scales, diagrams and
other labels that are actually inside the artwork. Validate crop bottoms against
the complete printed-label bounding boxes and check every crop visually. Facing
pages can contain both continuous artwork and separate neighboring figures:
join only the continuous object, preserving the neighbors as their own figures.
Retain native pixels and update any image archive from the same final assets.

Normalize figure references to one space between abbreviation and number, such
as `fig. 1`; audit missing or repeated spaces across inline markup. Check that
an OCRed `Jig.` or `Sig.` is really a figure label before correcting it. Use the
book's verified abbreviation and capitalization consistently.

Remove print-only guide headings such as `PREVIOUS`, `OVERLEAF`, and `FOLLOWING`,
and leading printed-page labels, from converted captions. Preserve the actual
illustration description and place it with the relevant image. Translate useful
internal page references into live EPUB links to figures or sections instead of
leaving nonfunctional page numbers. If descriptions baked into a scan contain
those labels, recover the descriptions separately before removing the scanned
caption block. Update left/right-page directions to meaningful plate or panel
references when the original arrangement no longer exists.

### Line-end hyphens and incomplete emphasis runs

Do not treat a line-final hyphen followed by lowercase text as sufficient proof
of discretionary hyphenation. Inventory the original token pairs before joining
lines, including caption columns and paragraph continuations across images or
pages. Distinguish syllabic wraps from grammatical compounds (`eighteenth-century`,
`well-educated`, `self-regulation`), proper names, date ranges, and suspended
compounds (`nineteenth- or early-twentieth-century`). The last case retains the
hyphen and the following space; an ordinary compound retains the hyphen without
a space. Confirm ambiguous cases from source context and other occurrences in
the book. Preserve a reviewed decision and test each resulting form rather than
trying to repair already-fused compounds with a broad spelling dictionary.

Once an English book's unspaced em-dash convention is verified, remove extraction
whitespace beside its sentence dashes after physical line joining, including in
captions. A dash at the end of a printed line must not inherit a space before
the next word. Keep deliberately spaced display typography and other language
conventions outside this prose normalization.

Word-by-word italic detection can leave only a title's middle word emphasized,
particularly when short articles and prepositions provide weak slant evidence.
Audit short emphasis fragments and partially styled titles/foreign phrases.
Check the complete source phrase, including articles, connectives and words on
the next physical line or page, and restore the whole verified run. Add a check
that every character of that occurrence has the expected emphasis. Do not
italicize every occurrence of the same words globally: a book title may match an
ordinary subject term used elsewhere in roman type. Preserve contextual source
identities or the surrounding phrase to distinguish them.

### Excess margins around extracted illustrations

After splitting neighboring illustrations, audit the outer margins of every
final crop, including the assembled result of a stitched image. Trim verified
blank page gutters to the artwork bounds, leaving only a minimal protective
edge where needed. Ignore isolated JPEG speckles when detecting bounds, but
visually check faint lines, pale backgrounds, captions internal to the artwork,
and small scale labels before trimming. Preserve intentional space inside a
multi-panel figure and alignment at a stitched seam. Use the same reviewed
native-resolution crop in the EPUB and any image archive, and retain the crop
coordinates in the reproducible build evidence.

Inspect crop edges at native resolution as well as in reduced contact sheets.
A one-pixel pale scan border can remain visible when enlarged even though a
thumbnail looks tightly cropped. Audit the complete outer rows and columns for
near-uniform pale strips followed by a sharp transition into rectangular art;
remove verified strips rather than retaining an arbitrary protective white
border. Do not mistake pale photographic content or deliberate print borders
for page whitespace. Check the packaged image bytes, since a correct working
crop does not establish that the final EPUB contains it.

A fixed near-white threshold is insufficient for scan borders: interpolation
and JPEG compression can turn an edge into a uniform grey or tinted strip.
Compare the first few outer rows/columns with the neighboring image content,
using both brightness and variation along the edge. A nearly uniform pale strip
followed by a sudden darker or more textured row is a review candidate even
when it is below the white threshold. Remove the verified interpolation fringe
as well as the blank strip. Review all edges of all figures when this occurs;
for stitched artwork, adjust the outside edge or both aligned vertical bounds
without deleting genuine artwork at the interior seam.


### Unmatched brackets and parentheses in OCR

Audit opening parentheses, square brackets, and braces against their matching
closers across each semantic paragraph or continuous quotation. An unmatched
opener may indicate that OCR misread a closing bracket as a letter, digit, or
punctuation mark; for example, a trailing `j` can be a damaged `)`. Report the
source page and surrounding text, inspect the scan, and repair only the
verified occurrence. Allow reviewed mathematical notation, editorial fragments,
and brackets spanning intentionally separate blocks; do not insert closers or
replace letters globally merely to balance a count.

### Typography and line recovery across layout changes

Calibrate scan-based bold detection against ordinary prose at the same printed
size. A larger roman body face can retain more ink than smaller bold captions;
a fixed stroke threshold across an entire book can make whole pages falsely
bold. Check both typography and paragraph leading when front matter uses a
larger, full-width layout than the main columns. Set paragraph boundaries from
that layout's indentation and line spacing, rather than reusing narrow-column
thresholds. Centered acknowledgments should preserve individual names while
joining wrapped introductory and closing prose into complete paragraphs.

Coalesce fragments of one physical line by baseline and horizontal position
before ordering lines vertically. Tiny baseline differences between words and
ellipsis dots must not reorder a sentence. Column boundaries should prevent
cross-column merging only on pages that actually use those columns; full-width
display text and introductory matter need their own reading-order regions.


### Verify a scan's hidden text layer against the images

Selectable text does not prove complete OCR coverage. A scan may contain clear
prose, captions, and headings while its hidden text layer contains only a stray
label—or nothing—on the same page. Inventory words per page and compare sparse
outliers with rendered pages, including pages dominated by diagrams. Also use
an independent image OCR pass to find missing lines on otherwise populated
pages. Preserve positioned original words where they overlap reliable image
OCR; recover missing regions with their own coordinates and provenance, then
review them in reading order. Exact coverage of the original hidden word stream
alone cannot establish completeness against the printed book.

For three-column books, assign lines to column regions using the actual column
starts, allowing scan drift and hanging list indents. Do not use a boundary
that lies on a column's left edge: small horizontal changes can then send its
first lines into the preceding column. Reconstruct hanging-indent list items
before applying ordinary first-line paragraph indentation rules, and retain
separate text streams for captions, boxed advice, and prose around pictures.


A horizontal rule can itself be OCRed as a line of plausible letters, especially
short repeated fragments such as `a`, `ll`, and `ee`. Rank low-information OCR
rows before paragraph assembly and inspect their image crops. Remove verified
rule/ornament interpretations by source region or positioned word identifiers;
keep real headings immediately below them. A confidence score alone cannot
separate rule hallucinations from text. Do not clean these fragments with a
whole-book word replacement dictionary.

Treat proposed illustration rectangles as candidates until compared with the
scan. A wrong rectangle can both clip artwork and silently remove adjacent prose
from the text stream. Inventory text ownership separately from image coverage,
review every crop, and audit short leftover fragments near every picture. Mask
only verified prose/caption regions; broad rectangular masks can erase sloping
roofs, foundation blocks, diagram labels, and other real artwork beside text.
For a picture that wraps around prose, record its irregular cutouts explicitly
and preserve the entire picture at native resolution. After moving a label or
caption out of the image, check the complete caption and neighboring sentence,
not only the image's appearance.


A heading spanning several columns may start in the second column while the
first column continues an earlier paragraph. Finish the unaffected leading
columns before processing the heading and the columns it actually governs.
Do not turn its vertical position into a page-wide boundary. Likewise, a float
can explain a large gap inside continuous prose, but cannot justify merging
separate fragmentary checklist items across every later line. Check both prose
continuations and unpunctuated lists when changing float-aware paragraph rules.


When reusing cached figure assets, compare the complete current extraction
specification, including caption membership, cutouts, rotation, and source
bounds. A deleted field is a change too: comparing only keys still present can
retain an obsolete caption or mask. Rebuild affected assets and regenerate text
ownership after layout changes, then validate the packaged image hashes and
caption placement together.


Hidden OCR can also duplicate a line or even a partial line at the same image
coordinates. Detect overlapping repeated words before baseline coalescing;
otherwise individually plausible OCR streams can become “Arrange Arrange the
the furniture”. Remove only source-verified duplicates, preserving unique words
in partially overlapping lines. In numbered lists, inspect split multi-digit
markers such as `1 0i` and punctuation misread as a second digit. Recover the
whole marker before deciding paragraph boundaries, and validate the expected
item sequence so a missed label cannot join adjacent columns' instructions.

### Recover complete emphasis blocks, lists, and diagram labels

Word-by-word scan measurements can drop short words inside a uniformly bold
quotation, caption, or emphasis paragraph, and can mistake isolated heavy
letters for italic type. Audit fragmented style runs across the whole book,
including short words and punctuation. Review each candidate against the scan
and recover the complete source span. Retain genuine italic words within bold
text; a majority vote must not erase real emphasis or extend bold over a roman
sentence at the end of the same paragraph. Repeated display quotations need
complete opening/closing marks and ellipses checked as whole units, rather than
normalizing their punctuation word by word.

A boxed or shaded passage can span two columns while ordinary prose above it
continues from the first column into the second. Recover the entire box as one
independent stream, including its heading, introduction, both list columns,
and closing comment. Finish the surrounding prose before inserting the box.
Inspect every edge: a boundary through one text row can leave only some words
of a sentence outside the panel. Reconstruct the row as a unit and audit mixed
body/panel ownership. Compare semantic list counts and item order with the scan;
consecutive styled paragraphs alone do not establish a complete list.

When a list's later elements each have their own source line, give its first
element the same treatment, even if it follows a colon or a column transition.
Do not let a fragmentary final item absorb the next column's prose. Preserve
wrapped lines within an item, combine wrapped heading lines, and keep category
headings outside the list they introduce. Oversized list numerals may have a
baseline far below the first text line; align them to that first line using
geometry before sorting, so they do not drift after the sentence or break it
into two paragraphs. A short heading above a long horizontal rule can govern
several columns even when the title itself is narrow; use the rule's span when
establishing reading-order bands.

Masking prose inside an illustration rectangle must not remove diagram labels.
Audit short masked strings separately: words such as “worry” or “WOOD” inside
a diagram or bottle label belong to the picture. Every confirmed label error
triggers a review of other small internal masks. For scans with tinted paper,
fill removed text areas with sampled local paper colour and opaque pixels.
Transparent cutouts can render black in ebook readers. Keep all unmasked
artwork at native resolution and inspect the packaged assets in a reader.

### OCR period-apostrophe clusters and final-letter confusions

Treat `.'` and `.’` after a word as review candidates, especially without a
matching opening quotation. The pair can be a damaged exclamation mark or
question mark, a genuine closing quote, or a raised note marker. Inventory the
pattern across the whole book and verify the printed glyph; never translate
all occurrences to the same punctuation. The shared punctuation audit flags
these clusters without rewriting them. In ordinary English OCR, apply the
whole-token `Mosi` → `Most` (`mosi` → `most`) default repair; do not change
substrings such as `Mosiac`, and preserve source-verified names or other-language
uses as explicit exceptions.

An oversized numeral may also be fused into the previous line's last word
(`forts.4`, for example), or recognized as two letter-shaped pieces. Compare
independent OCR and the scan, split the text/geometry at the real line boundary,
and restore the numeral to the following item. Do not merely replace the token
in place: its tall bounding box can still reorder both lines. Check the complete
number sequence after recovery. For a shaded panel continued on another page,
exclude prose below the shaded edge and join the continued panel before returning
to that prose; assigning the entire physical page to the panel interleaves
unrelated streams.

When reviewing nested quotations, balance every quotation level. A sentence can
have a legitimate inner single closing quote and still be missing its outer
double closing quote. In particular, flag a paragraph that opens with a double
quote and ends with punctuation plus a single quote while its outer quotation
remains open. Verify the full printed ending, including faint final marks.
Do not dismiss the whole cluster merely because its inner quotation is balanced.

Represent printed bullets as semantic `ul`/`li` markers and remove the literal
bullet and its following source whitespace from the item text. Each item should
begin with its first word, without an ASCII space or non-breaking space before
it; let list layout position the marker. Audit all list items and reader exports
for leading whitespace and duplicated literal bullets, preserving inline styles
when removing the source marker.

Audit complete style spans, including a bold opening followed by a roman tail
in the same paragraph. Reviewing only paragraphs that are mostly bold misses
such openings. Short function words provide weak pixel measurements: recover
their style from reliable words on the same physical line, or from an explicitly
continuous span on both sides, and retain reviewed span boundaries. OCR repair
and dehyphenation can also split formatting inside one word; check the rebuilt
word as a unit. Preserve real italic words inside bold prose and deliberate
changes of style. Do not flatten whole mixed paragraphs to a majority style.

The full rectangle of an instructional panel includes its heading, introductory
text, every list column, diagram, and caption. A rectangle starting at the
picture or lower half of the box silently leaves its upper text in the main
stream. This can insert a heading into a continuing sentence or split a list
around unrelated prose. Check the complete block against the scan and place it
at a safe boundary after the related prose; a user-requested chapter-end position
takes precedence over the introductory-quotation default. Keep a preceding list
of examples before a subsequent checklist, even when the checklist lies below
the first column and the examples occupy the next column. Validate the final
sequence and test the repaired surrounding prose as well as the box itself.

Caption selection must compare all neighboring text, not merely choose the
nearest bold paragraph. A bold body paragraph can resemble a caption while the
real caption is roman in the hidden OCR. Audit unexpectedly distant captions,
verify the source, and reconstruct page-end prose across the separately owned
caption. Image alternative text should use the same cleaned wording as the
visible caption, without raw OCR or print-line hyphenation.

Flag asterisks or carets inside apparent words, including a short space after
the mark, for source review. Such marks can represent a line-end hyphen, a
compound's real hyphen, or a stray stroke from nearby artwork. They can also be
legitimate notes or mathematical notation, so detection must not imply global
removal. Verify whether to join the word, retain a hyphen, or remove an artifact.
Unexpected capitalization within prose likewise needs contextual source review;
do not globally lowercase names or technical terms.

Text completeness does not prove illustration completeness. Compare residual
ink regions against the figure inventory after excluding retained prose,
verified headings, rules, and semantic panels. Small product drawings and signs
can be missed even when every OCR word is accounted for. Review residuals
against the scan and retain lettering belonging to a drawing inside its image.

### Second pass for fragmented emphasis

After dehyphenation, OCR correction, and inline markup generation, make a
second suspicious-formatting pass over the packaged text. Flag every word
whose letters are only partly bold or italic, and every sentence, heading,
or paragraph that is predominantly bold or italic except for a few isolated
words or letter fragments. Check both missing emphasis and stray emphasis;
short function words, first words, and fragments joined across lines or columns
are especially vulnerable. Audit bold and italics independently, including
spurious italics inside bold text. Do not infer correct formatting from a
paragraph's majority style alone: compare the complete span with the scan,
preserve genuine mixed emphasis, and record verified boundaries in the builder.
Examples include a heading with only its last words italicized, a bold sentence
with an unbold initial article, and `du` italicized inside roman `durable`.
Add packaged-output regressions for each confirmed repair.

Include short run-in labels before an em dash in emphasis review, even when
most of the following paragraph is roman; a majority-style paragraph audit
will miss a label such as bold `Painted` followed by unbold `wood`. Review
adjacent entries together, including labels that lost all emphasis. A short
bold label below a drawing may be its caption rather than a subsection title;
confirm its position, attach it to the figure, and exclude it from the crop.

Replace linked print-page references with reader-independent wording such as
`here`, preserving the verified destination. Consume the whole page range,
not just its first number, and handle references in both inline text and tails.
Recheck reader-exported text after changing link labels. Preserve page numbers
that are substantive historical or bibliographic information rather than
navigation instructions.

For skewed scan text, deskew separate text columns before a fresh OCR pass.
Compare that result with the scan and existing transcription; fresh OCR is
additional evidence, not a reason to replace already correct words blindly.
Keep the original illustration pixels, source coordinates, and reviewed styles.
Verify unfamiliar technical identifiers against the source and an authoritative
reference when letter/digit confusion remains; do not guess from OCR shape.

Run the fragmented-emphasis audit after every structural markup rewrite as
well as after initial assembly. Converting literal bullet paragraphs into
semantic lists must reuse the already reviewed inline styles; regenerating
text from raw OCR at that stage can silently reintroduce repaired errors.
Retain source-verified exceptions in the review report, such as a deliberately
roman word within italic prose or a roman introductory label before an italic
sentence. An audit finding is a review candidate, not an automatic correction.

For titles and named works, audit the entire phrase at every occurrence,
including initial articles and short words such as `A`, `The`, `De`, `of`, and
`and`. A correctly italicized occurrence elsewhere does not validate a broken
one. Use capitalization and neighboring italic spans to find candidates, then
verify their full boundaries in the scan; a person's name preceding a title
may correctly remain roman. Accent or apostrophe variants can prevent a reviewed
phrase rule from matching, so flag near-matches as well as checking exact hits.
Restore missing accents only from source evidence, and assert that every
confirmed title occurrence has a continuous emphasis span.

During a final OCR pass, flag angle brackets embedded inside apparent words,
unlikely `ii` clusters, and isolated substitutions such as `ol` in `one ol`.
Also inspect letter-shape confusions that yield valid words, such as `modem`
for `modern` or `bum` for `burn`. These are detection examples, not global
replacement rules: a technical text may genuinely mention a modem, and `bum`
is an ordinary English word. Confirm the context and scan, keep ambiguous
repairs book-specific, use whole-token boundaries where appropriate, and check
that legitimate substrings such as `bump` and `bumps` remain intact.

On pages with prose in one column and an illustration grid in others, review
unclaimed short labels beneath drawings before merging text by reading order.
A caption missing from the figure inventory can otherwise be appended to the
last prose paragraph in another column. Assign caption ownership from the
source geometry and validate that the label occurs only inside its figure.

The fused pronoun phrase `Itis` is repaired to `It is` in the shared OCR layer.
Keep this an exact, whole-token rule and test punctuation boundaries plus
negative examples such as `Otitis`, `arthritis`, and longer names. Do not extend
it into a substring replacement or a general split of every `itis` sequence.

### Emphasis boundaries need negative checks

A mostly styled paragraph audit cannot detect every kind of style leak. Also
flag a single italic word immediately after an em dash when the following prose
is roman, and a bold initial word such as `If`, `It`, or `We` at the start of an
otherwise roman sentence following bold text. Verify these against the scan;
retain real contrastive emphasis and complete italic run-in labels. Test where
emphasis stops as well as where it starts. A numbered entry's description is
not necessarily styled like its number or label.

Short-word fallback must preserve explicit reviewed style decisions and must
not inherit style blindly from a preceding numeral, punctuation, sentence end,
or run-in label. After joining a line-end hyphen, treat the resulting word as a
unit: a short suffix on a new bold line can acquire that line's style even when
it completes the preceding roman word. Use the longer, more informative glyph
fragment and surrounding source evidence, then audit the complete word and
sentence again. Do not fix one partial word by imposing its weakest fragment's
style on the whole word. Keep legitimate internal emphasis when source-verified.

### Reconstruct complete list sequences around illustrations

Inventory every expected number for each list, including numbers detached by
oversized typography or mistaken for punctuation. A printed number may be
missing entirely from OCR even when the entry's label is present. Recover it
from the scan, mark the structural boundary before paragraph assembly, and
verify the complete monotonic sequence. A numbered item with a stray literal
bullet after its number should have one marker; remove the duplicate glyph only
within a confirmed numbered list, preserving its text and reviewed inline styles.

Finish a list before placing unrelated illustrations. When a print spread puts
an illustration for a later section above the continuation of the current list,
move it beside that later section's heading or discussion. Keep diagrams for the
current list together after its final item when that gives the clearest reading
order. Validate both the list's item membership and the neighboring figure IDs;
text coverage and figure counts alone cannot establish correct placement.

### Column fragments and navigation leftovers

Slight scan skew can displace the baselines of adjacent fragments of one line
by a few points. Before treating a short fragment as another column or paragraph,
compare its horizontal gap, vertical overlap, and column gutters with the prior
line. Use a constrained, source-verified joining tolerance that remains below
ordinary interline spacing. Test the rejoined word and its surrounding paragraph.
A styled sentence can also begin midway through one physical line; retain a
verified word-level paragraph boundary instead of requiring a separate OCR row.

Parse whole print-page reference expressions, including comma-separated and
`and`-joined references as well as ranges. Give each distinct destination a
reader-independent link label and check that no residual number remains after
an earlier reference was changed to `here`. Separately flag bare folios or
quotation-glyph OCR masquerading as numbers near headings, without deleting
legitimate numbered content.

The shared OCR layer repairs whole-token `It"s` and `it"s` to `It's` and `it's`.
This is a narrow English contraction repair, not permission to replace double
quotation marks throughout prose. Tests must protect occurrences embedded in
longer tokens.

### Short numeric enumerations and repeated prose

Audit inconsistent comma spacing in prose enumerations such as `Numbers 1,2,
and 3`. The shared spacing repair adds missing spaces only within a sequence
of at least three one- or two-digit integers with an explicit `and` or `or`.
Leave thousands separators, decimal commas, formulas, and code untouched;
broader numeric strings require contextual review.

Search for adjacent repeated phrases as well as duplicated whole paragraphs.
Compare their source coordinates and the scan: repetition may be an extraction
duplicate or an obvious typo already printed in the source. Remove a verified
accidental repetition with a narrow reproducible correction; preserve deliberate
rhetorical repetition. Distinct source lines do not prove intentional repetition.

Review an isolated italic word at a sentence or paragraph opening, especially
beside a large italic heading or list numeral. Style can leak from that nearby
object. Do not flatten the rest of the passage: a later emphasized word may be
genuine. Likewise, an apparent initial `I` beside otherwise parallel checklist
entries may be a misread bullet. Restore one semantic list after verifying its
membership and marker shape against the scan.

A slant detector may classify ordinary initial `W` or `A` glyphs as italic,
producing repeated false openings such as `We're`, `We've`, or `Are`. When one
occurs, audit all short italic openings across the book, including multiword
spans such as `Water is`. Compare each with neighboring source letters; remove
only the falsely styled span, retaining genuine emphasis elsewhere. A valid
italic opening such as `Time` does not justify extending italics into the
following roman `is`.

### Shaded panels, intrusive rules, and interrupted lists

Border strokes and shaded backgrounds can become convincing OCR tokens such as
`I`, `J`, `|`, `^`, or stray punctuation inside an otherwise readable paragraph.
Finding a cluster is a trigger to review the complete panel and its parallel
entries against the scan. Recover words, punctuation, emphasis, and numbered
membership together; do not merely delete every matching character. Ordinary
pronouns, mathematical notation, and genuine punctuation must remain intact.

Audit every isolated italic word in long prose when false emphasis recurs.
Roman `very`, `every`, `way`, and pronouns can acquire false slant scores, while
other occurrences really are emphasized. Keep source-positioned decisions for
each occurrence, including retained genuine emphasis; never remove italics by
word dictionary alone. Review the whole corrected word and adjacent words so a
repair does not leave partial-word styling.

A wrapped line just beyond an image mask can be mistakenly assigned to the
image and disappear from prose. Compare the interrupted sentence with the
source, extend the prose cutout to include the complete final line, regenerate
the image, and prove those word IDs now belong to the prose. Do not merely
insert a second transcription while leaving the same words inside the picture.

A new heading or short list low in one column can precede the continuation of
an earlier paragraph in the next column. Check for fragments stranded after
short entries and complete the earlier paragraph before the new section. For
illustrated numbered instructions, keep one ordered list with each illustration
inside its corresponding item; a figure should not restart the sequence.

The shared OCR layer repairs whole-token `Yoii`/`yoii` to `You`/`you`, with tests
protecting substrings inside longer tokens. Broader word-shape similarities are
review candidates, not automatic spelling changes: `clog` versus `dog`, `toll`
versus `tell`, and `lime` versus `time` can all be legitimate words.

For list numbering, account for both an OCR numeral and a separately extracted
full stop. Adding a full stop to the numeral without consuming its separate
glyph creates forms such as `1.. Fish`. Normalize the verified marker before
paragraph assembly, then check the complete semantic number sequence.

At the end of a pass, inventory prose paragraphs ending with a comma,
hyphen, or function word such as `the`, `and`, or `be`. Inspect the following
blocks even when they start with uppercase text: diagram debris or a displaced
`Before`/`After` label can prevent ordinary lowercase-continuation repair.
Check display titles split across a paragraph and heading as well. Capture
complete diagram labels with their illustration, or associate them explicitly
as captions, instead of letting them interrupt neighboring prose.

OCR punctuation confusion works in both directions: a comma may become a full
stop, and a full stop plus a capitalized next word may become a comma followed
by lowercase text. Review conspicuous run-on clauses against the scan, including
captions. Restore both the punctuation and capitalization when verified; do not
globally replace comma-plus-`if`, which is often grammatical.

A short display list's final entry can absorb prose from the next column even
when the combined paragraph ends normally. Audit short bold/italic prefixes
followed immediately by capitalized roman prose, and compare their coordinates
with the preceding parallel entries. Preserve genuine run-in labels, but give
a verified display item its own block and start the next column's explanation
as a new paragraph; checking paragraph endings alone cannot detect this merge.

For structured web editions, distinguish authored sidebars from website pull
quotes that repeat sentences already in the body. Verify each pull quote against
the complete retained text before omitting a decorative duplicate. Do not remove
unique quotations or authored marginal notes by this heuristic. Preserve a
publisher's substantive textual-correction note separately from the essay, while
omitting unrelated site biography, recommendations, and subscription forms.

A page-wide heading cutoff derived from one column's first baseline can clip
short words in another column whose baseline or glyph centers sit slightly
higher. Derive the retained opening band from the actual glyph-box tops across
all body columns, and audit words excluded immediately above the cutoff. Restore
misclassified words to prose ownership rather than inserting replacement text
while leaving the original excluded. Retained-only text comparisons cannot
prove that excluded words were legitimate exclusions.

`rn` can be read as `m`, yielding valid-looking words such as `comer` for
`corner`. Inventory the whole book when one is found, but verify the uses before
repairing them: `comer` is itself a valid English word, and longer words must not
be altered by substring replacement. Keep reviewed corrections at whole-token
or positioned-word scope when the document's context supports them.

Do not assume an HTML `<br>` is a deliberate authorial line break. Inventory
hard breaks inside prose, especially immediately before emphasized words or
between conditional clauses. Rejoin verified continuous sentences with a
separating space while retaining inline emphasis. Preserve actual verse,
dialogue, addresses, and source-supported display lists; grammar and structure,
not the mere presence of a `<br>` tag, determine the role.
