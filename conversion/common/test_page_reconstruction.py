"""Paragraph indentation must be measured from content, not its hanging marker."""
import unittest
from conversion.common.page_reconstruction import starts_indented_paragraph

class HangingParagraphTests(unittest.TestCase):
    def test_wrapped_note_does_not_start_paragraph_after_number(self):
        # Number at x=36, first-line text and wrapped prose at x=54.
        self.assertFalse(starts_indented_paragraph(54, body_left=54))
        self.assertFalse(starts_indented_paragraph(55, body_left=54))

    def test_genuine_second_paragraph_is_retained(self):
        self.assertTrue(starts_indented_paragraph(66, body_left=54))
        self.assertTrue(starts_indented_paragraph(65.2, body_left=54))

    def test_alternating_page_margins(self):
        for edge in (54.432, 55.488):
            self.assertFalse(starts_indented_paragraph(edge, body_left=edge))
            self.assertTrue(starts_indented_paragraph(edge+12, body_left=edge))

    def test_deeper_hanging_list_uses_its_own_content_edge(self):
        self.assertFalse(starts_indented_paragraph(72, body_left=72))
        self.assertTrue(starts_indented_paragraph(84, body_left=72))

if __name__ == '__main__':
    unittest.main()
