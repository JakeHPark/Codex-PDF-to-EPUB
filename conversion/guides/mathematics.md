# Mathematical source recovery and rendering

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Mathematical expressions and equation images](#mathematical-expressions-and-equation-images)

## Mathematical expressions and equation images

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

### Structured mathematics and annotations

A structured scholarly web edition can supply both presentation MathML and a
TeX annotation for the same expression. They are not guaranteed to agree:
annotations may omit words such as “to” inside a range, retain stray dollar
signs, or differ from an unparsed MathML construction. Inventory every expression
and compare suspect representations with the matching version's rendered PDF.
Use the representation that demonstrably retains the complete expression;
never render all annotations blindly because the prose HTML is clean.

Presentation MathML itself can misclassify sentence punctuation as a script
inside a denominator. Review unexpected primes and trailing punctuation against
the published page, including their vertical position. Move verified sentence
punctuation outside the formula and retain it in the surrounding text; do not
globally remove primes, which may be genuine notation.

For verified simple notation, semantic text with real subscripts/superscripts
can retain searchability. Normalize mathematical Unicode alphabet variants only
when their italic/bold/function roles are separately preserved. Complex
expressions may require transparent vector renders, with sentence punctuation
outside the asset. Track native and outlined expressions together so every
source expression appears exactly once, including headings, captions, tables
and notes. Check accessible labels independently; do not label a correctly
rendered range with an annotation that omitted its separator.

### Source recovery and conservative native mathematics

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

### Inventory of mathematical rendering failures found in this project

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

### Release checks for mathematical content

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
