import unittest
from conversion.common.epub_quality import find_ocr_punctuation_issues

class OCRPunctuationTests(unittest.TestCase):
 def test_failure_classes(self):
  text="in ' sentiment; person, . lazy. and active ২ how™ strange"
  reasons={i['reason'] for i in find_ocr_punctuation_issues(text)}
  self.assertEqual(reasons,{'isolated apostrophe','conflicting punctuation','period before lowercase','non-ASCII digit','trademark symbol'})
 def test_ordinary_prose(self):
  self.assertEqual(find_ocr_punctuation_issues("It's 3.14. Next, ‘a quotation’ and a name’s possessive…"),[])
 def test_valid_forms_are_only_candidates(self):
  self.assertTrue(find_ocr_punctuation_issues('Mr. smith; বাংলা ২'))
 def test_apostrophe_at_block_edge(self):
  self.assertEqual(find_ocr_punctuation_issues("' I am not of that opinion.")[0]['reason'],'isolated apostrophe')

if __name__=='__main__': unittest.main()
