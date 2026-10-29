"""Decode the declared EPUB cover and reconcile EPUB 2/3 reader metadata."""
from pathlib import Path, PurePosixPath
from urllib.parse import unquote
import argparse
import hashlib
import io
import json
import posixpath
import zipfile
from xml.etree import ElementTree as E

from PIL import Image

OPF = '{http://www.idpf.org/2007/opf}'
XHTML = '{http://www.w3.org/1999/xhtml}'


def audit_cover(path, max_bytes=None):
    path = Path(path)
    with zipfile.ZipFile(path) as z:
        container = E.fromstring(z.read('META-INF/container.xml'))
        package = next(e.get('full-path') for e in container.iter()
                       if e.tag.endswith('}rootfile'))
        root = E.fromstring(z.read(package))
        items = {e.get('id'): e for e in root.findall('.//' + OPF + 'manifest/' + OPF + 'item')}
        covers = [e for e in items.values() if 'cover-image' in e.get('properties', '').split()]
        if len(covers) != 1:
            raise ValueError('Expected exactly one EPUB 3 cover image')
        cover = covers[0]

        def resolve(origin, href):
            return posixpath.normpath(posixpath.join(posixpath.dirname(origin), unquote(href.split('#')[0])))

        member = resolve(package, cover.get('href', ''))
        legacy = [e.get('content') for e in root.findall('.//' + OPF + 'metadata/' + OPF + 'meta')
                  if e.get('name') == 'cover']
        if legacy != [cover.get('id')]:
            raise ValueError('Legacy cover metadata must identify the same image manifest ID')
        first_id = root.find(OPF + 'spine/' + OPF + 'itemref').get('idref')
        document = resolve(package, items[first_id].get('href'))
        page = E.fromstring(z.read(document))
        if not any(resolve(document, e.get('src', '')) == member for e in page.iter(XHTML + 'img')):
            raise ValueError('First spine document does not display the declared cover')
        data = z.read(member)
        with Image.open(io.BytesIO(data)) as image:
            image.load()  # Header parsing alone misses damaged image payloads.
            formats = {'JPEG': ('image/jpeg', {'.jpg', '.jpeg'}), 'PNG': ('image/png', {'.png'})}
            if image.format not in formats:
                raise ValueError('Cover must decode as JPEG or PNG for portable reader support')
            mime, extensions = formats[image.format]
            if cover.get('media-type') != mime or PurePosixPath(member).suffix.lower() not in extensions:
                raise ValueError('Cover encoding, filename extension and manifest media type disagree')
            if image.mode not in {'RGB', 'RGBA', 'L', 'LA', 'P'}:
                raise ValueError('Convert cover to RGB/grayscale for portable reader support')
            if min(image.size) <= 0:
                raise ValueError('Invalid cover dimensions')
            details = dict(member=member, format=image.format, mode=image.mode,
                           width=image.width, height=image.height, bytes=len(data))
        if max_bytes is not None and len(data) > max_bytes:
            raise ValueError(f'Cover exceeds configured mobile byte budget: {len(data)} > {max_bytes}')
    return dict(epub_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), status='pass',
                unresolved_findings=0, summary='Decoded cover and matching EPUB 2/3 image metadata and first spine page.',
                details=details)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('epub')
    parser.add_argument('--report', required=True)
    parser.add_argument('--max-bytes', type=int)
    args = parser.parse_args()
    try:
        report = audit_cover(args.epub, args.max_bytes)
    except Exception as error:
        report = dict(status='fail', unresolved_findings=1, error=str(error))
    Path(args.report).write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
