# Mathematical source recovery and rendering

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Mathematical expressions and equation images](#mathematical-expressions-and-equation-images)
  - [Keep prose out of mathematical assets](#keep-prose-out-of-mathematical-assets)

## Mathematical expressions and equation images

Do not flatten two-dimensional notation into text. Binomial coefficients need
vertically stacked entries, fractions need their numerator and denominator,
and sums, integrals, matrices, accents, and scripts need their original
relationships. Use semantic text with emphasis and superscript/subscript markup
for simple notation when the source glyphs and baselines can be verified.
Treat mathematical powers, isotope numbers, and note references as distinct
roles; a raised digit is not sufficient evidence for a note link.
Repeated logical variables may be mapped to ordinary text fonts or OCRed as
`Xi`, `Yi`, or `Z:` when the source has `X₁`, `Y₁`, `Z₁`. Verify the entire
parallel series and script baselines, including roman digit shapes. Preserve
italic variable letters without leaking emphasis into intervening prose such
as `and`. A short-word style bridge between two variables is not evidence that
the connector is emphasized; inspect these boundaries independently.
Check both positive and negative style boundaries throughout a reviewed
expression. Verifying that `X` and `Y` are italic does not detect a leaked
italic `was` in `either X or Y was the case`. Source-review the surrounding
prose, reset false emphasis there, and test the complete expression's roman
words as well as its variables. Preserve independently authored nearby emphasis.

### Keep prose out of mathematical assets

Prefer readable, searchable text for inline notation. The cost of incorrectly
turning prose into an image is higher than leaving simple notation as text:
when classification is uncertain, keep the text and flag its reading for review.
Recognizing mathematics does not itself justify rasterizing it. Expressions
such as `log p`, `H(p)`, `A_i/A`, simple equalities and inequalities, and short
variable sequences normally need only text, Unicode symbols and semantic
subscript/superscript markup. A report about an artifact is not a request to change mathematical notation.
Preserve a requested stacked expression and repair its rendering, using isolated
source glyphs/rules when reader CSS is unreliable.
A short inline fraction can use an unambiguous linear form such as `1/(1−t)`
when stacked CSS renders unreliably in EPUB readers. Parenthesize the complete
denominator and preserve variable emphasis; `1/1−t` changes the meaning. Do not
use this fallback to flatten matrices, binomial coefficients or complex
multilevel notation. Check both the visible reader result and exported text.
Use images only when source relationships cannot
be represented faithfully with the available semantic rendering. Preserve
necessary fractions and stacked coefficients; this preference does not permit
discarding an uncertain script or flattening a genuinely two-dimensional object.

Do not turn a word into a formula image because its OCR confidence is low,
its spelling is absent from a dictionary, or two OCR engines disagree. Collate
those readings against the source and retain reviewed prose as text. An image
fallback must resolve a verified mathematical construction, not conceal an
unresolved transcription. When removing an overbroad image fallback, review
the newly exposed OCR too: an image may have hidden a misread variable, such
as `7` for italic `T` or `n`, or a missing script numerator. Restore the correct
semantic glyph or complete expression from the source before release.
Italics, descenders and a low bounding-box edge alone
are insufficient: ordinary italic words such as “of”, “by” and “for” can resemble
subscripted notation. Apply this restraint to roman text and names too.

Identify prose and structural roles before classifying mathematical shapes.
Do not propagate a prose role to every line in an OCR paragraph: the same OCR
group can include a neighboring equation's numerator, denominator or radical.
Use the actual line's geometry and content when delimiting display crops. Check
for mathematical fragments left outside each crop as well as ink touching its
edges; an entirely omitted denominator can leave a deceptively clean white
edge. Conversely, keep an adjacent short prose continuation outside the image.
Parenthesized item labels such as `(1)` and `(2)`, the pronoun “I”, years,
chapter references and ordinals such as “19th” remain text. Raised ordinal
suffixes are typography, not equation scripts. Strip a list marker before
grouping adjacent mathematics, so the first variable cannot absorb the marker
and duplicate its number. A scanned vertical stroke may be “I”, “1”, a variable
or a conditional-probability bar; decide from source and context.
This also applies to appendix letters in references such as “Appendix F” and
“Appendix W”, and figure-panel or enumerated labels such as `(b)`. Classify
their structural role before inspecting the letter's mathematical appearance.
Include these labels in negative image-selection regressions. Review slash-like
OCR readings in mathematical prose too: `/7` may be an italic `H`; punctuation
inside `A;/A` or `H(+)` may hide a script or fraction. Check the complete source
expression and recover it as text where possible, rather than imaging the
malformed OCR or trusting its literal punctuation.

Classify the complete expression using source symbols, relationships and
context. Protect ordinary words from geometric heuristics without treating
every dictionary entry as prose: `Pr`, `dS`, `log` and genuine scripted variables
can be mathematical. Use semantic italic text for verified standalone variables;
retain native mathematics where scripts or two-dimensional relationships require
it. A reviewed inseparable mathematical passage may remain a source image, but
record its location and reduced searchability explicitly. When prose and
notation can be source-collated, reconstruct the prose and isolate the true
expression rather than making the whole sentence an image. An override created by
a fragment-merging heuristic is not reviewed evidence: tiny OCR rows can be
duplicate descenders, dots or quotation strokes from ordinary prose. Verify the
source ink before forcing their neighboring words into a math asset.

An OCR word box can truncate an unfamiliar Greek letter even when its recognized
text looks plausible. Inspect a padded source region and the complete connected
glyph before using a crop for transcription, style measurement or a matching
prototype. A clipped rho or sigma can resemble an unrelated Latin stroke and
poison later matches. Calibrate with complete positive glyphs and ordinary Latin
words/numerals as negative controls; review proposed readings in context, with
scripts and adjacent punctuation accounted for separately.

Inventory the source tokens assigned to every inline math asset. Audit common
prose words, unexpected asset counts and formulas containing whole sentences.
Assert that reviewed prose remains text in both the packaged EPUB and reader
export; a crop displaying the right word does not pass this check. Regression
cases must include italic prose with descenders and low OCR confidence, alongside
real subscripts, function names and unknown technical terms. Inspect both
positive math selections and ordinary words that must stay outside them.

Render equation images with black ink on solid white backgrounds by default.
This minimal presentation remains legible when the reader uses a black page
background, without requiring automatic image recolouring or theme detection.
Transparency alone does not make fixed black pixels follow the reader's text
colour. Apply the background to the actual raster or SVG asset, rather than
relying solely on CSS that a reader may ignore. Preserve original ink geometry,
resolution and antialiasing; inspect the packaged images on both light and dark
backgrounds. Semantic notation should continue to inherit ordinary text colour.
Do not recolour photographs, covers or arbitrary illustrations under this rule.

Audit complete parenthesized variable tuples and probability distributions: a
recognized opening fence or initial letter does not prove that the closing
fence, intervening letters, ellipsis, subscripts or fraction entries survived.
Review stray degree signs and question marks after numerical bases as possible
misread exponents; preserve real angles, temperatures and degree notation.

### Recover complete native expressions

For complex digital-PDF formulas that cannot be reconstructed faithfully as
semantic mathematics, preserve isolated source glyph outlines in SVG with black
ink and a white background rectangle. Select the actual glyph occurrences and
necessary fraction/overbar rules;
do not crop a whole page's SVG or include neighboring prose. Verify that every
selected visible glyph is present. Math-extension fonts often report ordinary
text boxes for tall brackets or operators: measure the transformed glyph
outlines to determine the true image bounds, and leave a small safety margin.
Use those same ink bounds when associating raised and lowered pieces with a
prose baseline. Otherwise a fraction can be separated from its sentence or a
stacked coefficient can lose its lower entry. Do not group solely by the PDF's
text blocks: one expression may occupy many blocks and one block may contain
both prose and a formula.

Recognize bibliography years and citation suffixes before grouping parenthesized
mathematics: `(2017a, 2017b)` is a citation, not a variable tuple. Commas and
alphabetic suffixes alone cannot distinguish these roles. Group complete
source-supported expressions without allowing a greedy neighboring run to
swallow an already reviewed semantic expression.

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

In scans, a faint lower stroke can turn `±` into `+` in OCR. Review signed
measurements, tolerances, deviations and modulation extents against the pixels,
including standalone signs and signs fused to a number. After finding this
failure, inventory every extracted plus sign throughout the book and check for
other damaged representations of the same source symbol. Restore verified
`±` as semantic text. Preserve genuine addition and positive-value signs, and
source-written `+/−` notation; numerical context alone does not authorize
replacing `+`. Regressions must cover both the repaired values and valid plus
signs, and verify the lower stroke in the rebuilt reader rendering.

Inspect overlaid text glyphs as well as drawn rules for accents and bars.
A roman macron and mathematical letter can have nearly identical origins,
although extraction emits them as separate adjacent characters. Preserve them
as one outlined expression; for a verified Planck-constant construction,
recover `ℏ` as a single semantic symbol. Never leave a detached bar beside an
italic h. Check all occurrences of the same glyph construction.

Keep punctuation belonging to the surrounding sentence outside inline math
assets, including a following comma, colon, semicolon, or full stop. Preserve
punctuation internal to mathematical expressions. Formula images must use black
ink on solid white backgrounds and must scale with surrounding text; check their baseline,
size, complete fences, and scripts in a reader preview. Audit all instances of
a discovered failure, not only the reported example. Include stacked
coefficients, inline fractions beside prose, labeled proof steps, large
operators, and neighboring punctuation in visual regression checks. Document
that outlined formulas retain appearance but are not searchable semantic math.

For scanned mathematics, OCR word boxes are an incomplete inventory: an entire
denominator, operator, equation label or unnumbered schematic may be absent.
Recover the full source band before narrowing its bounds against visible ink.
Then audit the actual packaged crop rectangles against independently reflowed
words. Exclusive OCR-token ownership alone cannot detect prose duplicated
inside an expanded image. Resolve every overlap by recovering the inline
expression or, when reliable separation is impossible, preserving one complete
source passage and documenting its reduced searchability. Never clip unseen
formula components merely to eliminate an overlap.
Do not remove an equation number by narrowing a whole multiline crop to the
number's horizontal position: an earlier line can extend farther right. Keep
the number in the native image unless its removal preserves every line's ink.
Review unexpected copyright or trademark symbols in mathematical prose against
the scan before deleting them. OCR can mistake an infinity sign, omega or a
raised variable for such a mark; recover the complete expression's source ink.
Clamp raster crops to the decoded image dimensions before padding or alpha
extraction. Rounded PDF-to-pixel coordinates can exceed the raster by one pixel;
some image libraries fill that overflow with black, creating a false vertical
rule and forcing the real equation to shrink to fit an almost page-wide asset.
Check unusually narrow inline glyph boxes too: a correctly transcribed zero can
have a box covering only its right stroke, so its raster crop resembles a closing
parenthesis. Confirm the complete ink and distinguish lookalikes such as zero
and omega before choosing a wider source crop or verified semantic glyph.

A tiny detached OCR row can also be ordinary text, a reference's final page
number, or a closing quotation mark. Associate it with its actual source
baseline, including short continuation rows; the nearest long prose row can
belong to the preceding line. Keep bibliography continuations outside generic
script-merging heuristics. When sorting blocks spanning physical pages, use
the first page's position, not the smallest vertical coordinate across all
their pages.

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
expressions may require vector renders with black ink and a white background,
with sentence punctuation
outside the asset. Track native and outlined expressions together so every
source expression appears exactly once, including headings, captions, tables
and notes. Check accessible labels independently; do not label a correctly
rendered range with an annotation that omitted its separator.

### Source recovery and conservative native mathematics

A digital PDF can display an equation correctly while its text mapping emits
control characters, private-use characters, replacement characters, or the
wrong ordinary letter. Inspect embedded glyph names and positioned text traces
before trusting extracted Unicode. A symbol-font override must match the actual
glyph identity as well as its font; the same font can supply spaces and ordinary
punctuation. Replacing every character in that font can duplicate a recovered
symbol and delete its separating space. Check the complete surrounding phrase
and the recovered symbol’s occurrence count in both XHTML and the reader. Recover a Unicode symbol only when the
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
| Prose misclassified as mathematics | Ordinary words become images because they are italic, have descenders, have low OCR confidence or are absent from a dictionary. | Review the source reading as text; require independent mathematical evidence; inventory asset source tokens and verify prose searchability in the final EPUB and reader export. |
| Sentence punctuation absorbed | A trailing comma, colon, semicolon, or full stop enters the formula image. | Classify punctuation by sentence role, keep external punctuation as text, and preserve genuine internal formula punctuation. |
| Font-run typography or spacing damaged | Decimal dots become emphasized, words touch formula edges, or spacing is inserted inside words. | Check packaged decimal spans and whole-formula edge gaps; preserve verified source separators and avoid inference from font family alone. |
| Background or neighboring ink obscures notation | Transparent black ink disappears on a dark page, or a whole-page SVG leaks nearby prose. | Use isolated black notation on an actual white asset background; exclude unrelated glyphs and inspect against both light and dark reader backgrounds. |
| Formula scaled or aligned incorrectly | Inline math sits too high/low, is much larger than prose, or a display overflows the viewport. | Size inline assets relative to body text, derive alignment from the source baseline and full ink bounds, and preview both inline and displayed formulas at reader widths. |
| Coverage checks pass despite corrupt structure | All characters exist somewhere, but an upper entry is in prose, a fraction is split, or citation digits are reordered. | Track exclusive source-character ownership and expected formula groups/roles; add complete-expression and reading-order checks plus source-to-reader visual comparison. A display must interrupt the prose at its source position: keep a following “where…” definition after the display, rather than merging it into the introduction and delaying the formula. |
| Extracted alt text mistaken for accessible math | An outlined formula looks correct but its raw text map has scrambled order or unknown symbols. | Do not call that map a verified transcription; provide accessible mathematical text only after reconstruction and review, and document the limitations of outlined formulas. |

### Release checks for mathematical content

Maintain a book-specific inventory of source formula locations, selected glyph
identities, drawn rules, inline/display roles, and surrounding prose. Require
every retained visible source character to have exactly one accounted role;
reconcile source equation labels independently. Verbose formulas such as
`H(location and momentum)` can exceed a prose-length heuristic while remaining
a displayed equation. Verify their full regions and labels, rather than leaving
function descriptions and isolated operators scattered through prose.
Document intentional semantic replacement of markers and composite symbols.
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
check, glyph count, correct background, or text export alone is never
sufficient evidence that mathematical rendering is correct.

Inventory unnumbered diagrams too. Search for substantial vector paths and
visible image placements outside the numbered figure/table and equation
inventory, then review each candidate against its source page. An image
resource listed in the PDF is not proof that a visible illustration appears
on that page.
