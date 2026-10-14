import unittest
from lxml import etree
from prose_spacing import normalize_prose_spacing, normalize_xhtml_prose_spacing


class ProseSpacingTests(unittest.TestCase):
    def test_word_before_opening_double_quote(self):
        self.assertEqual(normalize_prose_spacing('the word“number”'), 'the word “number”')
        self.assertEqual(normalize_prose_spacing('λέξη“number”'), 'λέξη “number”')

    def test_sentence_stop(self):
        self.assertEqual(normalize_prose_spacing('conceptual confusion . Next.'), 'conceptual confusion. Next.')
        self.assertEqual(normalize_prose_spacing('called “confusion”\u00a0.'), 'called “confusion”.')

    def test_legitimate_notation_and_quotes(self):
        s = 'He said “no”. A word . . . another; . .. ...; 3 . 14; x .5; E.g. “yes”; John’s book.'
        self.assertEqual(normalize_prose_spacing(s), s)

    def test_markup_boundaries_preserve_emphasis(self):
        p = etree.fromstring('<p>the <em>word</em>“number” and <em>conceptual confusion</em> .</p>')
        self.assertEqual(normalize_xhtml_prose_spacing(p), 2)
        self.assertEqual(''.join(p.itertext()), 'the word “number” and conceptual confusion.')
        self.assertEqual(p[1].text, 'conceptual confusion')
        self.assertEqual(normalize_xhtml_prose_spacing(p), 0)

    def test_formula_classes_and_images_are_barriers(self):
        root = etree.fromstring('<div><p>word<img src="x"/>“sample”</p><p><span class="math">x .</span> .</p></div>')
        self.assertEqual(normalize_xhtml_prose_spacing(root), 0)

    def test_excluded_objects_and_nested_blocks(self):
        root = etree.fromstring('<div><li><p>word“one” .</p></li><p><code>x“y” .</code> <math>x .</math></p><pre><p>word“two” .</p></pre></div>')
        self.assertEqual(normalize_xhtml_prose_spacing(root), 2)
        self.assertEqual(root.find('.//code').text, 'x“y” .')
        self.assertEqual(root.find('.//pre/p').text, 'word“two” .')


if __name__ == '__main__':
    unittest.main()
