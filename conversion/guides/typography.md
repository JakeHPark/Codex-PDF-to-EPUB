# Emphasis, quotations and punctuation

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Recover source emphasis and digital font semantics](#recover-source-emphasis-and-digital-font-semantics)
- [Recover bold from scans](#recover-bold-from-scans)
- [Symbol-aware comparison and style recovery](#symbol-aware-comparison-and-style-recovery)
- [Second pass for fragmented emphasis](#second-pass-for-fragmented-emphasis)
- [Emphasis boundaries need negative checks](#emphasis-boundaries-need-negative-checks)
- [Parallel list label formatting](#parallel-list-label-formatting)
- [Recover meaningful underlining](#recover-meaningful-underlining)
- [Prefer typographic quotation marks and apostrophes](#prefer-typographic-quotation-marks-and-apostrophes)
- [Repeated quotation marks](#repeated-quotation-marks)
- [Apostrophes versus quotation marks](#apostrophes-versus-quotation-marks)
- [Repairs across inline formatting and profile fields](#repairs-across-inline-formatting-and-profile-fields)
- [Spacing at quotation and emphasis boundaries](#spacing-at-quotation-and-emphasis-boundaries)
- [Language-aware punctuation spacing](#language-aware-punctuation-spacing)
- [Line-end hyphens and sentence dashes](#line-end-hyphens-and-sentence-dashes)

## Recover source emphasis and digital font semantics

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

A reliable digital PDF can also insert extraction-only spaces immediately after
an encoded ligature, producing `ﬁ rst`, `ofﬁ ce` or `conﬂ ict`. Inspect the printed
word and its character positions before normalizing the ligature. Inventory all
such glyph-space boundaries in the work, remove only verified internal spaces,
and expand the actual ligature while retaining its emphasis. Do not promote this
into joining arbitrary short words or ordinary `fi`/`fl` sequences. Validate the
complete words and style stream after line joining; a normalizer that expands
`ﬁ` first can conceal the evidence that the gap came from a single glyph.

When classifying small digits by baseline, exclude whitespace-only spans from
reference-baseline estimates. A PDF may position a separator at the preceding
superscript's height even though the surrounding words remain on the body
baseline. Compare a small digit with its local heading or prose size: a
heading's note marker may be larger than a body marker and exceed a fixed
point-size cutoff. Reconcile both against the note inventory. Otherwise a note
marker or exponent can be misclassified as a
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

For scanned quotations, compare line-level style and spacing before joining
blocks. An italic quotation's short final line can be followed by roman author
commentary at the same left edge, with a gap smaller than normal body-leading
thresholds. Sentence completion plus a sustained italic-to-roman transition
can identify that boundary. Review such transitions throughout the book before
expanding a mostly italic paragraph; otherwise commentary inherits quotation
styling. Exclude bibliography title-to-publisher continuations and genuine
mixed-style sentences from this boundary heuristic.

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

Also audit the first word of an emphasized sentence or clause. A short,
capitalised word can receive a low slant score even when the following run is
clearly italic; reviewing only gaps between two italic neighbors misses it.
Review the preceding roman word against source pixels, and retain roman
introducers before italic titles or selectively emphasized phrases. Store
occurrence-specific positive and negative boundary assertions.

Do not bridge a short word solely because both neighbors are italic. The source
may intentionally use italic labels or contrast words around a roman connective,
such as italic “fourth category” and “lack” around roman “is”. Require glyph or
reviewed span evidence, and check isolated short candidates independently:
roman `A`, `a`, `who` and `is` can score as slanted, while `not`, `are`, `do`
and `all` may carry genuine contrastive emphasis. Keep occurrence-specific
positive and negative decisions, including complete title boundaries.

After application, require complete evidence-page coverage, high weighted token alignment, no leaked private-use markers, semantic `<em>` markup in packaged XHTML, and reader-rendered spot checks covering isolated emphasis, multiword titles, long italic passages, notes, and nearby roman controls. Running heads may be detected in the page image, but they should remain unmatched because the builder removes them before formatting alignment.

Marginal section numbers and ornamental boxes may be inserted into the first prose line by OCR. Remove them using a layout-specific pattern that requires the ornamental delimiter; do not delete ordinary Roman numerals appearing in prose.

For source small-cap lettering, check actual reader support rather than only
retaining `font-variant: small-caps`. Some readers display the underlying
lowercase letters unchanged. When uppercase presentation is required, encode
uppercase letters in the verified spans themselves and remove conflicting
lowercase transforms. Respect inherited spans and parent-owned text tails;
verify all occurrences in packaged text and reader output without capitalizing
neighboring prose or changing unrelated lowercase quotations.

Review scientific letter strings separately from prose: OCR may lowercase
small-cap nucleotide sequences or assign them false italics. Restore their
source-verified letters, case and upright/italic style together; do not infer
case from a word dictionary or treat every capital sequence as a variable.

A superscript reference fused into an italic word's OCR box can corrupt its
slant score. Contractions can likewise defeat a short-word fallback when their
combined letter count exceeds the threshold. Review complete titles and the
last word of emphasized passages, including attached references; separate the
reference geometry where possible or record a source-verified span repair.
Do not extend emphasis into the note number or adjacent roman prose.

Superscript note numerals can merge with a neighboring closing quotation mark
or question mark during OCR. Use the raised ink and character geometry to
separate the marker from ordinary punctuation. A numeric OCR result outside the
expected note range may reflect that merger; review the glyph rather than
silently dropping its link or leaving symbols such as a degree sign in prose.

## Recover bold from scans

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

## Symbol-aware comparison and style recovery

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

## Second pass for fragmented emphasis

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

Scope a short-word style repair to its verified occurrence. Replacing every
literal `a` in a paragraph can style letters inside other words; even a
whole-word replacement can wrongly style the paragraph's other articles.
Use positioned word identifiers or an anchored complete phrase, verify roman
lookalikes elsewhere in the same block, and rerun the packaged audit afterward.

Include short run-in labels before an em dash in emphasis review, even when
most of the following paragraph is roman; a majority-style paragraph audit
will miss a label such as bold `Painted` followed by unbold `wood`. Review
adjacent entries together, including labels that lost all emphasis. A short
bold label below a drawing may be its caption rather than a subsection title;
confirm its position, attach it to the figure, and exclude it from the crop.

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
confirmed title occurrence has a continuous emphasis span. Check final words,
subtitles and parenthetical title extensions as well as short opening words.
Adjacent italic works separated by quotation marks or citation punctuation
need separate spans; do not bridge punctuation merely because both neighboring
words are italic. Keep surrounding author names, publication data and separators
outside the title, and validate the complete title in packaged markup.

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

Audit complete style spans, including a bold opening followed by a roman tail
in the same paragraph. Reviewing only paragraphs that are mostly bold misses
such openings. Short function words provide weak pixel measurements: recover
their style from reliable words on the same physical line, or from an explicitly
continuous span on both sides, and retain reviewed span boundaries. OCR repair
and dehyphenation can also split formatting inside one word; check the rebuilt
word as a unit. Preserve real italic words inside bold prose and deliberate
changes of style. Do not flatten whole mixed paragraphs to a majority style.

When false emphasis recurs, inventory every packaged italic span in body and
notes for source review; a shortlist of frequently misclassified words is not
whole-book coverage. Also inspect missing emphasis independently. Length-based
filters can discard genuine two-letter foreign words, initials, numerals and
variables, and a neighbor-fill rule can miss two consecutive short italic words.
Review complete foreign phrases and titles across physical lines, plus fused
tokens that contain both roman and italic text even when the detector classified
the entire token as roman. Preserve explicitly reviewed roman decisions through
later gap filling, and retain source-supported internal puns as exceptions.
Use the shared `inline_audit.find_emphasis_issues` on final packaged XHTML;
include known complete titles/foreign phrases and review its positive and
negative boundaries. Make new, unresolved findings release-blocking, with
source-positioned exceptions for valid isolated emphasis and roman connectives.
Do not merely generate a candidate report or approve an entire failure class.
When a spelling repair restores letters mistaken for slash strokes, classify
the corrected token length using its original glyph evidence, then audit its
emphasis again. A recovered word must not inherit its damaged spelling's
short-token rejection.

Audit the roman word immediately before each multiword italic run, including
capitalized question openings such as “What’s”, “With” and “When”. A zero slant
score can be a glyph-shape failure, not proof of roman type. Compare the complete
question or expression against the source, and assert both its italic opening
and its roman surroundings. Conversely, italic words on either side of a roman
word do not prove a continuous italic phrase: retain source-verified roman gaps
through span joining and test them explicitly in the final package.

Audit every isolated italic word in long prose when false emphasis recurs.
Roman `very`, `every`, `way`, and pronouns can acquire false slant scores, while
other occurrences really are emphasized. Keep source-positioned decisions for
each occurrence, including retained genuine emphasis; never remove italics by
word dictionary alone. Review the whole corrected word and adjacent words so a
repair does not leave partial-word styling.

A book title can match an ordinary subject term used elsewhere in roman type. Keep source-positioned occurrence identities; do not italicize every matching word sequence globally.

## Emphasis boundaries need negative checks

OCR can fuse text across an em dash into one token despite a change of typeface
(e.g. italic `Perplex` followed by roman `—mostly`). Audit dash-containing
styled tokens throughout body and notes. Review each side against the source,
split its style spans at character boundaries, and test the roman side as well
as the emphasized side. Either side may legitimately carry emphasis; do not
strip or propagate it automatically. Short-word style inference must not cross
a dash without source evidence.

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

## Parallel list label formatting

Audit every list for inconsistent emphasis among parallel entries. Compare the
number, run-in label, and explanatory prose separately; one or two labels in a
different bold/italic style are suspicious even when their words are complete.
Also flag a label whose final word lost its emphasis. Review these outliers
against neighboring source entries, preserving genuine contrasts such as one
italic word inside otherwise roman instructions. Do not make all list prose
uniform merely because its opening labels share a style. Record retained
exceptions as well as repairs, and validate the final packaged list membership
and complete label spans after structural assembly.

## Recover meaningful underlining

When OCR produces underscores in prose, inspect the source for underlining
before deleting them. If the author uses underlining to identify advice or
another meaningful category, recover the complete source-supported underline
spans and their roman boundaries; removing OCR debris alone loses that meaning.
Distinguish printed underlines from handwritten annotations and scan artifacts.

Keep spaces within one continuous source-underlined phrase inside the same
`u` span. Separate per-word tags with roman spaces can leave visible gaps in
mobile readers. Bridge only intervening whitespace between verified underline
runs; never extend underlining across a genuine roman word or punctuation
boundary without source evidence. Check final markup as well as desktop export;
reader-specific rendering needs an actual device check before claiming support.
Printed underlines can also resemble box rules: review apparent panels that
start or end inside prose, and restore complete paragraphs before styling them.

Printed underlining can also obscure letters and defeat both OCR engines.
Inspect emphasized quotations independently, restore missing source words, and
preserve the underline when it carries an explicitly stated editorial distinction.

## Prefer typographic quotation marks and apostrophes

Use typographic quotation marks (`“…”` and `‘…’`) and apostrophes (`’`) by
default in ordinary EPUB prose, including headings, captions, and notes.
Preserve the source's quotation levels and punctuation while replacing straight
ASCII marks where their role is clear. Distinguish contractions, possessives,
and leading elisions such as `’tis` from quotation delimiters; account for
quotations continued across paragraphs. Do not blindly replace or pair every
apostrophe. Preserve literal marks in code, URLs, and other notation, and use
proper prime symbols for measurements or mathematics when the source requires
them. Review ambiguous marks against the source, and check the packaged visible
text across inline emphasis boundaries for mixed or mismatched quote styles.
For positional style assertions, derive the text and style flags together from
the packaged DOM. Internal one-character note placeholders can expand to several
digits, and line-break markers can disappear from visible text; offsets from an
earlier extraction stream may therefore test the wrong character.

Apply prose typography after structural joining, across complete visible blocks,
while preserving inline elements, text/tails, emphasis and links. Check remaining
ASCII marks separately from curly-quotation nesting: the shared nesting detector
does not flag straight prose quotes. Audit the actual packaged text before any
quote-neutral normalization used by older content regressions. Keep inline
contractions contiguous in the audit stream, preserve block/`br` boundaries and
handle linked note digits separately. Model source-verified quotation reopeners
across paragraphs as one continuing quotation; do not invent intermediate closers
or delete repeated openers in the delivered text just to clear an audit.
The packaged audit must include unclosed openers: a wrong single closer after
an ordinary word (`“secondary effects’`) can be classified as an apostrophe,
leaving the double opener as the only detectable defect. Do not suppress all
unclosed findings to accommodate continued quotations. Review those exceptions
individually, with source evidence and exact block fingerprints.
Plural possessives inside a quoted title also need special care: in
`“‘Haddocks’ Eyes.’”`, the mark after `Haddocks` is an apostrophe and the mark
after `Eyes.` closes the inner quotation. A checker that counts the possessive
as that closer can falsely pass a missing final mark. Review capitalized
possessive/title continuations and test both the intact and damaged nesting;
do not globally replace apostrophes or infer closers merely from mark counts.
See the [helper catalog](../common/README.md#quality-detectors-and-package-policy-checks)
for exact detector defaults and limitations.

## Repeated quotation marks

Review complete ellipsis runs across inline markup, not merely adjacent
punctuation pairs. Flag mixed spacing such as `. . ..`, two-dot or excessive
dot runs, and a redundant full stop beside `!` or `?` plus an ellipsis.
Distinguish a three-dot omission from a sentence stop plus three omission dots:
four dots can be intentional. Verify the source and normalize only the damaged
spacing or redundant stop; do not collapse every four-dot sequence to three.
Check every occurrence in the book and assert the repaired full context in
both packaged text and reader export. A clean word comparison cannot catch it.

After normalizing spaced ellipses, check the boundary before a closing quote.
Do not retain an OCR or normalization-inserted space that lets the closing mark
wrap alone onto the next line. Preserve the source dots and quotation nesting;
verify the complete sentence in the reader export and visual rendering.

OCR may duplicate a closing quotation mark, but repeated quote characters can also arise near nested quotations. Do not collapse every doubled quote globally. Verify the source and use an exact or tightly contextual repair, then add a regression assertion for the corrected phrase.

Audit duplicated opening quotes and a quotation beginning with digit `1` followed
by a first-person verb as well as duplicated closers. Check the attribution's
punctuation in context: a quoted statement followed by a speaker tag may need
a comma before the closing quote. When the passage crosses a page or column,
inspect both physical edges for a lost sentence dash before joining the prose.
These are source-review candidates, not global quote, digit, or period repairs.

OCR may also mismatch quotation styles, such as a single opening mark paired with a double closing mark. Compare the phrase with the rendered source page before normalizing it; apostrophes and genuinely nested quotations make global quote substitution unsafe.

Run a stack-based typographic-quotation audit over the complete final packaged
prose, preserving semantic block and line boundaries.
Treat curly opening and closing marks structurally; classify contractions and
possessives before pairing quotation delimiters, and flag mismatched or unclosed marks for page-image review. This distinguishes
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

When reviewing nested quotations, balance every quotation level. A sentence can
have a legitimate inner single closing quote and still be missing its outer
double closing quote. In particular, flag a paragraph that opens with a double
quote and ends with punctuation plus a single quote while its outer quotation
remains open. Verify the full printed ending, including faint final marks.
Do not dismiss the whole cluster merely because its inner quotation is balanced.

## Apostrophes versus quotation marks

Also distinguish measurement marks from quotations. In dimensions such as
`29” wide` or `4’5” tall`, the quote-shaped glyphs denote inches or feet and
must not be deleted as unmatched quotation marks. When their measurement role
is unambiguous, use Unicode primes (`29″`, `4′5″`); otherwise review the context.
Keep compact feet-and-inches notation internally consistent: `5′11″` rather
than `5′ 11″`. Audit spaces between the prime and inch count throughout the
work when one appears. Apply this only to confirmed compound measurements;
ordinary text following a measurement still needs its separating space.

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

## Repairs across inline formatting and profile fields

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

## Spacing at quotation and emphasis boundaries

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

When an apparent ellipsis has more than four dots, first check whether two
source paragraphs were accidentally joined: an ending omission and a new
paragraph's opening omission must not become one run. Recover quotation
paragraph gaps using their own line spacing, rather than the larger body-font
threshold. Normalize verified omission marks consistently while preserving the
distinction between three omission dots and a sentence full stop followed by
three omission dots; keep any following note reference linked.

When a punctuation audit finds definite defects, review the source and repair
them before release. Missing ellipses and closing quotation marks can coexist
with false paragraph breaks, including quotations interrupted by inline
pictures. Rejoin only source-confirmed continuations and preserve the pictures
at their semantic position. Record each exact repair and any obvious source
typo separately; do not dismiss all findings as ambiguous or balance every
quotation globally merely to clear the audit.

## Language-aware punctuation spacing

In ordinary English prose, flag spaces immediately inside opening quotation
marks, immediately before closing quotation marks (`Confusion. ”`), and
before semicolons, colons, question marks and exclamation marks.
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

Audit inconsistent comma spacing in prose enumerations such as `Numbers 1,2,
and 3`. The shared spacing repair adds missing spaces only within a sequence
of at least three one- or two-digit integers with an explicit `and` or `or`.
Leave thousands separators, decimal commas, formulas, and code untouched;
broader numeric strings require contextual review.

## Line-end hyphens and sentence dashes

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

Line-end hyphen handling must include numeric compounds, not only alphabetic
words. A wrapped `42-` followed by `inch` should retain the hyphen without a
space when the source confirms a measurement adjective. Check the reverse
direction too: `mid-` followed by `2000s`, or a citation range `160–` followed by
`67`, must not acquire an internal space. Preserve the original hyphen or range
dash; do not treat either as an alphabetic word split. Do not apply the same
rule to a range or a suspended construction such as `42- and 48-inch`.
Measurements with mixed fractions also need source review: OCR may turn `3½`
into `3 '/2`. Recover a legible Unicode fraction or accurate mathematical form,
retaining the dimension's units and its relationship to neighboring numbers.
