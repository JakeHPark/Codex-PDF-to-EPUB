"""Shared inspection helpers for text-based PDF conversion.

Some typeset PDFs map one.super to '1' at the body size and baseline, and
N.sc to 'n'. Font size and Unicode alone cannot recover those distinctions.
Return position-keyed glyph names to join to PyMuPDF rawdict characters. The
caption helper identifies wrapped lines for safe table-panel cropping. These
helpers preserve source text; they do not perform OCR or rewrite prose.
"""
import io
import unicodedata
from fontTools.cffLib import CFFFontSet
from fontTools.agl import toUnicode


def continues_wrapped_caption(previous, candidate, max_baseline_gap=14.0):
    """Whether an adjacent PDF text line belongs to a wrapped object caption.

    Compare line starts and text size, rather than font-family names: many
    books switch from a bold caption label to roman text for the continuation.
    The caller must stop at the first table header/body row.
    """
    prev_box = previous['bbox']
    next_box = candidate['bbox']
    baseline_gap = next_box[1] - prev_box[1]
    return (
        -1.0 <= baseline_gap <= max_baseline_gap
        and abs(float(candidate['size']) - float(previous['size'])) <= 0.75
    )


def recover_ligature(text, glyph_name):
    """Expand a verified f-ligature even when ToUnicode maps it only to f.

    Apply to one actual glyph, not an arbitrarily sized text span. Do not
    duplicate already-expanded characters supplied by an extractor.
    """
    mapped=unicodedata.normalize('NFKC',toUnicode(glyph_name))
    if mapped in ('fi','fl','ff','ffi','ffl','ft','ffj') and text in ('f','ﬀ','ﬁ','ﬂ','ﬃ','ﬄ'):
        return mapped
    return text


def position_key(font, origin):
    return font, round(origin[0], 2), round(origin[1], 2)


class GlyphSemantics:
    def __init__(self, document):
        self.document = document
        self.cache = {}

    def page_map(self, page):
        names_by_font = {}
        for entry in page.get_fonts():
            xref = entry[0]
            if xref not in self.cache:
                name, ext, _, data = self.document.extract_font(xref)
                names = []
                if ext == 'cff':
                    cff = CFFFontSet()
                    cff.decompile(io.BytesIO(data), None)
                    names = cff[cff.fontNames[0]].charset
                self.cache[xref] = names
            names_by_font[entry[3].split('+')[-1]] = self.cache[xref]
        result = {}
        for span in page.get_texttrace():
            names = names_by_font.get(span['font'], [])
            for _, glyph, origin, _ in span['chars']:
                if 0 <= glyph < len(names):
                    result[position_key(span['font'], origin)] = names[glyph]
        return result
