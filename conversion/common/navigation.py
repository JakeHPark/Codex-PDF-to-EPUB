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


def validate_toc(root):
    """Validate EPUB 3 TOC list semantics, not merely resolving descendant links.

    Accept ElementTree/lxml roots. Return the number of linked entries. A branch
    may use a direct span label; nested lists must still belong to a labeled li.
    Readers commonly ignore links hidden inside paragraph wrappers.
    """
    q = '{http://www.w3.org/1999/xhtml}'
    tocs = [n for n in root.iter(q + 'nav')
            if 'toc' in n.get(EPUB_TYPE, '').split()]
    if len(tocs) != 1:
        raise ValueError('Expected one semantic EPUB TOC')
    lists = tocs[0].findall(q + 'ol')
    if len(lists) != 1:
        raise ValueError('TOC must contain one direct ordered list')

    def visit(ol):
        if not len(ol) or any(li.tag != q + 'li' for li in ol):
            raise ValueError('TOC ordered list needs nonempty li entries')
        count = 0
        for li in ol:
            children = list(li)
            if not children or children[0].tag not in (q + 'a', q + 'span'):
                raise ValueError('TOC li needs a direct a/span label, without wrappers')
            label = children[0]
            if not (''.join(label.itertext()).strip() or
                    any(n.get('alt', '').strip() for n in label.iter(q + 'img'))):
                raise ValueError('TOC label must not be empty')
            if len(children) > 2 or any(c.tag != q + 'ol' for c in children[1:]):
                raise ValueError('TOC label may only be followed by one nested list')
            if label.tag == q + 'a':
                if not label.get('href', '').strip():
                    raise ValueError('TOC link needs a destination')
                count += 1
            elif len(children) != 2:
                raise ValueError('Unlinked TOC span must label a branch')
            if len(children) == 2:
                count += visit(children[1])
        return count

    return visit(lists[0])
