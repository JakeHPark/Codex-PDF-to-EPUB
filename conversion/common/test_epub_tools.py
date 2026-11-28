from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from lxml import etree as E
from PIL import Image

from conversion.common.cover_audit import audit_cover
from conversion.common.epub_tools import DC, NCX, OP, Q, doc, el, package
from conversion.common.release import container_check


class PackageTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.work = Path(temp.name)
        self.output = self.work / 'Sample.epub'
        cover = self.work / 'images' / 'cover page.jpg'
        cover.parent.mkdir()
        Image.new('RGB', (40, 60), '#354154').save(cover)
        section = doc('Chapter', language='fr')
        section[-1].append(el('h1', 'Chapter', id='opening'))
        section[-1].append(el('h2', 'Exercise', id='practice'))
        appendix = doc('Appendix', language='fr')
        appendix[-1].append(el('h1', 'Appendix'))
        self.documents = {'chapter.xhtml': section, 'appendix.xhtml': appendix}
        self.toc = [
            ('chapter.xhtml#opening', 'Chapter', 1),
            ('chapter.xhtml#practice', 'Exercise', 2),
            ('appendix.xhtml', 'Appendix', 1),
        ]

    def build(self, headings=None):
        return package(
            self.work, self.output, 'Example', ['Author A', 'Author B'],
            self.documents, self.toc if headings is None else headings,
            cover_asset='images/cover page.jpg', subtitle='A short example',
            language='fr', contents_label='Sommaire',
            modified=datetime(2020, 1, 2, tzinfo=timezone.utc),
        )

    def test_matching_navigation_and_portable_cover(self):
        self.build()
        self.assertEqual(container_check(self.output)['spine_items'], 4)
        self.assertEqual(audit_cover(self.output)['details']['member'], 'EPUB/images/cover page.jpg')
        with ZipFile(self.output) as z:
            nav = E.fromstring(z.read('EPUB/nav.xhtml'))
            ncx = E.fromstring(z.read('EPUB/toc.ncx'))
            opf = E.fromstring(z.read('EPUB/package.opf'))
            native = nav.find(f'.//{Q}nav/{Q}ol')
            legacy = ncx.find(f'{{{NCX}}}navMap')
            self.assertEqual([i[0].text for i in native], ['Chapter', 'Appendix'])
            self.assertEqual(native[0][1][0][0].text, 'Exercise')
            self.assertEqual(legacy[0][-1].find(f'{{{NCX}}}content').get('src'), 'chapter.xhtml#practice')
            self.assertEqual(legacy[1].find(f'{{{NCX}}}content').get('src'), 'appendix.xhtml')
            meta = opf.find(OP + 'metadata')
            self.assertEqual([x.text for x in meta.findall(DC + 'creator')], ['Author A', 'Author B'])
            self.assertEqual(meta.find(DC + 'language').text, 'fr')
            self.assertEqual(meta.find(DC + 'title' + '[@id="subtitle"]').text, 'A short example')

    def test_reproducible_build_and_rejection_preserves_existing_output(self):
        first = self.build()
        self.assertEqual(first, self.build())
        before = self.output.read_bytes()
        with self.assertRaisesRegex(ValueError, 'skips a level'):
            self.build([('chapter.xhtml', 'Chapter', 2)])
        self.assertEqual(self.output.read_bytes(), before)
