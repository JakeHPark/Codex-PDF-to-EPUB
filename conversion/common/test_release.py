"""Release orchestration regressions: an exit code alone cannot release a book."""
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

try:
    from .release import CHECK_GATES, ReleaseError, container_check, digest, run, save, verify
except ImportError:
    from release import CHECK_GATES, ReleaseError, container_check, digest, run, save, verify


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.w = Path(self.temp.name)
        self.epub = self.w / 'book.epub'
        self.make_epub()
        (self.w / 'source.txt').write_text('Authoritative source.')
        # A deterministic fake converter tests invocation/freshness without requiring Calibre.
        (self.w / 'converter.py').write_text('import pathlib,sys\npathlib.Path(sys.argv[-1]).write_text("Hello world.")\n')
        (self.w / 'check.py').write_text(
            'import hashlib,json,pathlib,sys\n'
            'p=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])\n'
            'out.write_text(json.dumps(dict(epub_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),'
            'status="pass",unresolved_findings=0,summary="Fixture source and reader comparison")))\n')
        self.config = dict(schema_version=1, epub='book.epub', inputs=['source.txt', 'check.py'],
                           reader_text='reader.txt', calibre=[sys.executable, str(self.w / 'converter.py')],
                           checks=[dict(id='book', argv=[sys.executable, 'check.py', '{epub}', 'check-report.json'],
                                        gates=sorted(CHECK_GATES), report='check-report.json')],
                           reviews=dict(second_pass='second.json', visual_review='visual.json'))
        (self.w / 'reader.txt').write_text('Hello world.')
        self.review('second.json')
        self.review('visual.json')

    def make_epub(self, text='Hello world.', bad_link=False):
        x = 'http://www.w3.org/1999/xhtml'
        files = {
            'META-INF/container.xml': '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="EPUB/package.opf"/></rootfiles></container>',
            'EPUB/package.opf': '<package xmlns="http://www.idpf.org/2007/opf" version="3.0"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Book</dc:title><dc:creator>Author</dc:creator><dc:language>en</dc:language><dc:identifier>urn:test</dc:identifier></metadata><manifest><item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/><item id="image" href="cover.png" media-type="image/png" properties="cover-image"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="text" href="text.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="cover"/><itemref idref="text"/></spine></package>',
            'EPUB/cover.xhtml': f'<html xmlns="{x}"><body><img src="cover.png" alt="Cover"/></body></html>',
            'EPUB/cover.png': b'fixture-image',
            'EPUB/nav.xhtml': f'<html xmlns="{x}"><body><nav><a href="text.xhtml#{"missing" if bad_link else "opening"}">Start</a></nav></body></html>',
            'EPUB/text.xhtml': f'<html xmlns="{x}"><body><p id="opening">{text}</p></body></html>',
        }
        with zipfile.ZipFile(self.epub, 'w') as z:
            z.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
            for name, data in files.items():
                z.writestr(name, data)

    def review(self, name, **updates):
        evidence = [dict(path=f, sha256=digest(self.w / f)) for f in ['source.txt', 'check.py', 'reader.txt']]
        data = dict(epub_sha256=digest(self.epub), status='pass', unresolved_findings=0,
                    reviewed_by='test reviewer', scope='Complete fixture', summary='Source and reader reviewed', evidence=evidence)
        data.update(updates)
        save(self.w / name, data)

    def release(self):
        save(self.w / 'release.json', self.config)
        return run(self.w / 'release.json')

    def test_complete_release_and_reverify(self):
        p, r = self.release()
        self.assertEqual(r['status'], 'pass', r)
        self.assertEqual(verify(p)['epub_sha256'], digest(self.epub))
        (self.w / 'source.txt').write_text('Changed source')
        with self.assertRaisesRegex(ReleaseError, 'Stale'):
            verify(p)

    def test_missing_book_gate_cannot_pass(self):
        self.config['checks'][0]['gates'].remove('notes_links')
        self.assertIn('Missing book-specific gates', self.release()[1]['error'])

    def test_second_pass_is_required_even_with_successful_validator(self):
        del self.config['reviews']['second_pass']
        self.assertEqual(self.release()[1]['status'], 'fail')

    def test_old_epub_review_rejected(self):
        self.review('visual.json', epub_sha256='0' * 64)
        self.assertIn('stale approval', self.release()[1]['error'])

    def test_changed_review_evidence_rejected(self):
        (self.w / 'source.txt').write_text('Changed after proofreading')
        self.assertIn('stale evidence', self.release()[1]['error'])

    def test_old_reader_is_deleted_and_missing_export_fails(self):
        self.config['calibre'] = [sys.executable, '-c', 'pass']
        self.assertIn('no reading text', self.release()[1]['error'])
        self.assertFalse((self.w / 'reader.txt').exists())

    def test_second_pass_must_bind_reader_text(self):
        self.review('second.json', evidence=[dict(path=f, sha256=digest(self.w / f)) for f in ['source.txt', 'check.py']])
        self.assertIn('Calibre text export', self.release()[1]['error'])

    def test_zero_exit_without_new_check_report_fails(self):
        save(self.w / 'check-report.json', dict(status='pass', epub_sha256=digest(self.epub)))
        self.config['checks'][0]['argv'] = [sys.executable, '-c', 'pass']
        self.assertIn('missing new check report', self.release()[1]['error'])

    def test_unresolved_custom_findings_fail(self):
        p = self.w / 'check.py'
        p.write_text(p.read_text().replace('unresolved_findings=0', 'unresolved_findings=1'))
        self.assertIn('zero unresolved', self.release()[1]['error'])

    def test_epub_mutation_during_check_fails(self):
        self.config['checks'][0]['argv'] = [sys.executable, '-c', 'import pathlib,sys;pathlib.Path(sys.argv[1]).write_bytes(b"changed")', '{epub}']
        self.assertIn('changed during release', self.release()[1]['error'])

    def test_later_check_cannot_rewrite_earlier_evidence(self):
        self.config['checks'].append(dict(id='rewrite', gates=['text_structure'], report='second-check.json',
            argv=[sys.executable, '-c', 'from pathlib import Path;Path("check-report.json").write_text("changed")']))
        self.assertIn('changed during release', self.release()[1]['error'])

    def test_unreviewed_shared_audit_blocks_release(self):
        self.make_epub('Hello, . This is corrupted.')
        r = self.release()[1]
        self.assertIn('Shared audit', r['error'])

    def test_missing_fragment_fails_container(self):
        self.make_epub(bad_link=True)
        with self.assertRaisesRegex(ReleaseError, 'Missing fragment'):
            container_check(self.epub)

    def test_reader_cannot_overwrite_a_source_file(self):
        self.config['reader_text'] = 'source.txt'
        before = (self.w / 'source.txt').read_bytes()
        self.assertEqual(self.release()[1]['status'], 'fail')
        self.assertEqual((self.w / 'source.txt').read_bytes(), before)

    def test_check_cannot_replace_a_review_record(self):
        self.config['checks'][0]['report'] = 'visual.json'
        before = (self.w / 'visual.json').read_bytes()
        self.assertEqual(self.release()[1]['status'], 'fail')
        self.assertEqual((self.w / 'visual.json').read_bytes(), before)

    def test_review_record_cannot_change_during_a_check(self):
        self.config['checks'][0]['argv'] = [sys.executable, '-c', 'from pathlib import Path;Path("visual.json").write_text("changed")']
        self.assertIn('changed during release', self.release()[1]['error'])

    def test_only_absent_objects_can_be_not_applicable(self):
        self.config['not_applicable'] = {'reader_export': 'Prefer to skip'}
        self.assertEqual(self.release()[1]['status'], 'fail')

    def test_source_only_book_absence_needs_signed_evidence(self):
        self.config['not_applicable'] = {'objects_layout': 'No substantive body objects; cover checked separately'}
        self.config['checks'][0]['gates'].remove('objects_layout')
        self.config['reviews']['objects_layout'] = 'objects.json'
        self.review('objects.json', status='not_applicable')
        self.assertEqual(self.release()[1]['status'], 'pass')

    def test_failed_rerun_invalidates_previous_pass(self):
        p, r = self.release()
        self.assertEqual(r['status'], 'pass')
        self.config['checks'][0]['argv'] = [sys.executable, '-c', 'raise SystemExit(4)']
        self.assertEqual(self.release()[1]['status'], 'fail')
        with self.assertRaisesRegex(ReleaseError, 'not a pass'):
            verify(p)


if __name__ == '__main__':
    unittest.main()
