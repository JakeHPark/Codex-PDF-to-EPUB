import unittest
from conversion.common.epub_quality import find_orphan_symbol_issues

class OrphanSymbols(unittest.TestCase):
    def test_isolated_and_embedded_artifacts_are_flagged(self):
        s='A closet <A room. Talent. © : A waist. ° More prose.'
        marks=[v['symbol'] for v in find_orphan_symbol_issues(s)]
        self.assertIn('<',marks);self.assertIn('©',marks);self.assertIn('°',marks)
    def test_numeric_degrees_and_ordinary_punctuation_pass(self):
        self.assertEqual(find_orphan_symbol_issues('From 60° to 70°, turn 45°. English! French !'),[])
    def test_legitimate_symbols_still_require_context_review(self):
        s='Copyright © 1872. Let x < y.'
        self.assertEqual([v['symbol'] for v in find_orphan_symbol_issues(s)],['©','<'])
        self.assertEqual(s,'Copyright © 1872. Let x < y.')
    def test_punctuation_cluster(self):
        self.assertTrue(find_orphan_symbol_issues('Prevalent. — ;'))

if __name__=='__main__':unittest.main()
