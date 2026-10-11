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

## Recommended project layout

```text
project/
├── Source Book.pdf
├── AGENTS.md
├── conversion/
│   ├── source-book/
│   │   ├── build_epub.py
│   │   ├── validate_epub.py
│   │   ├── corrections.json       # optional book-specific substitutions
│   │   ├── extracted-pages/       # optional retained diagnostic text
│   │   └── build/                 # disposable unpacked EPUB tree
│   └── validate_all.py
└── output/
    └── epub/
        └── Source Book.epub
```

Use `tmp/` only for disposable renderings, text exports, and experiments. Builders, validators, correction data, and this manual are durable project assets and should live outside `tmp/` in future conversions.

The builders for the books already in this project currently remain under `tmp/pdfs/`; move them only as a deliberate refactor because their path calculations depend on their present location.

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

Pay special attention to:

- fused words (`selfknowledge`, `Ihave`);
- false hyphenation at line or page breaks;
- spaces around em dashes;
- zero/O and one/I confusion;
- missing punctuation at page boundaries;
- OCR fragments from illustrations or verso bleed-through;
- headers inserted into prose.

### 6. Generate semantic EPUB XHTML

Each navigable section should normally have:

- one generated `<h1>`;
- body paragraphs as `<p>`;
- quotations as `<blockquote>`;
- deliberate scene breaks as a semantic or styled divider;
- stable identifiers for notes and links.

If the builder generates a chapter heading from the section map, remove the extracted printed heading from the body. Otherwise readers see a duplicated heading.

Part-title pages should contain the part heading only. Do not retain OCR from blank facing pages, ornamental backgrounds, or show-through text.

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

### Bleed-through and divider pages

OCR can turn faint reverse-side printing or decorative pages into convincing-looking gibberish. A mostly blank page is not necessarily usable text. Compare suspicious output with a page image and exclude it when appropriate.

### Decorative initials

Large, spaced, or mixed-case opening letters may be extracted as multiple fragments. These irregular forms require source-verified substitutions rather than a broad whitespace rule.

### Generated versus extracted headings

If a chapter title is generated from metadata, strip the printed title from extracted body text. Check that it appears exactly once in a reader export.

### Cascading section-boundary drift

An incorrect start page can place a new chapter’s heading and opening paragraph at the end of the previous EPUB section, while the new section begins in mid-sentence or mid-word. Audit all downstream boundaries whenever one such error is found.

### Invisible notes

Semantically marked EPUB footnotes may be hidden or treated as popups by some readers. For notes that must remain visibly readable, use normal block elements with explicit CSS and retain semantic relationships only where reader behavior has been tested.

### Repeated quotation marks

OCR may duplicate a closing quotation mark, but repeated quote characters can also arise near nested quotations. Do not collapse every doubled quote globally. Verify the source and use an exact or tightly contextual repair, then add a regression assertion for the corrected phrase.

OCR may also mismatch quotation styles, such as a single opening mark paired with a double closing mark. Compare the phrase with the rendered source page before normalizing it; apostrophes and genuinely nested quotations make global quote substitution unsafe.

### Stranded footnote-marker punctuation

Superscript note symbols may be OCRed as punctuation such as `!`, or as a combination such as `*!`. If later cleanup removes only the asterisk, it can leave a bizarre sentence ending such as `.!`. Confirm the source marker and preserve its note text, then remove the entire body marker before general punctuation cleanup. Scan the packaged EPUB for the stranded signature as a regression check.

### Running-head variants absorbed into prose

Running heads may be extracted at a physical page boundary and then joined into a continuing paragraph. Recognizers must tolerate folio variants such as `405` and `407.`, typographic apostrophe variants, and every running title actually used by the book. After conversion, scan body chapters (excluding the contents, notes, and index) for a page number followed by a known running title. When one failure is found, audit all chapters because the same incomplete header rule usually affects many pages.

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
