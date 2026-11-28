# Runnable conversion recipes

These examples keep the conversion decisions close to the code that applies
them. Their sources can be generated locally. General helpers live in
[common](../common/), and private work folders follow the layout in
[AGENTS.md](../../AGENTS.md).

## Studio Notes

[Studio Notes](studio_notes.py) is an original one-page fixture. Its authoritative
revised edition is a two-column raster PDF with highlighted text and a music
example. Its earlier EPUB supplies an inline emphasis span confirmed in the scan. The revised
wording comes from the scan. The crop preserves the full staff, and its
caption remains selectable.

From the repository root, with Python, lxml, NumPy, Pillow 10.1 or later,
Tesseract, and Poppler available:

```sh
python3 -m conversion.recipes.studio_notes tmp/studio-notes-demo
```

Use a fresh destination. The recipe generates both source files, the EPUB, and
`inventory.json` with source and output checksums, pixel coordinates, and the
edition and typography decisions. The shared English Tesseract model is used
by default. The example checks the package, cover, reading order, revised
wording, carried-over emphasis, the packaged crop, and shared text and style checks. Add
`--reader ebook-convert` to verify the reading stream through Calibre.

The source areas and expected readings are specific to this fixture. For a
real book, inspect its own layout and use the full
[release workflow](../README.md#release-orchestration).
