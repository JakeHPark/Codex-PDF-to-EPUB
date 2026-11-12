import unittest
import xml.etree.ElementTree as E

from conversion.common.navigation import heading_label, validate_toc


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


class NavigationTests(unittest.TestCase):
    def root(self, entries):
        return E.fromstring('<html xmlns="http://www.w3.org/1999/xhtml" '
                            'xmlns:epub="http://www.idpf.org/2007/ops"><body>'
                            '<nav epub:type="toc"><ol>'+entries+'</ol></nav></body></html>')

    def test_nested_direct_links_and_span_branch(self):
        root=self.root('<li><a href="c.xhtml">Chapter</a><ol><li><span>Group</span>'
                       '<ol><li><a href="c.xhtml#s"><em>Section</em></a></li></ol>'
                       '</li></ol></li>')
        self.assertEqual(validate_toc(root),2)

    def test_image_label_keeps_accessible_alternative(self):
        self.assertEqual(validate_toc(self.root('<li><a href="c.xhtml">'
                         '<img src="icon.png" alt="Chapter"/></a></li>')),1)

    def test_paragraph_wrapped_links_rejected(self):
        with self.assertRaisesRegex(ValueError,'direct a/span'):
            validate_toc(self.root('<li><p><a href="c.xhtml">Chapter</a></p></li>'))

    def test_empty_labels_and_destinations_rejected(self):
        for entry in ['<li><a href="c.xhtml"> </a></li>', '<li><a>Chapter</a></li>',
                      '<li><span>Chapter</span></li>', '<p>Chapter</p>']:
            with self.subTest(entry=entry),self.assertRaises(ValueError):
                validate_toc(self.root(entry))

    def test_multiple_child_lists_rejected(self):
        with self.assertRaisesRegex(ValueError,'one nested list'):
            validate_toc(self.root('<li><a href="c.xhtml">Chapter</a>'
                         '<ol><li><a href="c.xhtml#one">One</a></li></ol>'
                         '<ol><li><a href="c.xhtml#two">Two</a></li></ol></li>'))

    def test_nested_entry_cannot_hide_bad_label(self):
        with self.assertRaisesRegex(ValueError,'direct a/span'):
            validate_toc(self.root('<li><a href="c.xhtml">Chapter</a><ol>'
                                   '<li><p><a href="c.xhtml#s">Section</a></p></li></ol></li>'))


if __name__ == '__main__':
    unittest.main()
