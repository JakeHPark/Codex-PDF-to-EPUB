# Source selection and edition recovery

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Prefer a complete structured web edition when available](#prefer-a-complete-structured-web-edition-when-available)
- [Use a secondary transcription as a reference](#use-a-secondary-transcription-as-a-reference)
- [Auditing a recovered scan against a secondary transcription](#auditing-a-recovered-scan-against-a-secondary-transcription)
- [Distinguish edition cuts from missing OCR lines](#distinguish-edition-cuts-from-missing-ocr-lines)
- [Cleaning an existing EPUB with numbered remarks or arguments](#cleaning-an-existing-epub-with-numbered-remarks-or-arguments)
- [Loose text and notes in malformed HTML](#loose-text-and-notes-in-malformed-html)
- [Publisher EPUB tables in auxiliary documents](#publisher-epub-tables-in-auxiliary-documents)
- [Outlined text in PDFs](#outlined-text-in-pdfs)
- [Academic papers and positioned objects](#academic-papers-and-positioned-objects)
- [Website pull quotes and publisher corrections](#website-pull-quotes-and-publisher-corrections)

## Prefer a complete structured web edition when available

Before starting OCR, check whether the user has supplied—or an authoritative
source offers—a complete HTML edition. Prefer that structured text when its
chapter coverage and provenance can be verified. Record the source URL and
inventory every chapter before building so a partial web mirror is never
mistaken for the whole book.

Check publication metadata against the versioned record and matching PDF.
A regenerated scholarly HTML edition can evaluate a dynamic source command
such as TeX's `\today` again, displaying its conversion date as if it were the
paper's date. Preserve the requested version and verified publication/document
date; do not silently update the edition from a renderer's timestamp. Keep
submission dates distinct from a date explicitly printed on the paper.

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

A saved HTML edition may replace every illustration with an identical broken-image
or security-warning icon while retaining useful image positions and captions.
If the user supplies a matching PDF with intact illustrations, inventory the
real images there and map them to the HTML by surrounding prose, caption and
panel order. Recover original embedded assets when complete, preserving their
resolution and encoding. Do not package warning icons or mistake a site logo
for an article figure. Rebuild malformed image/caption groups and note links,
then verify every recovered image and caption against both source reading orders.
For a multi-panel sequence, preserve its sequence and grouping while keeping
individual panels legible and preventing captions from becoming stranded.

Recover meaningful source CSS classes as well as inline tags. A scholarly
repository may mark whole quotations as italic using a class, and encode a
numbered list as an unstyled `ul` with literal label spans. Reconstruct those
roles explicitly so dropping website CSS does not lose emphasis or introduce
bullets beside the printed numbers. Compare reference typography with the
published PDF when the repository's citation markup has lost title emphasis
or reordered bibliographic fields.

Check CSS overrides before equating tag names with visible emphasis. A `font`
shorthand declaration can reset an `em` element to roman while changing only
its face or size; another class can make an ordinary span italic. Recover the
verified presentation and semantic role together, normalize site-specific font
choices, and retain the style evidence. Do not introduce italics solely because
an imported tag is named `em`, or discard real italics when removing site CSS.

Validation for HTML-derived EPUBs must prove that every expected chapter was
included, every local image reference resolves and appears in the manifest,
no remote image URL remains, and every content image renders inline with its
caption in a representative reader export or preview.

## Use a secondary transcription as a reference

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

## Auditing a recovered scan against a secondary transcription

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

## Distinguish edition cuts from missing OCR lines

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

## Cleaning an existing EPUB with numbered remarks or arguments

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

## Loose text and notes in malformed HTML

When a note entry has no working call, inspect raw anchor attributes as well as
the parsed links. An unclosed attribute quote can swallow the intended `href`
into an anchor name. Repair only when the source location, surrounding note
sequence and entry establish the association; do not invent a call to balance
the counts.

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

Apply the same inventory to body prose around layout tables. A table nested in
an invalid paragraph can cause the HTML parser to close the paragraph early,
leaving its continuation in the table's tail before an empty paragraph. Identify
whether the table contains real tabular data, verse, or layout gutters; recover
its semantic content and the following prose separately. Reconcile the complete
source region, including tails, rather than only its paragraph descendants.

## Publisher EPUB tables in auxiliary documents

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

Even a searchable auxiliary table can omit a cell-internal line break and fuse
separate entries. Compare its visible entries with the table image; inspect
lowercase-to-uppercase joins within individual text nodes while preserving real
names such as `LinkedIn`. Distinguish missing breaks from existing `br` elements:
flattened text alone makes both look fused. Restore verified entry boundaries
in the semantic cell, and check the complete cell in a reader export.

When auditing punctuation in readable text, account for linked superscript
citations separately. Flattening a closing quotation mark directly against a
reference digit can make a valid quotation resemble an apostrophe inside a
word. Ignore the citation's digit for quotation classification, or insert an
audit-only separator around it; preserve the actual superscript and link in
the EPUB. Do not delete or rewrite the quotation to silence this false flag.

## Outlined text in PDFs

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

## Academic papers and positioned objects

Preserve a paper's title, author, version/date, publication or working-paper
identifier, abstract, classification codes, and authored acknowledgments.
Separate institutional boilerplate and postal/contact details from substantive
front matter. Preserve numbered section/subsection hierarchy in both content
and navigation, and keep footnotes distinct from bibliographic references.

A structured web edition can contain damaged bibliography strings even when
its prose is clean: duplicated DOI fields, fused years and journal names, or
reordered author/title fields. Compare flagged references with the matching
published PDF. Recover complete references and their emphasis from that edition,
then rebuild local citation targets and return links. Rejoin DOI fragments using
the complete identifier as independent evidence; do not apply prose hyphen
removal or generic spacing substitutions to identifiers. Verify each reference's
text, numbering, italic titles and links separately from the main prose.

A saved journal page may retain a table number and caption with only “view
inline” or “view popup” links, leaving the actual cells out of the file. Zero
`table` elements does not establish that the article has no tables. Inventory
numbered object wrappers and in-text calls, recover the cells from the linked
document or a matching structured edition, and verify headers, values, spans
and table notes against the published source before placing them inline.

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

## Website pull quotes and publisher corrections

For structured web editions, distinguish authored sidebars from website pull
quotes that repeat sentences already in the body. Verify each pull quote against
the complete retained text before omitting a decorative duplicate. Do not remove
unique quotations or authored marginal notes by this heuristic. Preserve a
publisher's substantive textual-correction note separately from the essay, while
omitting unrelated site biography, recommendations, and subscription forms.
