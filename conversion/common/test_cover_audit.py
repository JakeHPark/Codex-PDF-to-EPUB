import io
from pathlib import Path
import tempfile
import unittest
import zipfile
from PIL import Image

try:
    from .cover_audit import audit_cover
except ImportError:
    from cover_audit import audit_cover


class CoverTests(unittest.TestCase):
    def make(self, data=None, meta='image', mime='image/png'):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name) / 'book.epub'
        if data is None:
            stream = io.BytesIO()
            Image.new('RGB', (20, 30), 'navy').save(stream, format='PNG')
            data = stream.getvalue()
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr('META-INF/container.xml', '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfile full-path="book.opf"/></container>')
            z.writestr('book.opf', f'<package xmlns="http://www.idpf.org/2007/opf"><metadata><meta name="cover" content="{meta}"/></metadata><manifest><item id="image" href="cover.png" media-type="{mime}" properties="cover-image"/><item id="page" href="cover.xhtml"/></manifest><spine><itemref idref="page"/></spine></package>')
            z.writestr('cover.xhtml', '<html xmlns="http://www.w3.org/1999/xhtml"><body><img src="cover.png"/></body></html>')
            z.writestr('cover.png', data)
        return path

    def test_matching_decodable_cover(self):
        self.assertEqual(audit_cover(self.make())['details']['width'], 20)

    def test_legacy_id_is_not_an_image_filename(self):
        with self.assertRaisesRegex(ValueError, 'manifest ID'):
            audit_cover(self.make(meta='cover.png'))

    def test_mislabeled_encoding(self):
        with self.assertRaisesRegex(ValueError, 'disagree'):
            audit_cover(self.make(mime='image/jpeg'))

    def test_undecodable_payload(self):
        with self.assertRaises(OSError):
            audit_cover(self.make(data=b'not an image'))

    def test_explicit_mobile_budget(self):
        with self.assertRaisesRegex(ValueError, 'byte budget'):
            audit_cover(self.make(), max_bytes=10)


if __name__ == '__main__':
    unittest.main()
