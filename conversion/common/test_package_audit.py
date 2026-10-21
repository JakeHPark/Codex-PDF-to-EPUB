import tempfile
import unittest
from pathlib import Path
import zipfile
from conversion.common.package_audit import audit_epub


class PackageAuditTests(unittest.TestCase):
    def package(self, directory, markup):
        path=Path(directory)/'test.epub'
        with zipfile.ZipFile(path,'w') as archive:
            archive.writestr('EPUB/chapter.xhtml','<html xmlns="http://www.w3.org/1999/xhtml"><body>'+markup+'</body></html>')
        return path

    def test_actual_package_defect_blocks_until_repaired(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>It happened. ,</p>')
            self.assertGreater(audit_epub(path)['unreviewed_count'],0)
            self.package(d,'<p>It happened.</p>')
            self.assertEqual(audit_epub(path)['unreviewed_count'],0)

    def test_period_spacing_crosses_inline_styles(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>had to.<em>say</em> about it.</p>')
            findings=audit_epub(path)['records']
            self.assertTrue(any(r['kind']=='period_spacing' for r in findings))
            self.package(d,'<p>had to <em>say</em> about it.</p>')
            self.assertFalse(any(r['kind']=='period_spacing' for r in audit_epub(path)['records']))
            self.package(d,'<p>Use 3.14.</p>')
            self.assertFalse(any(r['kind']=='period_spacing' for r in audit_epub(path)['records']))

    def test_review_applies_only_to_exact_text_and_style(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>It is <em>really</em> so.</p>')
            result=audit_epub(path);keys=[r['key'] for r in result['records']]
            self.assertTrue(keys)
            self.assertEqual(audit_epub(path,reviewed_keys=keys)['unreviewed_count'],0)
            self.package(d,'<p>It is really <em>so</em>.</p>')
            self.assertGreater(audit_epub(path,reviewed_keys=keys)['unreviewed_count'],0)


if __name__=='__main__':unittest.main()
