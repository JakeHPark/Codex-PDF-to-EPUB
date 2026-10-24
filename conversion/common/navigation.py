"""Build navigation labels from semantic headings without their note calls."""
import re

EPUB_TYPE = '{http://www.idpf.org/2007/ops}type'


def heading_label(heading):
    """Return plain heading text, excluding explicit noterefs but keeping tails.

    Accepts ElementTree or lxml elements. Ordinary digits and superscripts are
    retained: callers must identify actual references semantically first.
    """
    def visit(node):
        if ('noteref' in node.get(EPUB_TYPE, '').split()
                or node.get('role') == 'doc-noteref'):
            return ''
        parts = [node.text or '']
        for child in node:
            parts.extend((visit(child), child.tail or ''))
        return ''.join(parts)

    return re.sub(r'\s+', ' ', visit(heading)).strip()
