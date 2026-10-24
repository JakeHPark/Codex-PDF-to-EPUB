import unittest
import xml.etree.ElementTree as E

from conversion.common.navigation import heading_label


class HeadingLabelTests(unittest.TestCase):
    def test_middle_reference_preserves_tail_and_styles(self):
        h = E.fromstring('<h2 xmlns:epub="http://www.idpf.org/2007/ops">'
                         '<em>A title</em><a epub:type="noteref" href="#n">'
                         '<sup>12</sup></a> with <strong>more words</strong></h2>')
        before = E.tostring(h)
        self.assertEqual(heading_label(h), 'A title with more words')
        self.assertEqual(E.tostring(h), before)

    def test_terminal_and_role_references(self):
        h = E.fromstring('<h2>Title<a role="doc-noteref">3</a></h2>')
        self.assertEqual(heading_label(h), 'Title')

    def test_real_numbers_and_ordinary_superscripts_survive(self):
        h = E.fromstring('<h2>Figure 3: Life in 1984 and x<sup>2</sup></h2>')
        self.assertEqual(heading_label(h), 'Figure 3: Life in 1984 and x2')


if __name__ == '__main__':
    unittest.main()
