import unittest
from xml.etree import ElementTree as E
from conversion.common.inline_audit import find_emphasis_issues, find_unlinked_note_candidates
from conversion.common.epub_quality import find_ocr_slash_issues, find_degree_glyphs


class InlineAuditTests(unittest.TestCase):
    def issues(self, markup, **kwargs):
        return find_emphasis_issues(E.fromstring(markup), **kwargs)

    def test_partial_word_and_fused_dash(self):
        self.assertIn('partial-word emphasis', {i['reason'] for i in self.issues('<p><em>du</em>rable</p>')})
        self.assertIn('emphasis at dash boundary', {i['reason'] for i in self.issues('<p><em>Title—mostly</em> ordinary prose.</p>')})
        # Correct mixed styling still needs source review at a dash.
        self.assertIn('emphasis at dash boundary', {i['reason'] for i in self.issues('<p><em>Title</em>—mostly ordinary prose.</p>')})

    def test_short_gaps_and_known_foreign_phrase(self):
        issues = self.issues('<p><em>faute</em> de <em>mieux</em>; <em>Narrative</em> as a <em>Symbolic Act</em></p>', known_phrases=['faute de mieux'])
        self.assertEqual([i['token'] for i in issues if i['reason']=='short roman gap between emphasis'], ['de', 'as a'])
        self.assertIn('incomplete reviewed italic phrase', {i['reason'] for i in issues})
        complete = self.issues('<p><em>faute de mieux</em></p>', known_phrases=['faute de mieux'])
        self.assertFalse(any(i['reason'].startswith('incomplete') for i in complete))

    def test_isolated_emphasis_is_review_not_rewrite(self):
        issues=self.issues('<p>On the <em>verge</em> of retiring; really <em>not</em> ready.</p>')
        self.assertEqual([i['token'] for i in issues if i['reason']=='isolated emphasized word'], ['verge','not'])

    def test_mostly_styled_block_includes_long_missing_words(self):
        issues=self.issues('<p><em>This entire heading needs complete</em> emphasis</p>')
        self.assertIn('roman outlier in mostly emphasized block', {i['reason'] for i in issues})

    def test_semantic_barriers_and_inheritance(self):
        self.assertEqual(self.issues('<p><code>a//b</code><math>x</math></p>'), [])
        self.assertFalse(any(i['reason']=='partial-word emphasis' for i in self.issues('<p><em>whole<strong>word</strong></em></p>') if i['style']=='italic'))
        issues=self.issues('<p><em>Alpha</em> to<br/><em>Beta</em></p>')
        self.assertFalse(any(i['reason']=='short roman gap between emphasis' for i in issues))

    def test_unlinked_notes_and_real_note_containers(self):
        broken=E.fromstring('<body><p id="call">merit raises.*</p><p>*See the source.</p></body>')
        self.assertEqual(len(find_unlinked_note_candidates(broken)),2)
        valid=E.fromstring('<body xmlns:epub="http://www.idpf.org/2007/ops"><p>raises.<a epub:type="noteref" href="#n"><sup>*</sup></a></p><aside id="n" epub:type="footnote"><p>*See the source.</p></aside></body>')
        self.assertEqual(find_unlinked_note_candidates(valid),[])

    def test_slashes_and_degree_glyphs_are_reviewable(self):
        reasons={i['reason'] for i in find_ocr_slash_issues('a// of them, stolen/ hidden and /ocal.')}
        self.assertEqual(len(reasons),3)
        self.assertEqual(find_ocr_slash_issues('stolen/hidden and https://host/path'),[])
        self.assertIn('slash-shaped final letter', {i['reason'] for i in find_ocr_slash_issues('So/- dier and rea/.')})
        self.assertEqual(len(find_degree_glyphs('30° and 3° confrontation; 3º')),3)


if __name__=='__main__': unittest.main()
