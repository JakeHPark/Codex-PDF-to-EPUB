# Lists, markers and continuations

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Identify lists before paragraphs](#identify-lists-before-paragraphs)
- [Oversized and detached list markers](#oversized-and-detached-list-markers)
- [Semantic bullets and clean item text](#semantic-bullets-and-clean-item-text)
- [Reconstruct complete list sequences around illustrations](#reconstruct-complete-list-sequences-around-illustrations)
- [List continuity across column changes](#list-continuity-across-column-changes)
- [List typography and release checks](#list-typography-and-release-checks)

## Identify lists before paragraphs

Review long merged blocks containing several short label-plus-colon phrases.
They may be independent bullet items whose dots were missed by OCR. Compare
the left marker column and hanging text margins in the scan, recover every
peer item and its complete continuation across page turns, and restore label
emphasis separately. A following label such as `Compensation:` belongs to a
new item when the source shows a new bullet; a preceding italic sentence is
not evidence that the next label belongs in the same paragraph. Use this as
a review trigger, not a rule to split every colon in prose.

Do not require colons or visible bullets to detect a list. A short run of
parallel, capitalized fragments on separate baselines, especially italic and
more deeply indented beneath an existing item, can be an unmarked sublist.
Keep each complete example separate and attach the group to its governing
item; do not flatten it into a quotation paragraph or split the outer list
around it. Preserve the absence of printed markers with an unmarked nested
list when appropriate. Audit other short, nonterminal lines followed by a
capital at the same indent, but retain ordinary wraps before names, titles,
initials and the pronoun `I` as source-reviewed controls.

Do not infer a quotation from the hanging indent of a list item. Before
classifying indented prose as a blockquote, identify source bullet/number
markers and their complete wrapped items. Group consecutive peers in one
semantic list and retain only source-supported nesting. Audit every packaged
list's ancestor chain: a mixture of direct items and individually blockquoted
items creates inconsistent reader indents even when their text is correct.
Likewise, indentation alone must not attach ordinary following prose to the
last item; verify item continuations and the list's closing boundary.

A hanging list can place every continuation line beyond the ordinary paragraph
indent threshold. Measure continuation from the item's text margin, separately
from its numeral, or retain verified item-region ownership; otherwise every
physical line may become a paragraph and leave word fragments such as a line-end
hyphen followed by a detached suffix. Check the final item-to-prose transition
across page turns as well as the numbered starts. A four-digit year followed by
a full stop is normally sentence text, not a list marker: constrain ordinal
detection and source-check digit-initial paragraph splits.
Empty physical-page anchors between consecutive items do not end their semantic
list. Skip such anchors when grouping peers, and preserve their correct source
ownership when moving an item into the shared list.

Recognize numbered and bulleted lists before ordinary paragraph indentation.
A hanging item's continuation lines are indented relative to its number; they
are not fresh paragraphs. Join wrapped words and sentences within each item,
start a new item only at a verified marker, and preserve continuations across
physical pages. Emit semantic lists with distinct items. Check the entire list
sequence in the packaged EPUB and reader export, including long items crossing
pages. Do not mistake endnotes, equation numbers, or years for list markers.

A parenthesized publication year at the start of a wrapped line is not a list
marker. Require a plausible item sequence and source indentation before
creating an ordered list; never let `(1970)` or `(1974)` split a continuous
bibliographic sentence. Validate each list's complete values and separately
assert that publication years remain visible in the surrounding prose. Reader
exports may omit generated list numbers, concealing an accidental year-as-item
conversion even when an intermediate text comparison passes.

## Oversized and detached list markers

A genuine numbered list need not print a full stop after each number. Confirm
its sequence and geometry rather than requiring `1.` as the only marker form.
Some numbered entries use ordinary first-line paragraph indents with unindented
continuations instead of hanging indents. Derive the item's continuation edge
from the source; do not use its indented opening label as that edge. Validate
the complete item and the return to ordinary prose in both cases.

An oversized numeral may also be fused into the previous line's last word
(`forts.4`, for example), or recognized as two letter-shaped pieces. Compare
independent OCR and the scan, split the text/geometry at the real line boundary,
and restore the numeral to the following item. Do not merely replace the token
in place: its tall bounding box can still reorder both lines. Check the complete
number sequence after recovery. For a shaded panel continued on another page,
exclude prose below the shaded edge and join the continued panel before returning
to that prose; assigning the entire physical page to the panel interleaves
unrelated streams.

A detached ordinal can be recognized as a short prose word (such as `Be` for
`3.`), or sorted to the top of the page independently of its item. Review tiny
standalone OCR regions and numeric tails on complete sentences against marker
positions and baselines. Restore the marker to its source item before paragraph
assembly; do not guess its owner from extraction order. Reconcile every printed
ordinal with its item opening, including absent middle entries, and compare the
actual source values rather than testing only a consecutive generated sequence.
Keep later paragraphs inside their verified item and stop at the return to prose.

For list numbering, account for both an OCR numeral and a separately extracted
full stop. Adding a full stop to the numeral without consuming its separate
glyph creates forms such as `1.. Fish`. Normalize the verified marker before
paragraph assembly, then check the complete semantic number sequence.

When a numbered opening uses separate spans for the marker and drop cap, check
the complete visible text after flattening that display typography. Retain an
explicit space between the closing marker and first word, such as `(1.) After`.
Audit every numbered remark for a marker touching a letter; inline span counts
and word-only text comparisons cannot detect this missing separator.

## Semantic bullets and clean item text

Represent printed bullets as semantic `ul`/`li` markers and remove the literal
bullet and its following source whitespace from the item text. Each item should
begin with its first word, without an ASCII space or non-breaking space before
it; let list layout position the marker. Audit all list items and reader exports
for leading whitespace and duplicated literal bullets, preserving inline styles
when removing the source marker.

## Reconstruct complete list sequences around illustrations

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

## List continuity across column changes

A new heading or short list low in one column can precede the continuation of
an earlier paragraph in the next column. Check for fragments stranded after
short entries and complete the earlier paragraph before the new section. For
illustrated numbered instructions, keep one ordered list with each illustration
inside its corresponding item; a figure should not restart the sequence.

A short display list's final entry can absorb prose from the next column even
when the combined paragraph ends normally. Audit short bold/italic prefixes
followed immediately by capitalized roman prose, and compare their coordinates
with the preceding parallel entries. Preserve genuine run-in labels, but give
a verified display item its own block and start the next column's explanation
as a new paragraph; checking paragraph endings alone cannot detect this merge.

## List typography and release checks

Review numbers, labels and explanatory prose independently using [parallel list label formatting](typography.md#parallel-list-label-formatting). Verify complete source membership, original values, nesting, continuations and figure ownership in both packaged XHTML and reader export; a generated consecutive sequence or text count alone cannot prove a list correct.
