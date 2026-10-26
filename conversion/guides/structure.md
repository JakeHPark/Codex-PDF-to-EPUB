# Reading order, paragraphs, headings and notes

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Inspect all source regions](#inspect-all-source-regions)
- [Section map and shared-page boundaries](#section-map-and-shared-page-boundaries)
- [Keep physical line evidence independent of joined text](#keep-physical-line-evidence-independent-of-joined-text)
- [Wide justification gaps mistaken for paragraph breaks](#wide-justification-gaps-mistaken-for-paragraph-breaks)
- [Column fragments and scan skew](#column-fragments-and-scan-skew)
- [Paragraph continuity](#paragraph-continuity)
- [Stranded fragments after reconstruction](#stranded-fragments-after-reconstruction)
- [Meaningful versus print-only hard breaks](#meaningful-versus-print-only-hard-breaks)
- [Parallel textual witnesses in scholarly editions](#parallel-textual-witnesses-in-scholarly-editions)
- [Semantic XHTML and inherited styles](#semantic-xhtml-and-inherited-styles)
- [Preserve substantive front matter](#preserve-substantive-front-matter)
- [Generated versus extracted headings](#generated-versus-extracted-headings)
- [Dialogue, inscriptions and secondary headings](#dialogue-inscriptions-and-secondary-headings)
- [Publication credits and bibliographic entries](#publication-credits-and-bibliographic-entries)
- [Footnotes and endnotes](#footnotes-and-endnotes)
- [Stranded footnote-marker punctuation](#stranded-footnote-marker-punctuation)
- [Superscript numeric endnotes misread as symbols](#superscript-numeric-endnotes-misread-as-symbols)
- [Note markers inside headings](#note-markers-inside-headings)
- [Running-head variants absorbed into prose](#running-head-variants-absorbed-into-prose)
- [Print indexes in reflowable EPUBs](#print-indexes-in-reflowable-epubs)
- [Print references and navigation leftovers](#print-references-and-navigation-leftovers)
- [Soft line breaks in structured tables](#soft-line-breaks-in-structured-tables)

## Inspect all source regions

Before building anything:

- Run `pdfinfo` to determine page count, metadata, and whether the PDF contains text.
- Extract representative pages with `pdftotext -layout`.
- Render suspicious pages to images when text order, notes, headings, or bleed-through are ambiguous.
- Identify front matter, chapter openings, part dividers, notes, bibliography, and index.
- Record physical PDF page numbers separately from printed page numbers.

Do not infer every boundary from a table of contents. Locate the actual heading on the actual PDF page.

## Section map and shared-page boundaries

Store each section as an identifier, title, inclusive PDF-page range, and hierarchy level. For example:

```python
SECTIONS = [
    ("chapter-one", "I. Chapter One", 10, 24, 1),
    ("chapter-two", "II. Chapter Two", 25, 39, 1),
]
```

Check every transition page visually or from layout-preserving text. A chapter can begin halfway through a PDF page. In that case, split at the heading rather than assigning the complete page to either neighboring chapter.

A digitally generated PDF may itself be a printout of an imperfect plaintext
transcription. A single monospaced font does not preserve the printed book's
italics, small capitals, or paragraph structure. When a matching published scan
is available, align it chapter by chapter as a reference for typography and
verified omissions; retain the supplied edition's legitimate spelling and
wording rather than replacing its prose wholesale with another edition's OCR.
Check the contents against both bodies: two complete chapters can be transposed
in a transcription even when all titles are present. Correct their order only
when independent edition evidence establishes it.

OCR XML leaf numbers and an exported scan PDF's physical page numbers can differ
because a cover or placeholder leaf was omitted. Verify the mapping at the
beginning, middle, and end before using OCR coordinates for source crops or
style evidence. Store the PDF page separately and inspect the rendered text;
a plausible OCR match on one leaf does not prove that the corresponding crop
shows the same passage.

Treat page ranges as search bounds, not ownership boundaries. Extract each physical page once, locate every printed heading with an explicit book-specific pattern, then give the text before that heading to the preceding section and the text after it to the new section. Generate the EPUB heading separately and discard the matched printed heading. `conversion/common/section_boundaries.py` implements this shared-page rule and deliberately fails when an expected heading cannot be found; do not fall back to removing everything before the first blank line. That fallback silently strands sentence continuations and duplicates headings.

After changing one boundary, audit all later boundaries. A single mistaken offset often becomes progressive drift, causing each later chapter to lose its opening and inherit the next chapter’s heading.

## Keep physical line evidence independent of joined text

Joining a discretionary hyphen must not change the original line's bounding
rectangle. Removing the continuation token and then recalculating that line's
left edge can make an ordinary continuation appear indented, creating false
paragraphs throughout a book. Retain the original physical line geometry and
use a separate character map for the joined text. Infer the body margin robustly
from ordinary full-width lines, allowing for page skew; a single dust speck at
the extreme left must not define the margin. Audit both unusually short
paragraphs and runs of lowercase continuations after reconstruction.

Do not classify short ordinary words as mathematics merely because they occupy
a separate PDF text line. Fragments such as “In” can share the surrounding
prose baseline and should be merged before equation detection. Keep mathematical
operator names distinct. Decimal points in a math font do not require emphasis:
retain the number as continuous text and audit against forms such as
`0<em>.</em>7` in the packaged output.

## Wide justification gaps mistaken for paragraph breaks

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

## Column fragments and scan skew

Slight scan skew can displace the baselines of adjacent fragments of one line
by a few points. Before treating a short fragment as another column or paragraph,
compare its horizontal gap, vertical overlap, and column gutters with the prior
line. Use a constrained, source-verified joining tolerance that remains below
ordinary interline spacing. Test the rejoined word and its surrounding paragraph.
A styled sentence can also begin midway through one physical line; retain a
verified word-level paragraph boundary instead of requiring a separate OCR row.

## Paragraph continuity

For scans, use physical baselines and the local line leading as additional
paragraph evidence. Ascenders, descenders, superscripts and page skew make OCR
rectangle gaps unreliable: a visibly separated, unindented paragraph may have
almost no gap between its extracted boxes. Audit nonterminal block endings,
including uppercase continuations and transitions between prose and quotation
roles. A quoted list can use ordinary-size type and unpunctuated numerals;
recognize its marker and continuation margins before treating every indented
line as a fresh paragraph. Check short, wrapped subheadings separately from
long prose lines rather than requiring one fixed gap or stroke threshold.

Inset arguments and syllogisms may contain several complete propositions, each
wrapping onto a hanging continuation line. Join each complete proposition,
retain a separate block for the next one, and keep the following prose lead-in
and displayed symbolic proportion distinct. Neither an indented first line nor
a hanging continuation alone determines the extent of the inset argument.

Inset quotations can dominate a page. Do not estimate the body margin from the
median of all long lines: enough inset lines can shift it inward and turn quoted
paragraphs into body prose. Establish the outer text measure from verified
full-width lines and neighboring pages, then identify each quotation as a region
before splitting its paragraphs. Dialogue indentation belongs inside that region;
a short final line and a page boundary do not end the quotation. A short final
italic word followed by a longer roman citation can also have a low italic
percentage. Preserve that whole ending with the quotation; line-level majority
style must not move it into the following prose. Review every
prose/quotation role change inside an unfinished sentence and compare all pages
whose margin estimate changes materially under a full-width-line cross-check.

A drop capital can indent several continuation lines. Review every such opening
against the page before accepting an indent as a paragraph boundary; restoring
the missing capital alone does not fix the structure. Keep one reviewed mapping
for drop-cap continuations, including explicit exceptions where a genuine new
paragraph begins alongside the capital. Check complete opening paragraphs and
line-end hyphen joins in the packaged EPUB and reader export.

Check leading punctuation before measuring an OCR line's indent from its first
recognized word. Missed ellipsis dots or quotation marks can make an ordinary
wrapped continuation appear indented. Inspect the ink at the apparent left
margin before creating a new paragraph or block quotation; retain the whole
source quotation and its citation in their verified structure.

A paragraph can end with a parenthetical citation whose final character is `)`,
with no following full stop. Treat that as a possible complete boundary, not
automatic evidence of a column/page continuation. Check source paragraph spacing
and the next opening before joining; retain a negative regression beside genuine
continuations that cross the same column or page boundary.

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

OCR-derived line heights can vary within one printed block quotation because
of capitals, punctuation, or inconsistent hidden font sizes. Recover a sustained
inset stream from its left edge, baseline spacing, and surrounding lines rather
than one exact height threshold. Audit short lowercase blocks and successive
inset lines classified as ordinary paragraphs; reconstruct the whole quotation
before deciding its genuine internal paragraph boundaries.

## Stranded fragments after reconstruction

At the end of a pass, inventory prose paragraphs ending with a comma,
hyphen, or function word such as `the`, `and`, or `be`. Inspect the following
blocks even when they start with uppercase text: diagram debris or a displaced
`Before`/`After` label can prevent ordinary lowercase-continuation repair.
Check display titles split across a paragraph and heading as well. Capture
complete diagram labels with their illustration, or associate them explicitly
as captions, instead of letting them interrupt neighboring prose.

## Meaningful versus print-only hard breaks

An imported HTML container named `poem` or a preformatted wrapper can contain
ordinary prose copied from a plain-text edition. Classify its complete contents
before preserving its line breaks: recover paragraphs from verified blank-line
boundaries, retain actual verse extracts, and separate explanatory notes from
the interrupted prose stream. A container's name alone does not establish verse.

Do not assume an HTML `<br>` is a deliberate authorial line break. Inventory
hard breaks inside prose, especially immediately before emphasized words or
between conditional clauses. Rejoin verified continuous sentences with a
separating space while retaining inline emphasis. Preserve actual verse,
dialogue, addresses, and source-supported display lists; grammar and structure,
not the mere presence of a `<br>` tag, determine the role.

## Parallel textual witnesses in scholarly editions

Verify volume numbers on printed title pages before ordering files; filenames
can be reversed. Inventory each source-language text, translation, supplementary
witness and apparatus separately. A page can contain two translations of the
same numbered passage. Repeated section numbers establish parallel witnesses,
not duplicate extraction.

Recover each witness as a continuous stream across pages. Its next page may
begin with an unnumbered continuation well before the next numbered paragraph.
Locate the first line of the witness from source spacing, typography and the
preceding page's unfinished sentence; do not split only at paragraph numbers,
at a fixed page height, or at the largest gap. Some pages may contain only one
witness even within an otherwise parallel run. Small note panels can occur
between streams, so classify those panels independently before paragraph joining.
Check both streams' paragraph-number sequences and sentence continuations.

When making a translation-only reading edition, remove the parallel source
texts by stream or verified region, not by script detection across the book.
Keep distinct translated witnesses, translated fragments, English commentary
and notes; quoted source-language terms within that commentary are a separate
editorial role. Check mixed-language appendices region by region. Repoint note
links to the retained notes, rebuild navigation and the manifest, and confirm
that removed facsimiles are absent from the archive. Small English note panels
can occur near the top of a short page: exclude a generated title by its actual
identity, never by a blanket upper-page cutoff. Record omitted textual apparatus
and any retained image-based English material in the edition description.

When original-language text or critical apparatus is preserved as facsimiles,
keep its marginal line numbers, sigla, variant readings and reference system.
Link the reading text to the corresponding original pages and state which
material remains image-based and therefore lacks searchable text. Preserve a
print index when explicitly requested; retained original-page anchors make its
pagination usable alongside the reflowed text.

An internal subheading within the first witness can create the same vertical
gap as the start of the second witness. Check both sides of every proposed
boundary against the page and its continuations; a plausible spacing threshold
alone cannot establish ownership. Include numbered paragraphs with OCR-damaged
final punctuation in structural audits, so a comma misread for a full stop does
not merge several numbered sections into one paragraph.

## Semantic XHTML and inherited styles

For lists, read [the list reconstruction guide](lists.md) before interpreting indents or grouping items.

Navigation lists should not add an automatic ordinal before a chapter label
that already contains its printed number. Use semantic nested lists with
appropriate list styling, while retaining actual list numbering in body content.
Inspect the visible contents as well as the reader's navigation panel.

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

HTML `blockquote` elements sometimes serve only as print-size wrappers around
bibliographies or entire quotation anthologies. Classify their contents before
copying the tag: retain reading lists as lists/sections, and group independent
extracts separately with their own attributions. Preserve paragraphs within a
single continuing quotation. Preserve the source’s choice of inline versus
separately displayed attributions rather than imposing one style throughout.
Keep a separate attribution beside the final lines
of its extract with modest relative spacing and a break-before avoidance rule;
do not force a long quotation to stay on one reader page. Check verse stored in
plain paragraphs as well as explicitly marked poetry: recover verified lineation
without treating ordinary source-wrapped prose as verse.

A hidden OCR row can combine a quotation's final word with an attribution
printed on a different baseline. Split the two from source coordinates; retain
both streams and their styles. Removing an apparent duplicate attribution must
not remove its only surviving occurrence. Reconcile source attributions with
the packaged reading stream separately from quotation text coverage.

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

## Preserve substantive front matter

Do not apply a blanket "remove front matter" rule to a whole book. Omit publisher advertisements, series lists, copyright/imprint pages, and blank
leaves when they are not part of the reading experience. Preserve authored
forewords, prefaces, introductions, prologues, and other substantive opening
sections, and put them in the book's original reading order before the main
chapters. Distinguish a standalone introduction in the preliminary pages from
a numbered Introduction that is already a main chapter; include both when the
source contains both. Check the contents page and the PDF pages themselves
before setting the extraction start page. Record explicitly which preliminary
sections were retained and which publisher matter was omitted.

When a compact dedication shares one source page, keep its introductory words,
dedicatee names, connecting words and explanatory paragraphs in one semantic
dedication group. Names are normally styled paragraphs, not separate chapter
headings or navigation entries. Use `break-inside: avoid` with the compatible
`page-break-inside: avoid` on the group; avoid oversized margins that force a
split. Verify that the complete dedication stays together in a paginated reader
export. Preserve reflow and allow an unavoidable split on very small screens
or at large font sizes rather than shrinking or clipping the text.

## Generated versus extracted headings

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

Join wrapped heading lines when matching fonts, consecutive baselines, and
heading structure show that they form one title. Use the joined title in both
body and navigation; do not join a following numbered heading or Notes label.

## Dialogue, inscriptions and secondary headings

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

## Publication credits and bibliographic entries

A chapter-opening publication or permissions credit below a separator rule is
paratext. Keep it in a distinct credit block near the chapter opening, and
remove it from the main prose stream before joining pages. Otherwise it can
split an unfinished sentence at the bottom of the opening page. Inventory and
verify every chapter's credit separator rather than applying a blanket bottom
margin cutoff, which could discard actual prose. Preserve chapter bylines too;
they must not be discarded with the generated chapter title.

Determine quotation margins from sustained inset lines, since a PDF block
can contain both ordinary prose and a quotation. Reconstruct quotation
paragraphs relative to that inset. Audit every paragraph ending in a line-wrap
hyphen and review the next block; a lowercase continuation should not remain
stranded because indentation changed. Bibliographies may distinguish entries
by a modest extra baseline gap while every line shares the same left margin.
Do not treat every left-aligned reference line as a new citation. Verify the
source entry spacing and join wrapped publication names and words within each
entry before applying hanging-indent styling.

A repeated-author rule may disappear from OCR while its year survives farther
right. On pages dominated by these entries, continuation lines can become the
apparent left margin. Identify entry starts from the source rule, author/year
pattern and spacing together; do not split every hanging continuation. Review
uppercase title continuations and city/publisher lines as well as lowercase
fragments. Preserve repeated-author rules explicitly in the rebuilt references.

Numeric-only lines can be ordinary citation continuations, such as a volume
number and page range. Classify them from their font, baseline, left edge,
and entry spacing before equation detection. Never attach their digits to a
nearby author name. Audit the whole bibliography when one such fragment is
found; test complete citations and page ranges, since character-presence
checks can pass even when those characters occur in the wrong order.

## Footnotes and endnotes

Never leave a printed footnote embedded between ordinary prose paragraphs.

Chapter-opening pages can carry a symbolic note attached to the title, byline,
contributor biography or ordinary prose. Inventory asterisks and other symbols
separately from each chapter’s numeric sequence. Do not disable note-region
detection on pages with large headings: a numeral-only pattern or a chapter-open
exemption can leave a small `*See …` citation in the body. Inspect low-position
small-type regions and match every symbolic call to its actual note. Retain it as a
linked note or visible editorial aside; do not absorb it into the contributor’s
biography or omit it while stripping the displayed heading. Validate symbolic
references and numbered references independently, including their return links.
Run `inline_audit.find_unlinked_note_candidates` on the final package and resolve
all findings, while retaining separate source-region completeness checks.

Detect note markers and note text while page structure is still available. Associate each note with its chapter and render it in a predictable location. Chapter-end notes are acceptable when page-local placement cannot be represented reliably.

Allow long, multi-paragraph notes to flow across reader pages. Keep the label
with the opening paragraph rather than applying `break-inside: avoid` to the
entire note. An oversized keep-together group can strand the Notes heading or
leave excessive blank space even when every word survives a text export.

In scanned books, a note can begin with a short or separately extracted line,
or continue from the previous page before the next numbered entry. Expand the
verified small-type region to its actual first baseline; do not start it at the
first sufficiently long line or the first recognizable numeral. Reconcile the
call and entry streams independently across page boundaries. A comma followed
by digits in a quantity is not evidence of a raised note number: verify its
baseline and the corresponding entry before turning it into a link.

Keep punctuation adjacent to a superscript reference separate from the marker
itself. A source may print a colon after a note call, for example
`Sen’s⁷: even …`. When replacing an OCR marker and its neighboring characters,
retain that colon rather than consuming it with the damaged marker. Inventory
punctuation-bearing marker replacements across the work and verify them against
the source; both the packaged text and reader export must preserve the sentence's
punctuation before and after the reference.

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

For scholarly citation ranges, inventory both the visible marker and its full
membership: `4–10` cites seven entries even when the source links the whole
range only to entry 4. Preserve the compact marker and its verified destination,
but associate every included entry with that occurrence for coverage and return
links. Keep comma/range separators at the same raised level as citation numerals;
remove layout-only gaps within the citation cluster without changing neighboring
prose spacing.

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

## Stranded footnote-marker punctuation

Superscript note symbols may be OCRed as punctuation such as `!`, or as a combination such as `*!`. If later cleanup removes only the asterisk, it can leave a bizarre sentence ending such as `.!`. Confirm the source marker and preserve its note text, then remove the entire body marker before general punctuation cleanup. Scan the packaged EPUB for the stranded signature as a regression check.

Numeric endnotes can also be OCRed as an ASCII or curly apostrophe, with or without an asterisk: `denaturing.'*`, `attached.’`, and genuine closing quotation marks can all look deceptively similar in plain text. Textual shape alone must never decide whether such a mark is punctuation or a note. Before stripping symbols, inventory every sentence-final apostrophe-like candidate across the whole body. For each candidate, use its stored word box and baseline position, render a high-resolution crop, run digit-only OCR at several crop widths, and reconcile the result with the chapter's verified note-entry sequence (allowing repeated reference occurrences) and the corresponding notes entry. Record every reviewed decision under the book-specific `tmp/` material, including whether a genuine closing quotation mark must remain. Support multiple recovered markers on one page without relying on the page number as a unique key.

A matching numeric suffix is insufficient: `1640` is not necessarily a call to
note 40, and list item `12.` is not a call to note 2. Require raised glyph or
baseline evidence, preserve the complete ordinary number, and include years and
list labels as negative controls. If a line-end word is joined across a hyphen,
transfer any reference attached to its continuation into the reconstructed word.
Reconcile reference locations and surrounding punctuation as well as counts.

Convert confirmed markers to the same semantic linked-superscript form as other numeric notes. Treat unconfirmed marks as punctuation candidates and resolve them from the rendered source and sentence context; do not globally delete ASCII or curly apostrophes after full stops. Add packaged-XHTML checks for all reviewed cases, for leaked raw marker clusters, for every note target, and for the expected whole-book reference count.

## Superscript numeric endnotes misread as symbols

Raised endnote digits can be OCRed as ordinary symbols such as `®`, `°`, or `©`. Finding even one is a whole-book audit trigger, not permission to patch only the reported sentence. Inventory every occurrence of those glyphs in body XHTML and in the page-level OCR, excluding verified legitimate uses such as a copyright notice in front matter.

Do not globally translate any one symbol into a digit: the same glyph may be legitimate elsewhere, and different raised digits can collapse to similar OCR output. Recover each occurrence from layout evidence. Re-render the affected page at high resolution, use the stored word bounding box to crop the right edge of the token, run digit-only OCR over several crop widths, and check the candidate against the verified note-entry sequence (allowing repeated reference occurrences) and the corresponding entry in the notes section. Crops that are too wide can absorb the word's final letter and invent a leading `1`, so retain the votes and the reviewed selection as book-specific evidence under `tmp/`.

Remove the entire OCR marker cluster, including false leading digits, quote shapes, asterisks, or question marks, while preserving genuine sentence punctuation and verified closing quotation marks. Represent the restored marker semantically as a linked superscript, for example `<a epub:type="noteref" href="notes.xhtml#note-id"><sup>9</sup></a>`, with a stable destination in the visible notes chapter. Validate every fragment target in packaged XHTML and confirm that reader text export retains the digit.

Make this release-blocking: all packaged XHTML—not only the main body—must contain zero unresolved `°`, `®`, or `©` marker glyphs (apart from individually verified legitimate uses), zero leaked internal placeholders, and the expected number of recovered `<sup>` references. Also inspect reader-exported text, because page-bottom bleed-through in the notes can be joined to a valid note on the following page and evade body-only checks. When a glyph class is discovered late, rebuild and rerun the check across the entire book rather than adding a single contextual exception.

## Note markers inside headings

A heading can contain a note reference in the middle of its wording. Retain
that reference and destination in the content heading, but omit the note digit
from its navigation label. Derive the label from a clone and remove only the
reference's text: preserve the removed element's tail (the words following the
marker) by attaching it to its preceding sibling or parent text. Deleting the
whole element without preserving its tail can silently truncate a chapter
title. Check the complete title around a middle-of-heading reference, as well
as the forward and return note links.

Generate labels from the final semantic heading, after multiline joining and
note linking. `conversion/common/navigation.py:heading_label` omits only
explicit note-reference elements and preserves their following text. Audit
every packaged contents entry against its target heading, excluding those
references; do not strip trailing digits with a regular expression, since
years, numbered figures and other genuine title numbers must survive.

## Running-head variants absorbed into prose

Running heads may be extracted at a physical page boundary and then joined into a continuing paragraph. Recognizers must tolerate folio variants such as `405` and `407.`, typographic apostrophe variants, and every running title actually used by the book. After conversion, scan body chapters (excluding the contents, notes, and index) for a page number followed by a known running title. When one failure is found, audit all chapters because the same incomplete header rule usually affects many pages.

Do not remove every line above a fixed vertical cutoff. Scan drift can put a
real first body line inside that band or a running head below it. Identify the
head by its content and layout, then check the first retained body line on every
page. Audit removed ornament tokens separately: a short indented word such as
“Many,” “This,” or “Was” is not decorative merely because it occupies the same
horizontal position as an ornament elsewhere.

A running-head cutoff must leave the highest genuine body line intact in each
column. Font rectangles may extend above the visible ink, and top baselines can
vary by a few points across pages. Inventory excluded lines near the cutoff and
compare an independent extraction before accepting a fixed top margin; otherwise
whole, fluent continuation lines can disappear while all retained-text checks pass.

## Print indexes in reflowable EPUBs

Omit a print index by default when its page-number references have no usable
destinations in the EPUB, especially when it would be retained only as scanned
images. A searchable ebook does not need a nonfunctional reproduction of print
page references. Remove the index from the reproducible builder, navigation,
spine, manifest, and packaged assets; do not merely hide its contents with CSS.
Record the omission and verify that no index document, image, or dangling link
remains in the finished EPUB.

When retaining an index, reject numeric-only entry labels for review. Wrapped
page references can appear as independent rows, including rows sharing a baseline
with a neighboring entry. Reconstruct each column by position, attach numeric
continuations to their verified entry, and check the resulting labels as well as
their link destinations. Derive column membership from headings as well as
indented entries: a threshold fitted only to entry text can place right-column
headings in the left column. Assert the category owning each group of entries.
A resolving hyperlink does not prove a valid label or category.

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

Reconstruct index columns in source reading order and distinguish entry starts,
subentry starts, and their hanging continuations from verified indentation
levels. A PDF block's minimum left edge is not a reliable entry boundary.
Preserve subentry indentation in the EPUB and check transitions between columns
and pages, especially where one subentry continues at the next column's top. Do not
attach characters from whitespace-only PDF lines to nearby text. Sorting those
spacer characters by horizontal position can insert spaces inside valid words.

## Print references and navigation leftovers

Parse whole print-page reference expressions, including comma-separated and
`and`-joined references as well as ranges. Give each distinct destination a
reader-independent link label and check that no residual number remains after
an earlier reference was changed to `here`. Separately flag bare folios or
quotation-glyph OCR masquerading as numbers near headings, without deleting
legitimate numbered content.

Replace linked print-page references with reader-independent wording such as
`here`, preserving the verified destination. Consume the whole page range,
not just its first number, and handle references in both inline text and tails.
Recheck reader-exported text after changing link labels. Preserve page numbers
that are substantive historical or bibliographic information rather than
navigation instructions.

Establish which work a page citation belongs to before linking it. A quoted
author's `p. 207` does not become a reference to this book merely because this
book also has a page 207. Require evidence of an internal navigation instruction
or a verified index destination; preserve external citation numbers as text.

## Soft line breaks in structured tables

HTML table cells may use `br` solely to wrap a name or phrase for print, for
example `Beauclerk or<br/>Beauclerc` or `Cal'dron not<br/>Cauldron`. When the
lineation has no semantic role, replace that break with an ordinary space while
preserving adjacent emphasis and text. Readers, copy/export paths, and text
extractors can otherwise concatenate the words when they flatten the cell.
Keep meaningful lineation in verse, addresses and comparable structured text.
Validate table phrases with whitespace collapsed to one space, not removed
entirely: a character-only comparison cannot detect `orBeauclerc`. Check both
packaged cell text and reader-exported text for the full separated phrase.
