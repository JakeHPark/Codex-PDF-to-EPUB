# OCR scans and damaged transcriptions

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Conservative page extraction](#conservative-page-extraction)
- [Correction scope and common normalization](#correction-scope-and-common-normalization)
- [Correct very obvious typos in the source](#correct-very-obvious-typos-in-the-source)
- [Verify a scan's hidden text layer against the images](#verify-a-scans-hidden-text-layer-against-the-images)
- [Bleed-through and divider pages](#bleed-through-and-divider-pages)
- [Decorative initials](#decorative-initials)
- [Fused words and digit errors inherited from an OCR ebook](#fused-words-and-digit-errors-inherited-from-an-ocr-ebook)
- [Sentence dashes represented by ordinary hyphens](#sentence-dashes-represented-by-ordinary-hyphens)
- [Orphaned symbols and punctuation clusters](#orphaned-symbols-and-punctuation-clusters)
- [Stray OCR glyphs and contradictory punctuation](#stray-ocr-glyphs-and-contradictory-punctuation)
- [Unmatched brackets and parentheses in OCR](#unmatched-brackets-and-parentheses-in-ocr)
- [Pāli and other scholarly transliterations](#pāli-and-other-scholarly-transliterations)
- [Deskewing and technical identifiers](#deskewing-and-technical-identifiers)
- [Word-shape confusions](#word-shape-confusions)
- [Constrained shared token repairs](#constrained-shared-token-repairs)
- [Accidental repetition](#accidental-repetition)
- [Punctuation clusters and intrusive strokes](#punctuation-clusters-and-intrusive-strokes)

## Conservative page extraction

For each page:

- Remove running heads and isolated printed page numbers.
- Remove form-feed characters.
- retain paragraph-separating blank lines;
- join discretionary hyphens only when the evidence supports it;
- preserve block quotations and deliberate section breaks;
- exclude blank divider pages and reverse-side bleed-through.

Do not preserve a line-end hyphen merely because the fragment resembles a
prefix. `pro-` + `ject`, `pre-` + `cisely`, and `ex-` + `planation` are ordinary
words split for print. Review the reconstructed whole word and the original
pair; retain genuine compounds such as `non-Euclidean` or `post-Freudian`.
Audit the ledger of retained hyphens as well as the removed ones.
At a print wrap, an existing multiword compound can lose its first meaningful
hyphen (`might-` + `have-beens` → `mighthave-beens`). Review the complete compound,
including its remaining hyphens, rather than treating every line-end hyphen as
discretionary. Search all occurrences of the same compound after a repair.

Printed typography can confuse extractors. Drop caps and letter-spaced small capitals may become forms such as `A p pa R e n t ly`. Verify these against the rendered page and repair them explicitly.

Some PDF text layers also leak invisible font-run delimiters as standalone characters. Confirm them against the page image before removing them. For example, an isolated `*` may be an internal italic-run marker rather than a printed ornament; genuine scene breaks usually have a distinct repeated or centered form that should be retained.

A reconstructed scan may combine a faint residual bitmap with synthetic vector
glyphs or other foreground layers. Its largest embedded image can therefore be
an incomplete cover or illustration. Compare the extracted asset with the fully
rendered page before accepting it. When the composition itself is the intended
asset, preserve all layers in a suitably resolved render and record that choice;
native bitmap dimensions alone do not prove completeness.

## Correction scope and common normalization

Use three levels of repair:

1. **General rule:** safe across ordinary prose, such as collapsing repeated whitespace.
2. **Narrow pattern:** safe for a constrained form, such as personal pronouns fused to `have` (`Ihave` → `I have`).
3. **Exact substitution:** required for irregular decorative typography or ambiguous OCR.

Keep exact substitutions visible in a dictionary or correction file. Avoid broad dictionary-based “spell correction”; it can damage names, quotations, dialect, archaic spelling, and technical language.

Low confidence or disagreement between OCR readings triggers source review. It
does not authorize converting a prose word into a mathematical image. Recover
the reading as text; see [the prose/math boundary rules](mathematics.md#keep-prose-out-of-mathematical-assets)
for formula classification and searchability checks.

Track which exact corrections have already been applied when normalizing both
source lines and reconstructed blocks. A replacement that contains its own
search text can grow a second letter, quotation mark or year if applied again.
Apply each reviewed correction once per source occurrence; still check joined
blocks for repairs spanning a physical line break. Verify the resulting complete
phrase, including duplicate punctuation and appended digits.


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

## Correct very obvious typos in the source

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
- unexpected capitals inside a sentence, especially a common pronoun such as
  `It` after a comma or within a subordinate clause. Inventory every occurrence
  across the book when one appears. Check the scan before lowercasing: proper
  names, quotations, and title-case list labels can legitimately contain capitals;
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

## Verify a scan's hidden text layer against the images

Selectable text does not prove complete OCR coverage. A scan may contain clear
prose, captions, and headings while its hidden text layer contains only a stray
label—or nothing—on the same page. Inventory words per page and compare sparse
outliers with rendered pages, including pages dominated by diagrams. Also use
an independent image OCR pass to find missing lines on otherwise populated
pages. Preserve positioned original words where they overlap reliable image
OCR; recover missing regions with their own coordinates and provenance, then
review them in reading order. Exact coverage of the original hidden word stream
alone cannot establish completeness against the printed book.

When parsing hOCR, inventory every text-bearing line class, not only
`ocr_line`. Engines can emit `ocr_header`, `ocr_caption` or `ocr_textfloat`
for substantive headings, note-group labels and ordinary text. Classify those
regions by their source role before exclusion; ignoring a class can lose text
while every retained word still passes coverage checks. Compare segmentation
modes on hanging notes: one mode may turn the entire number column into a
vertical nonsense token, while a region-specific uniform-block pass recovers
the individual labels. Verify the labels and continuations against the scan.

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

### Audit disagreements that resemble valid words or symbols

When comparing independent OCR streams, retain strict-substring disagreements
and large edit-distance disagreements for review. `famine`→`amine` can remove
a substantive letter while leaving a real English word; an entire printed word
can also become a dash, numeral or punctuation. A filter that requires a shared
word stem, skips symbols or accepts any substring can conceal these defects.
Include omitted/mismatched tokens and compare meaningful word coverage as well
as character coverage. Review the source region before applying each repair.

Use a dictionary only to prioritize suspicious tokens, never to auto-correct
names, acronyms or technical vocabulary. Supplement it with context, matched
bracket checks, dates containing letters, and fused pronoun forms. The shared
OCR layer repairs case-sensitive whole-token `Iam` to `I am`; leave `IAM`,
`Iams` and substrings in legitimate words unchanged. A plausible dictionary word
or matching pair of OCR errors does not establish that the scan was recovered.


## Bleed-through and divider pages

OCR can turn faint reverse-side printing or decorative pages into convincing-looking gibberish. A mostly blank page is not necessarily usable text. Compare suspicious output with a page image and exclude it when appropriate.

Do not wait for a reader to find these pages. Before packaging, rank every included OCR page by word count, mean alphabetic-token length, and the proportion of one- or two-letter tokens. Render the outliers, especially pages at chapter ends and before part dividers. Maintain a book-specific set of visually verified blank/bleed-through pages and exclude them before paragraph assembly; never add their gibberish to a cleanup dictionary. Add distinctive OCR fragments from every excluded page to regression tests so a later range change cannot reintroduce them.

## Decorative initials

Large, spaced, or mixed-case opening letters may be extracted as multiple fragments. These irregular forms require source-verified substitutions rather than a broad whitespace rule.

Ordinary capitals, especially italic capitals in titles, can also become detached
from the rest of a word (`A bolitionists`). Audit single capital letters followed
by lowercase fragments throughout the packaged text; corroborate candidates with
source pixels and intact occurrences elsewhere. Do not automatically join them:
articles (`A better argument`), the pronoun `I`, initials and logical symbols
(`X and Y`) are valid separate tokens. Keep repairs occurrence-bound and retain
these valid lookalikes as regression controls.

## Fused words and digit errors inherited from an OCR ebook

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

## Sentence dashes represented by ordinary hyphens

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

## Orphaned symbols and punctuation clusters

Audit the entire packaged text for symbols with no plausible role in their
surrounding prose, including isolated copyright or degree signs, angle brackets,
and clusters such as a full stop followed by a dash and semicolon. Scan noise
can produce ordinary-looking punctuation as well as unusual Unicode characters.
Flag these for source-image review, including occurrences in the middle of a
paragraph; do not inspect only paragraph endings. Include symbols fused to a
word, such as an equals sign or underscore prefixed to an OCR token. A nearby
illustration stroke can contaminate both punctuation and letters; confirm the
whole word in the scan rather than merely stripping its non-letter prefix. Preserve legitimate degrees,
copyright notices, mathematics, note markers and deliberate ornaments. Remove
confirmed artifacts in the reproducible builder and test their full contexts.
An unexpected symbol is an audit trigger, not permission to delete that symbol
globally or assume it is a missing numeric note.
Include both comma-before-stop and stop-before-comma clusters (`person, .`,
`arise. ,`) across inline markup. Resolve them before release; do not treat the
absence of a crash or the generation of an audit file as a successful check.
Inventory degree-like glyphs even after numbers: a French ordinal `3e` can
lose its superscript `e` as `3°`. Preserve genuine angles and temperatures;
recover a verified ordinal with ordinary-letter superscript markup (`3<sup>e</sup>`)
when font support makes a small Unicode glyph ambiguous in the reader.

## Stray OCR glyphs and contradictory punctuation

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

## Unmatched brackets and parentheses in OCR

Audit opening parentheses, square brackets, and braces against their matching
closers across each semantic paragraph or continuous quotation. An unmatched
opener may indicate that OCR misread a closing bracket as a letter, digit, or
punctuation mark; for example, a trailing `j` can be a damaged `)`. Report the
source page and surrounding text, inspect the scan, and repair only the
verified occurrence. Allow reviewed mathematical notation, editorial fragments,
and brackets spanning intentionally separate blocks; do not insert closers or
replace letters globally merely to balance a count.

## Pāli and other scholarly transliterations

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

## Deskewing and technical identifiers

For skewed scan text, deskew separate text columns before a fresh OCR pass.
Compare that result with the scan and existing transcription; fresh OCR is
additional evidence, not a reason to replace already correct words blindly.
Keep the original illustration pixels, source coordinates, and reviewed styles.
Verify unfamiliar technical identifiers against the source and an authoritative
reference when letter/digit confusion remains; do not guess from OCR shape.

## Word-shape confusions

Flag apparent words beginning with a slash, such as `/ocal`, `/ess` or `“/t`,
and words ending abruptly in `]`, such as `If]`. Italic `l` or capital `I`
can be misrecognized as those strokes; a damaged `If I` can become `If]`.
Review the complete word and neighboring text against the source. Preserve
genuine mathematical division, paths, bracketed quotations and citation
closers. These are whole-book detection rules, not global slash or bracket
replacements. A trailing bracket can also be extra ink rather than a missing
pronoun, as in a corrupted `Recall]`.
Also inspect repeated slash strokes within words (`a//` for italic `all`) and
terminal slash strokes (`rea/` for `real`). The shared OCR helper repairs only
the standalone prose `a//` form; broader readings need source review. Audit
asymmetric spaces beside lexical slashes, especially after physical line
joining (`stolen/ hidden` → source-verified `stolen/hidden`). A slash may instead
be a damaged letter, and symmetric verse separators, mathematical division,
paths and URLs must retain their intended spacing. Do not globally delete slash
spaces or turn all slash strokes into letters.

During a final OCR pass, flag angle brackets embedded inside apparent words,
unlikely `ii` clusters, and isolated substitutions such as `ol` in `one ol`.
Also inspect letter-shape confusions that yield valid words, such as `modem`
for `modern` or `bum` for `burn`. These are detection examples, not global
replacement rules: a technical text may genuinely mention a modem, and `bum`
is an ordinary English word. Confirm the context and scan, keep ambiguous
repairs book-specific, use whole-token boundaries where appropriate, and check
that legitimate substrings such as `bump` and `bumps` remain intact.

`rn` can be read as `m`, yielding valid-looking words such as `comer` for
`corner`. Inventory the whole book when one is found, but verify the uses before
repairing them: `comer` is itself a valid English word, and longer words must not
be altered by substring replacement. Keep reviewed corrections at whole-token
or positioned-word scope when the document's context supports them.

## Constrained shared token repairs

For English OCR-derived prose, the shared layer repairs whole-token
`iato`/`Iato` to `into`/`Into` and rejoins `a bolitionist`, `a bolitionists`,
and `a bolitionism` (also with initial `A`). These are narrow defaults with
source-verified exceptions, not general spelling correction or permission to
join arbitrary articles to following words. Protect longer tokens and valid
initials; test both punctuation boundaries and legitimate lookalikes.

The shared OCR layer separates whole-token `asystem`/`Asystem` into
`a system`/`A system`. Protect longer tokens and technical identifiers; this
does not authorize splitting every word that contains `system`.

The fused pronoun phrase `Itis` is repaired to `It is` in the shared OCR layer.
Keep this an exact, whole-token rule and test punctuation boundaries plus
negative examples such as `Otitis`, `arthritis`, and longer names. Do not extend
it into a substring replacement or a general split of every `itis` sequence.

The shared OCR layer repairs whole-token `It"s` and `it"s` to `It's` and `it's`.
This is a narrow English contraction repair, not permission to replace double
quotation marks throughout prose. Tests must protect occurrences embedded in
longer tokens.

The shared OCR layer repairs whole-token `Yoii`/`yoii` to `You`/`you`, with tests
protecting substrings inside longer tokens. Broader word-shape similarities are
review candidates, not automatic spelling changes: `clog` versus `dog`, `toll`
versus `tell`, and `lime` versus `time` can all be legitimate words.

## Accidental repetition

Search for adjacent repeated phrases as well as duplicated whole paragraphs.
Compare their source coordinates and the scan: repetition may be an extraction
duplicate or an obvious typo already printed in the source. Remove a verified
accidental repetition with a narrow reproducible correction; preserve deliberate
rhetorical repetition. Distinct source lines do not prove intentional repetition.

## Punctuation clusters and intrusive strokes

Flag exclamation marks embedded between letters (`Beansta!k`, `mere!y`),
including across inline markup. They can be misread stems of `l` or `i`, but
the source determines the replacement. Keep normal exclamations, factorials,
code and deliberately punctuated names as reviewed exceptions; never globally
replace `!` with a letter. The packaged punctuation audit reports this class.

Treat `.'` and `.’` after a word as review candidates, especially without a
matching opening quotation. The pair can be a damaged exclamation mark or
question mark, a genuine closing quote, or a raised note marker. Inventory the
pattern across the whole book and verify the printed glyph; never translate
all occurrences to the same punctuation. The shared punctuation audit flags
these clusters without rewriting them. In ordinary English OCR, apply the
whole-token `Mosi` → `Most` (`mosi` → `most`) default repair; do not change
substrings such as `Mosiac`, and preserve source-verified names or other-language
uses as explicit exceptions.

Flag asterisks or carets inside apparent words, including a short space after
the mark, for source review. Such marks can represent a line-end hyphen, a
compound's real hyphen, or a stray stroke from nearby artwork. They can also be
legitimate notes or mathematical notation, so detection must not imply global
removal. Verify whether to join the word, retain a hyphen, or remove an artifact.
Unexpected capitalization within prose likewise needs contextual source review;
do not globally lowercase names or technical terms.

OCR punctuation confusion works in both directions: a comma may become a full
stop, and a full stop plus a capitalized next word may become a comma followed
by lowercase text. Review conspicuous run-on clauses against the scan, including
captions. Restore both the punctuation and capitalization when verified; do not
globally replace comma-plus-`if`, which is often grammatical.
