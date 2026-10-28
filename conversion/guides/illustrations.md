# Illustrations, tables, columns, sidebars and panels

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Decorative ornaments and drop caps](#decorative-ornaments-and-drop-caps)
- [Mixed text, tables, graphs, and diagrams](#mixed-text-tables-graphs-and-diagrams)
- [Floating instructional panels and nested exercise lists](#floating-instructional-panels-and-nested-exercise-lists)
- [Sidebar notes are independent text streams](#sidebar-notes-are-independent-text-streams)
- [Illustrated exercise lists and numbered subsection titles](#illustrated-exercise-lists-and-numbered-subsection-titles)
- [Image-led books and designed quotation pages](#image-led-books-and-designed-quotation-pages)
- [Continuous artwork across facing pages](#continuous-artwork-across-facing-pages)
- [Figure labels, captions, and obsolete print directions](#figure-labels-captions-and-obsolete-print-directions)
- [Excess margins around extracted illustrations](#excess-margins-around-extracted-illustrations)
- [Typography and line recovery across layout changes](#typography-and-line-recovery-across-layout-changes)
- [Recover complete emphasis blocks, lists, and diagram labels](#recover-complete-emphasis-blocks-lists-and-diagram-labels)
- [Shaded panels, intrusive rules, and interrupted lists](#shaded-panels-intrusive-rules-and-interrupted-lists)
- [Caption ownership beside prose](#caption-ownership-beside-prose)
- [Panel and caption ownership](#panel-and-caption-ownership)

## Decorative ornaments and drop caps

By default, remove purely decorative book ornaments: ornamental borders,
headpieces, tailpieces, flourishes, repeated divider pictures and similar
images that carry no textual or illustrative meaning. Omit their empty wrappers,
forced page breaks, captions describing only the ornament and unused assets.
Preserve meaningful illustrations, diagrams, authored visual arrangements and
the required minimal cover; do not classify artwork as decorative merely because
it is elaborate. Record the ornament inventory and omissions in the recipe.

Convert drop caps and other ornamental chapter initials into ordinary inline
text. Recover each initial from reliable image alt text, adjacent source text
or reviewed pixels **before** removing its image; join it to the remaining word
without inserting a space, while retaining a real word boundary when the
initial is a standalone word. Remove the decorative float/size styling as well.
Audit every section opening against the source: some initials are supplied only
by the image, some are duplicated by accessible text, and some precede an opening
quotation mark. Preserve the complete word, its surrounding punctuation and any
genuine emphasis, without duplicating the first letter. Test the first sentence
of every affected section and verify that no ornamental image or empty frame
remains in the package or reader output.

## Mixed text, tables, graphs, and diagrams

Inventory every numbered figure and table, every embedded image, and every
continued panel before assembly. Image extraction alone misses tables drawn
with text and ruling lines, vector diagrams, and labels placed over images.
Record each object's source page, bounding rectangle, caption, and reading-order
position. Account for rotated landscape pages and multipage continuations.

Distinguish PDF page rotation, image-placement transforms and native bitmap
orientation. An extracted bitmap may already be upright even when its PDF page
is rotated; applying the page rotation again turns it sideways. Check the actual
pixels, captions and overlaid labels before rotating. Keep folios and running
heads outside the artwork's ownership as well as outside the prose: an otherwise
complete crop can accidentally include a detached page number on a rotated leaf.

Use semantic HTML tables where row/column associations and merged headers can
be reconstructed and checked against the source. For complex statistical tables
or diagrams, a verified high-resolution crop is preferable to guessing cells or
flattening columns into prose. Preserve the entire object, including units,
legends, significance keys, and table notes. Keep a readable caption adjacent
to each responsive inline image; do not hotlink assets. Retain enough resolution
to enlarge dense panels. Document when tables remain images rather than
searchable, accessible HTML tables.

Keep short figures and tables together with their captions when they fit a
reader page, and discourage a break immediately after a caption. Verify this in
a paginated reader; adjacent XHTML elements alone do not prevent an orphaned
caption. Preserve block separators in serialized XHTML too: a caption followed
by a list or table must not fuse with its first item in a reader's text export.
Check the complete exported object, including nested list introductions and
cell boundaries, rather than relying solely on its visual appearance.

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

Font-reported text rectangles may understate visible label ink, especially for
transformed or bold labels in vector diagrams. A crop that includes every text
box can still lose a final letter. Check rendered ink and allow independent
edge padding rather than treating coordinate coverage as proof of completeness.
For a rotated full-page diagram, recover its caption separately and rotate the
artwork into a readable orientation; verify all arrowheads and labels again
in the packaged result. If extra padding would capture the original caption,
remove only that recovered caption on a working copy before making the asset.

Validate object coverage against the inventory, inspect every crop edge for
clipped labels or leaked prose, and check representative narrow and wide objects
in a reader preview. Compare the retained prose separately from captured object
text, so a completeness check cannot quietly excuse missing text as graphics.

Check both ends of a panel against its actual frame and neighboring prose.
Detecting a colored heading does not establish the illustration's top edge:
artwork may begin beside that heading. An oversized bottom can swallow the next
paragraph, while a mixed panel's old prose bounds can become invalid after its
art bounds change. Reconcile text ownership after every boundary repair and
review the actual packaged crops, including mixed text-and-diagram panels.

When an image description is derived from its caption, regenerate that
description after final caption repairs and cross-reference rewrites. Validate
the packaged caption and derived alternative text together so a repaired
measurement or word cannot remain corrupted in the image's accessible text.

## Floating instructional panels and nested exercise lists

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
Do not derive their crop solely from recognized word bounds: OCR can miss a
heading, blank answer lines, a table border, or an entire flowchart column.
Compare the full source page and every crop edge, retaining those non-text
features and labels at the native scan grid. Invalidate cached crops whenever
their source or rectangle changes.

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

## Sidebar notes are independent text streams

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

A framed panel may continue on another physical page without repeating its
title. Inventory these continuations across the whole book: an untitled panel,
a lowercase opening, or a preceding panel ending mid-sentence is a review
candidate. Reassemble the complete panel before inserting surrounding body
prose. Join verified sentence continuations across its parts, preserve each
illustration and its labels in sequence, and retain stable targets for the
original parts. Separate word-ownership and image-count checks can both pass
while the reader still encounters a detached sentence ending or illustration.
Verify the complete grouped panel in a reader, including image fit at a usable
viewport size; a complete working crop alone cannot prove reader presentation.

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

## Illustrated exercise lists and numbered subsection titles

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

## Image-led books and designed quotation pages

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

## Continuous artwork across facing pages

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

## Figure labels, captions, and obsolete print directions

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

## Excess margins around extracted illustrations

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

## Typography and line recovery across layout changes

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

## Recover complete emphasis blocks, lists, and diagram labels

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

## Shaded panels, intrusive rules, and interrupted lists

Border strokes and shaded backgrounds can become convincing OCR tokens such as
`I`, `J`, `|`, `^`, or stray punctuation inside an otherwise readable paragraph.
Finding a cluster is a trigger to review the complete panel and its parallel
entries against the scan. Recover words, punctuation, emphasis, and numbered
membership together; do not merely delete every matching character. Ordinary
pronouns, mathematical notation, and genuine punctuation must remain intact.

A wrapped line just beyond an image mask can be mistakenly assigned to the
image and disappear from prose. Compare the interrupted sentence with the
source, extend the prose cutout to include the complete final line, regenerate
the image, and prove those word IDs now belong to the prose. Do not merely
insert a second transcription while leaving the same words inside the picture.

A page-wide heading cutoff derived from one column's first baseline can clip
short words in another column whose baseline or glyph centers sit slightly
higher. Derive the retained opening band from the actual glyph-box tops across
all body columns, and audit words excluded immediately above the cutoff. Restore
misclassified words to prose ownership rather than inserting replacement text
while leaving the original excluded. Retained-only text comparisons cannot
prove that excluded words were legitimate exclusions.

## Caption ownership beside prose

On pages with prose in one column and an illustration grid in others, review
unclaimed short labels beneath drawings before merging text by reading order.
A caption missing from the figure inventory can otherwise be appended to the
last prose paragraph in another column. Assign caption ownership from the
source geometry and validate that the label occurs only inside its figure.

## Panel and caption ownership

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

A prose sentence mentioning `Figure N.N` is not automatically a caption.
Confirm a caption opening from its position, local type size and complete
paragraph group; do not let a reference in ordinary prose remove that line
from the text stream or expand the adjacent image crop into it.

Caption selection must compare all neighboring text, not merely choose the
nearest bold paragraph. A bold body paragraph can resemble a caption while the
real caption is roman in the hidden OCR. Audit unexpectedly distant captions,
verify the source, and reconstruct page-end prose across the separately owned
caption. Image alternative text should use the same cleaned wording as the
visible caption, without raw OCR or print-line hyphenation.

Text completeness does not prove illustration completeness. Compare residual
ink regions against the figure inventory after excluding retained prose,
verified headings, rules, and semantic panels. Small product drawings and signs
can be missed even when every OCR word is accounted for. Review residuals
against the scan and retain lettering belonging to a drawing inside its image.

### Cropped pages backed by shared spread images

A PDF page can display only part of a larger embedded scan, and facing PDF pages
can reuse the same image with different placement offsets. Inspect the image
placement transform and the page rectangle before extracting it: saving the
entire bitmap can introduce the facing page, while treating its pixels as a
single page can crop the wrong text. Map each verified page/region through the
placement transform to native image pixels. Cache decoded spreads for adjacent
crops, preserve the original resolution, and check the resulting page identity.
For scholarly facsimiles, inspect the outer margins too; line numbers belonging
to the critical apparatus must not be mistaken for disposable whitespace.
