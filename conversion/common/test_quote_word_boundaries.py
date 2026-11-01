import unittest
from epub_quality import find_ocr_punctuation_issues
class WordBoundaryAuditTest(unittest.TestCase):
 def reasons(self,s):return {r['reason'] for r in find_ocr_punctuation_issues(s)}
 def test_closing_quote_before_word(self):
  for s in ['“integrations”of it.', '"integration"of it.', '“écho”encore']:
   self.assertIn('closing quote touches following word',self.reasons(s))
 def test_openers_and_correct_boundaries(self):
  for s in ['“integration” of it.', 'He said "integration" today.', '“word,” she said.', '29″ wide']:
   self.assertNotIn('closing quote touches following word',self.reasons(s))
 def test_possessive_gap(self):
  for s in ['one’ s thoughts', "one' s thoughts"]:self.assertIn('space inside possessive apostrophe',self.reasons(s))
  for s in ['one’s thoughts', 'dogs’ bowls', '‘word’ said aloud']:
   self.assertNotIn('space inside possessive apostrophe',self.reasons(s))
 def test_ol_is_review_only_and_whole_token(self):
  self.assertIn('possible of misread as ol',self.reasons('composers ol that time'))
  for s in ['Mongol music', 'alcohol', 'ol-based identifier', 'OL acronym']:
   self.assertNotIn('possible of misread as ol',self.reasons(s))
if __name__=='__main__':unittest.main()
