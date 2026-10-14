import unittest
from conversion.common.epub_quality import find_period_word_spacing_issues

class PeriodSpacingTests(unittest.TestCase):
    def test_number_and_closing_parenthesis_before_sentence(self):
        for text in ('0 to 1.An impossible event', '(1999).Working group', 'ends.Next sentence', 'ends.next sentence'):
            self.assertEqual(len(find_period_word_spacing_issues(text)),1,text)
    def test_spaced_sentences_and_decimals(self):
        for text in ('1. An impossible event','Value 0.125 or .5','ends. Next sentence'):
            self.assertEqual(find_period_word_spacing_issues(text),[])
    def test_unicode_letters(self):
        self.assertEqual(len(find_period_word_spacing_issues('fin.Événement')),1)
    def test_abbreviations_and_domains_need_review(self):
        for text in ('U.S. Census','example.com','Ph.D. student'):
            self.assertTrue(find_period_word_spacing_issues(text))

if __name__=='__main__':unittest.main()
