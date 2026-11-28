"""Assemble reflowable EPUB 3 from prepared XHTML and local assets."""
from datetime import datetime, timezone
import hashlib
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

from lxml import etree as E

Q = '{http://www.w3.org/1999/xhtml}'
EP = 'http://www.idpf.org/2007/ops'
OP = '{http://www.idpf.org/2007/opf}'
DC = '{http://purl.org/dc/elements/1.1/}'
NCX = 'http://www.daisy.org/z3986/2005/ncx/'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
OPS_TYPE = '{' + EP + '}type'
MIMETYPE = 'application/epub+zip'
ASSET_TYPES = {
    '.css': 'text/css',
    '.gif': 'image/gif',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.otf': 'font/otf',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
    '.ttf': 'font/ttf',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
}
CONTAINER = b'''<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
'''


def el(tag, text=None, **attributes):
    """Create an XHTML element with optional text and attributes."""
    node = E.Element(Q + tag, **attributes)
    node.text = text
    return node


def doc(title, *, language='en'):
    """Create a document whose last child is its writable body."""
    root = E.Element(Q + 'html', nsmap={None: Q[1:-1], 'epub': EP})
    root.set('lang', language)
    root.set(XML_LANG, language)
    head = E.SubElement(root, Q + 'head')
    head.append(el('meta', charset='utf-8'))
    head.append(el('title', title))
    head.append(el('link', rel='stylesheet', href='style.css'))
    E.SubElement(root, Q + 'body')
    return root


def _xml(node):
    return E.tostring(node, encoding='utf-8', xml_declaration=True)


def _navigation(headings, title, label, identifier, language):
    book_nav = doc(label, language=language)
    toc = el('nav', id='toc', **{OPS_TYPE: 'toc'})
    toc.append(el('h1', label))
    listing = el('ol')
    toc.append(listing)
    book_nav[-1].append(toc)
    landmarks = el('nav', hidden='hidden', **{OPS_TYPE: 'landmarks'})
    cover_list = el('ol')
    item = el('li')
    item.append(el('a', 'Cover', href='cover.xhtml', **{OPS_TYPE: 'cover'}))
    cover_list.append(item)
    landmarks.append(cover_list)
    book_nav[-1].append(landmarks)

    ns = '{' + NCX + '}'
    ncx = E.Element(ns + 'ncx', nsmap={None: NCX}, version='2005-1')
    ncx.set(XML_LANG, language)
    head = E.SubElement(ncx, ns + 'head')
    for name, value in (
        ('dtb:uid', identifier), ('dtb:depth', str(max(level for _, _, level in headings))),
        ('dtb:totalPageCount', '0'), ('dtb:maxPageNumber', '0'),
    ):
        E.SubElement(head, ns + 'meta', name=name, content=value)
    E.SubElement(E.SubElement(ncx, ns + 'docTitle'), ns + 'text').text = title
    nav_map = E.SubElement(ncx, ns + 'navMap')

    # Build both TOCs from the same stack so labels, order and parents agree.
    html_lists = [listing]
    legacy_parents = [nav_map]
    for index, (href, text, level) in enumerate(headings, 1):
        if level > len(html_lists):
            raise ValueError(f'Navigation skips a level at {text!r}')
        del html_lists[level:]
        del legacy_parents[level:]
        item = el('li')
        item.append(el('a', text, href=href))
        html_lists[-1].append(item)

        point = E.SubElement(legacy_parents[-1], ns + 'navPoint', id=f'nav-{index}', playOrder=str(index))
        E.SubElement(E.SubElement(point, ns + 'navLabel'), ns + 'text').text = text
        E.SubElement(point, ns + 'content', src=href)

        sublist = el('ol')
        item.append(sublist)
        html_lists.append(sublist)
        legacy_parents.append(point)

    for sublist in list(toc.iter(Q + 'ol')):
        if not len(sublist):
            sublist.getparent().remove(sublist)
    return book_nav, ncx


def _member_name(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '..' in path.parts or path.as_posix() != name or '\\' in name:
        raise ValueError(f'Invalid EPUB member path: {name!r}')
    return name


def package(work, output, title, authors, documents, headings, assets=(), *,
            cover_asset='cover.png', subtitle=None, date=None, language='en',
            contents_label='Contents', identifier=None, extra_css='', modified=None):
    """Write a complete EPUB atomically and return its SHA-256.

    Documents map root-level XHTML filenames to lxml elements, in spine order.
    Headings are (href, label, one-based depth) triples. Pass URI-escaped links
    in XHTML and headings, and literal relative paths for asset filenames.
    Assets and an optional base-style.css are read from work. The cover must
    be a local JPEG or PNG and is included automatically. Supply a timezone-
    aware modified datetime for reproducible bytes with the same runtime.
    """
    work, output = Path(work), Path(output)
    authors, headings, assets = tuple(authors), tuple(headings), tuple(assets)
    if not title.strip() or not authors or any(not author.strip() for author in authors) or not language.strip():
        raise ValueError('A title, at least one credited author and a language are required')
    if not documents or not headings or any(type(depth) is not int or depth < 1 or not label.strip() or not href
                                            for href, label, depth in headings):
        raise ValueError('Provide body documents and a nonempty, one-based TOC')
    reserved = {'cover.xhtml', 'nav.xhtml', 'toc.ncx', 'style.css', 'package.opf'}
    for name, root in documents.items():
        _member_name(name)
        if '/' in name or not name.endswith('.xhtml') or name in reserved or root.tag != Q + 'html':
            raise ValueError(f'Expected a root-level body XHTML member: {name!r}')
    asset_names = (cover_asset, *assets)
    if len(set(asset_names)) != len(asset_names) or set(asset_names) & (reserved | documents.keys()):
        raise ValueError('Duplicate or reserved asset name')
    media = {_member_name(name): ASSET_TYPES.get(PurePosixPath(name).suffix.lower()) for name in asset_names}
    if not all(media.values()) or media[cover_asset] not in {'image/jpeg', 'image/png'}:
        raise ValueError('Unsupported asset extension or cover format')

    timestamp = modified or datetime.now(timezone.utc)
    if timestamp.utcoffset() is None:
        raise ValueError('modified must have a time zone')
    timestamp = timestamp.astimezone(timezone.utc)
    if identifier is None:
        key = '\0'.join((title, *authors, subtitle or '', date or '', language))
        identifier = 'urn:sha256:' + hashlib.sha256(key.encode()).hexdigest()

    cover = doc('Cover', language=language)
    cover[-1].set('class', 'cover')
    cover[-1].append(el('img', src=quote(cover_asset), alt=title + ' — ' + ', '.join(authors)))
    nav, ncx = _navigation(headings, title, contents_label, identifier, language)
    documents = {'cover.xhtml': cover, 'nav.xhtml': nav, **documents}
    content = {name: _xml(root) for name, root in documents.items()}
    media.update(dict.fromkeys(documents, 'application/xhtml+xml'))
    content['toc.ncx'] = _xml(ncx)
    media['toc.ncx'] = 'application/x-dtbncx+xml'
    style = work / 'base-style.css'
    if not style.is_file():
        style = Path(__file__).with_name('epub_base.css')
    content['style.css'] = (style.read_text(encoding='utf-8') + '\n' + extra_css).encode()
    media['style.css'] = 'text/css'
    content.update({name: (work / name).read_bytes() for name in asset_names})

    opf = E.Element(OP + 'package', nsmap={None: OP[1:-1], 'dc': DC[1:-1]},
                    version='3.0', **{'unique-identifier': 'book-id'})
    metadata = E.SubElement(opf, OP + 'metadata')
    E.SubElement(metadata, DC + 'identifier', id='book-id').text = identifier
    main_title = E.SubElement(metadata, DC + 'title')
    main_title.text = title
    if subtitle:
        main_title.set('id', 'main-title')
        E.SubElement(metadata, DC + 'title', id='subtitle').text = subtitle
        for field, value in [('main-title', 'main'), ('subtitle', 'subtitle')]:
            E.SubElement(metadata, OP + 'meta', property='title-type', refines='#' + field).text = value
    E.SubElement(metadata, DC + 'language').text = language
    for author in authors:
        E.SubElement(metadata, DC + 'creator').text = author
    if date:
        E.SubElement(metadata, DC + 'date').text = date
    E.SubElement(metadata, OP + 'meta', property='dcterms:modified').text = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    E.SubElement(metadata, OP + 'meta', name='cover', content='cover-image')

    manifest = E.SubElement(opf, OP + 'manifest')
    ids = {}
    for index, name in enumerate(content):
        ids[name] = 'cover-image' if name == cover_asset else f'item-{index}'
        item = E.SubElement(manifest, OP + 'item', id=ids[name], href=quote(name), **{'media-type': media[name]})
        properties = []
        if name == cover_asset:
            properties.append('cover-image')
        if name == 'nav.xhtml':
            properties.append('nav')
        if name in documents:
            for namespace, prop in [('http://www.w3.org/2000/svg', 'svg'),
                                    ('http://www.w3.org/1998/Math/MathML', 'mathml')]:
                if documents[name].find(f'.//{{{namespace}}}*') is not None:
                    properties.append(prop)
        if properties:
            item.set('properties', ' '.join(properties))
    spine = E.SubElement(opf, OP + 'spine', toc=ids['toc.ncx'])
    for name in documents:
        E.SubElement(spine, OP + 'itemref', idref=ids[name])
    guide = E.SubElement(opf, OP + 'guide')
    E.SubElement(guide, OP + 'reference', type='cover', title='Cover', href='cover.xhtml')
    content['package.opf'] = _xml(opf)

    with NamedTemporaryFile(dir=output.parent, suffix='.epub', delete=False) as stage:
        temp = Path(stage.name)
    try:
        # EPUB modification metadata and ZIP member times come from one clock.
        # ZIP dates before 1980 cannot be encoded.
        zip_time = max(timestamp, datetime(1980, 1, 1, tzinfo=timezone.utc)).timetuple()[:6]
        with ZipFile(temp, 'w') as archive:
            archive.writestr(ZipInfo('mimetype', zip_time), MIMETYPE, compress_type=ZIP_STORED)
            archive.writestr(ZipInfo('META-INF/container.xml', zip_time), CONTAINER, compress_type=ZIP_DEFLATED)
            for name, data in content.items():
                archive.writestr(ZipInfo('EPUB/' + name, zip_time), data, compress_type=ZIP_DEFLATED)
        with temp.open('rb') as stream:
            checksum = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                checksum.update(chunk)
            digest = checksum.hexdigest()
        temp.replace(output)
    finally:
        temp.unlink(missing_ok=True)
    return digest
