import unittest
from epub_quality import find_ocr_punctuation_issues

class OCRCaseAndGuillemets(unittest.TestCase):
    def reasons(self,text):
        return [x['reason'] for x in find_ocr_punctuation_issues(text)]
    def test_lowercase_outlier(self):
        self.assertIn('lowercase outlier in uppercase word',self.reasons('UsING SCRIPTS'))
        for text in ['USING SCRIPTS','Using scripts','iPhone eBay HTML','NASA TCP']:
            self.assertNotIn('lowercase outlier in uppercase word',self.reasons(text))
    def test_exclamation_in_discretionary_word_break(self):
        for text in ['know!- edge', 'know!-\nedge', 'Beansta!k']:
            self.assertIn('embedded exclamation mark', self.reasons(text))
        for text in ['Stop! Next.', 'Wonderful!—Next question.']:
            self.assertNotIn('embedded exclamation mark', self.reasons(text))
    def test_guillemets_are_paired_not_removed(self):
        for text in ['Call back. »','«An unfinished quotation','‹unfinished']:
            self.assertIn('unpaired guillemet',self.reasons(text))
        self.assertNotIn('unpaired guillemet',self.reasons('«Une citation.» ‹Another›'))
    def test_nota_is_review_only_and_token_bound(self):
        self.assertIn('possibly fused not a',self.reasons('This is nota license.'))
        for text in ['notable annotation','This is not a license.']:
            self.assertNotIn('possibly fused not a',self.reasons(text))
        # Legitimate Latin is a review candidate, never an automatic edit.
        text='nota bene';find_ocr_punctuation_issues(text);self.assertEqual(text,'nota bene')

if __name__=='__main__':unittest.main()
