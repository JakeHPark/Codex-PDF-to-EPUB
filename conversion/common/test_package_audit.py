import tempfile
import unittest
from pathlib import Path
import zipfile
from conversion.common.package_audit import audit_epub


class PackageAuditTests(unittest.TestCase):
    def test_opening_quote_gap_crosses_inline_markup(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>“<span> </span>‘feudal law’ was imposed.”</p>')
            self.assertTrue(any(r['finding']['reason']=='space after opening quote' for r in audit_epub(path)['records']))
            self.package(d,'<p>“‘feudal law’ was imposed.”</p>')
            self.assertEqual(audit_epub(path)['unreviewed_count'],0)
    def test_closing_quote_space_crosses_inline_markup(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>“Confusion.<span> </span>”</p>')
            self.assertTrue(any(r['finding']['reason']=='space before closing quote' for r in audit_epub(path)['records']))
            self.package(d,'<p>“Confusion.”</p>')
            self.assertEqual(audit_epub(path)['unreviewed_count'],0)
    def test_embedded_exclamation_across_inline_markup(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>Beansta<span>!</span>k</p>')
            self.assertTrue(any(r['finding']['reason']=='embedded exclamation mark' for r in audit_epub(path)['records']))
            self.package(d,'<p>Beanstalk! Next.</p>')
            self.assertEqual(audit_epub(path)['unreviewed_count'],0)
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

    def test_quote_mismatch_blocks_across_inline_styles(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>He estimates “secondary <span>effects</span>’—changes.</p>')
            result=audit_epub(path)
            self.assertTrue(any(r['kind']=='quotes' for r in result['unreviewed']))
            self.package(d,'<p>He estimates “secondary <span>effects</span>”—changes.</p>')
            self.assertEqual(audit_epub(path)['unreviewed_count'],0)

    def test_nested_possessive_title_missing_quote_blocks_release(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>“The name is called ‘<span>Haddocks’ Eyes</span>.”</p>')
            self.assertTrue(any(r['kind']=='quotes' for r in audit_epub(path)['unreviewed']))
            self.package(d,'<p>“The name is called ‘<span>Haddocks’ Eyes</span>.’”</p>')
            self.assertEqual(audit_epub(path)['unreviewed_count'],0)
            self.package(d,'<p>“He called it ‘no,’” she said. The historians’ books.</p>')
            self.assertEqual(audit_epub(path)['unreviewed_count'],0)

    def test_continued_quote_requires_exact_review(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p id="intro">He said, “In other words:</p>')
            result=audit_epub(path)
            keys=[r['key'] for r in result['records'] if r['kind']=='quotes']
            self.assertTrue(keys)
            self.assertEqual(audit_epub(path,reviewed_keys=keys)['unreviewed_count'],0)
            self.package(d,'<p id="intro">He said, “Something else:</p>')
            self.assertGreater(audit_epub(path,reviewed_keys=keys)['unreviewed_count'],0)

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

    def test_ellipsis_check_crosses_inline_boundaries(self):
        with tempfile.TemporaryDirectory() as d:
            path=self.package(d,'<p>mostly hollow . <span>.</span> .. Owing to it.</p>')
            self.assertTrue(any(r['finding']['reason']=='mixed ellipsis spacing'
                                for r in audit_epub(path)['records']))
            self.package(d,'<p>mostly hollow. . . . Owing to it.</p>')
            self.assertEqual(audit_epub(path)['unreviewed_count'],0)


if __name__=='__main__':unittest.main()
