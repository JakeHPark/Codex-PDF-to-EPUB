# Packaging and release validation

## Mandatory whole-book second pass

After the initial complete conversion and correction cycle, perform a fresh
proofreading pass over the entire packaged reading stream before delivery.
Include front matter, every chapter, lists, captions, quotations and notes.
This is separate from the first extraction audit and must not depend on a user
finding an error. Record its scope, actual checks, reviewed findings, repairs,
exceptions and final artifact checksum in a distinct QA entry.

For OCR, review suspicious words and glyphs in context as well as punctuation;
a valid-looking word or high OCR confidence does not prove the reading. Use
lexical comparisons as candidate generators, preserving names, dialect, archaic
spellings and foreign-language passages unless source evidence supports repair.
Recheck cross-page sentences and prose/inset/list boundaries. Examine complete
emphasis expressions and their roman neighbors: correct italic variables can
still coexist with falsely italicized prose. Refresh the packaged shared audit,
resolve every finding, and source-check new candidates beyond the original
repairs. An unchanged list of first-pass findings is not a second pass.

After second-pass corrections, rebuild and run the final package/reader gates;
inspect all special repairs in that output. Recheck affected classes throughout
the book when later changes invalidate them. Do not claim a literal word-by-word
manual proofread if the performed pass combined automated detection with focused
source review; state the actual scope and remaining source limitations.

Detailed operating rules supporting [AGENTS.md](../../AGENTS.md). Read the
sections selected by its source and feature routing tables before implementing
that part of a conversion. These are instructions, not a list of checks that
can be satisfied by merely generating a report.

## Contents

- [Cover, metadata and EPUB container](#cover-metadata-and-epub-container)
- [Container, structural and reader checks](#container-structural-and-reader-checks)
- [Visual review coverage](#visual-review-coverage)
- [Keep source filenames out of EPUB metadata](#keep-source-filenames-out-of-epub-metadata)

## Cover, metadata and EPUB container

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

Identify the cover document semantically as well as declaring its image. Use an
EPUB navigation landmark and compatible legacy guide information when required
by the target reader/converter. Check that a reader does not add a second cover
because it cannot associate the declared image with the first spine document.
Preserve one real cover document; do not hide a duplicate-cover defect by
removing the required cover image or its metadata.

An EPUB is a ZIP container with strict requirements:

- `mimetype` must be the first member;
- `mimetype` must be stored without compression;
- `META-INF/container.xml` must point to the package document;
- every manifest and spine reference must resolve;
- XHTML and XML must be well formed;
- navigation entries must match real sections;
- metadata, language, cover, and reading order must be present.

## Container, structural and reader checks

### Container validation

Verify ZIP integrity, member order, compression rules, manifest references, spine references, XML parsing, and navigation targets.

When repairing a corrupt EPUB, preserve a copy before changing the archive.
A truncated compressed entry may still yield its complete original contents:
accept such recovery only when the uncompressed length and original CRC both
match and the recovered document parses correctly. Repackage with valid ZIP
records, verify every member, and compare all recovered payloads byte for byte.
Do not ignore overlap/truncation warnings or silently discard an unreadable
entry. If exact recovery fails, rebuild a damaged navigation document from
verified surviving navigation/spine data and document that reconstruction.

### Structural and textual assertions

Add regression assertions for every confirmed error. Examples:

```python
assert "predictable or mechanical" in text
assert "predictable or</p>\n<p>mechanical" not in text
assert "<p>7. Progress Without Subtraction</p>" not in text
assert "Apparently everywhere" in text
```

Also scan for suspicious paragraph boundaries where a paragraph ends without terminal punctuation and the next begins in lowercase.

### Reader-level round trip

Use Calibre’s `ebook-convert` to export the finished EPUB to plain text. Search that export for:

- corrected phrases;
- duplicated headings;
- missing chapter openings;
- stray note markers;
- gibberish signatures;
- unexpected hyphenation;
- text that exists in XHTML but disappears in a reader conversion.

The packaged EPUB—not the build directory—is the artifact that must pass.

## Visual review coverage

At minimum, inspect:

- cover and title page;
- table of contents;
- first paragraph of every chapter and part;
- pages surrounding every source boundary;
- all footnote sections;
- block quotations and section breaks;
- bibliography and index samples;
- any page whose extraction required a special repair.

## Keep source filenames out of EPUB metadata

Do not embed source-PDF filenames, local paths, download-site labels or temporary
working filenames in the package metadata, including `dc:source`, descriptions
and identifiers. Keep file provenance and conversion evidence in the external
book-specific build records. When bibliographic source metadata is useful, use
a proper edition citation or authoritative publication URL. Inspect all packaged
metadata fields before release; removing visible source credits alone is not
sufficient.

Verify cover and illustration formats from their decoded content, not merely
filenames. A downloaded `.jpg` can contain WebP bytes. Convert unsupported
formats to a genuinely supported encoding, preferably losslessly, and keep the
manifest media type and extension consistent. Compare decoded pixels when an
encoding change is necessary; byte equality alone can certify a mislabeled file.
