import unittest
from conversion.common.epub_quality import find_ocr_punctuation_issues

class OpeningQuoteSpacingTests(unittest.TestCase):
 def test_opening_gaps_are_review_candidates(self):
  for text in ['“ ‘feudal law’ was imposed.”', '“ word”', '‘ word’', '“\u00a0‘word’”', '“\u202fword”']:
   self.assertIn('space after opening quote', {i['reason'] for i in find_ocr_punctuation_issues(text)})
  for text in ['“‘feudal law’ was imposed.”', '“word”', '‘word’', '« texte »', '“\n  verse”']:
   self.assertNotIn('space after opening quote', {i['reason'] for i in find_ocr_punctuation_issues(text)})

class OCRPunctuationTests(unittest.TestCase):
 def test_space_before_closing_quote_is_reviewed(self):
  for text in ['“Confusion. ”', '“word ”23', '‘word ’', 'word\u00a0”']:
   self.assertIn('space before closing quote',{i['reason'] for i in find_ocr_punctuation_issues(text)})
  for text in ['“Confusion.”', '‘word’', 'He used ’tis.', '« texte »']:
   self.assertNotIn('space before closing quote',{i['reason'] for i in find_ocr_punctuation_issues(text)})
 def test_embedded_exclamation_is_reviewed_not_rewritten(self):
  for text in ['Beansta!k', 'mere!y']:
   self.assertIn('embedded exclamation mark',{i['reason'] for i in find_ocr_punctuation_issues(text)})
  for text in ['Stop! Next.', 'n! + 1', 'Wow!—yes', 'Really?!']:
   self.assertNotIn('embedded exclamation mark',{i['reason'] for i in find_ocr_punctuation_issues(text)})
 def test_failure_classes(self):
  text="in ' sentiment; person, . lazy. and active ২ how™ strange"
  reasons={i['reason'] for i in find_ocr_punctuation_issues(text)}
  self.assertEqual(reasons,{'isolated apostrophe','conflicting punctuation','period before lowercase','non-ASCII digit','trademark symbol'})
 def test_period_apostrophe_is_reviewed_not_rewritten(self):
  for text in ["They gave up.'", "They gave up.’ Next", "He said 'Stop.'"]:
   self.assertIn('period-apostrophe cluster',{i['reason'] for i in find_ocr_punctuation_issues(text)})
  self.assertEqual(find_ocr_punctuation_issues("They gave up!"),[])
 def test_nested_quote_requires_outer_closer(self):
  # Build with explicit character values to keep the embedded apostrophes clear.
  damaged='"The bank said '+chr(39)+"We don't finance weirdo ideas."+chr(39)
  self.assertIn('unclosed outer double quotation',{i['reason'] for i in find_ocr_punctuation_issues(damaged)})
  self.assertNotIn('unclosed outer double quotation',{i['reason'] for i in find_ocr_punctuation_issues(damaged+'"')})
 def test_internal_asterisk_or_caret_is_a_review_candidate(self):
  for text in ["prob* ably", "af*ter", "F^ire", "x^n"]:
   self.assertIn('internal word symbol',{i['reason'] for i in find_ocr_punctuation_issues(text)})
  self.assertNotIn('internal word symbol',{i['reason'] for i in find_ocr_punctuation_issues('A word*. With a footnote.')})
 def test_ordinary_prose(self):
  self.assertEqual(find_ocr_punctuation_issues("It's 3.14. Next, ‘a quotation’ and a name’s possessive…"),[])
 def test_missing_possessives_are_review_only(self):
  reason='possibly missing possessive apostrophe'
  for text in ['the nation s banks', 'the mans belief', 'discount mens stores', 'the variable s', 'He mans the station.', 'mens rea']:
   before=text
   self.assertIn(reason,{i['reason'] for i in find_ocr_punctuation_issues(text)})
   self.assertEqual(text,before)
  for text in ['the nation’s banks', 'the man’s belief', 'men’s stores', 'Le Mans', 'many nations', 'a = s']:
   self.assertNotIn(reason,{i['reason'] for i in find_ocr_punctuation_issues(text)})
 def test_punctuation_obstructing_dehyphenation(self):
  reason='punctuation interrupts hyphenated word'
  for text in ['price-, less', 'CONSCIOUS- ! NESS.', 'conscious-\n!\nness']:
   before=text
   self.assertIn(reason,{i['reason'] for i in find_ocr_punctuation_issues(text)})
   self.assertEqual(text,before)
  for text in ['price-less', 'over- and under-estimates', 'Wait—! Really?', 'word- ... another', 'x - y', 'Stop! Next.']:
   self.assertNotIn(reason,{i['reason'] for i in find_ocr_punctuation_issues(text)})
 def test_malformed_ellipsis_runs(self):
  for text in ['hollow . . .. Owing', 'Done.. Next', 'Wait.....', 'eyes!. . . . The cry']:
   self.assertTrue(any('ellipsis' in i['reason'] for i in find_ocr_punctuation_issues(text)),text)
  self.assertIn('mixed ellipsis spacing',{i['reason'] for i in find_ocr_punctuation_issues('hollow . . .. Owing')})
  self.assertIn('redundant stop beside ellipsis',{i['reason'] for i in find_ocr_punctuation_issues('eyes!. . . . The cry')})
 def test_valid_ellipses_and_sentence_stops(self):
  for text in ['hollow. . . . Owing', 'hollow . . . Owing', 'Wait... Then', 'Done.... Next', 'Stop! . . . Next', 'Done… Next', 'Done…. Next', '3.14 and 1.2.3']:
   self.assertFalse(any('ellipsis' in i['reason'] for i in find_ocr_punctuation_issues(text)),text)
 def test_comma_after_terminal_punctuation_across_spaces(self):
  for text in ['The occasion arose. ,', 'He said “No!” , then left.', 'Done? ,']:
   self.assertIn('conflicting punctuation',{i['reason'] for i in find_ocr_punctuation_issues(text)})
  self.assertEqual(find_ocr_punctuation_issues('For example, e.g., a comma. Then 3.14.'),[])
 def test_valid_forms_are_only_candidates(self):
  self.assertTrue(find_ocr_punctuation_issues('Mr. smith; বাংলা ২'))
 def test_apostrophe_at_block_edge(self):
  self.assertEqual(find_ocr_punctuation_issues("' I am not of that opinion.")[0]['reason'],'isolated apostrophe')


class CommaCapitalTests(unittest.TestCase):
 def test_sentence_candidates_are_review_only(self):
  for text in ['their pleasure, How about that?', 'a profit, I agree.', 'well served, And believe it.']:
   before=text
   self.assertIn('comma before possible sentence start',{i['reason'] for i in find_ocr_punctuation_issues(text)})
   self.assertEqual(text,before)
 def test_valid_capitals_remain_review_candidates(self):
  for text in ['Richmond, Virginia', 'When ready, I left.', 'Thank you, Mary.', 'the book, Your Erroneous Zones, is here.']:
   self.assertIn('comma before possible sentence start',{i['reason'] for i in find_ocr_punctuation_issues(text)})
 def test_lowercase_and_numbers_are_not_capital_candidates(self):
  for text in ['yes, indeed', '1,000', 'one, two, three', 'finished. How about that?']:
   self.assertNotIn('comma before possible sentence start',{i['reason'] for i in find_ocr_punctuation_issues(text)})

if __name__=='__main__': unittest.main()
