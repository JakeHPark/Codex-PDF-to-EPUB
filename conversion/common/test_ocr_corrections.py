#!/usr/bin/env python3
import unittest

from ocr_corrections import apply_common_ocr_corrections


class CommonOcrCorrectionsTest(unittest.TestCase):
    def test_fused_in_a_preserves_case_and_names(self):
        source = "Ina sense, Anna Karenina was ina difficult position."
        self.assertEqual(
            apply_common_ocr_corrections(source),
            "In a sense, Anna Karenina was in a difficult position.",
        )

    def test_fused_pronoun_and_compound(self):
        self.assertEqual(
            apply_common_ocr_corrections("Ihave sought selfknowledge."),
            "I have sought self-knowledge.",
        )

    def test_exact_dictionary(self):
        self.assertEqual(
            apply_common_ocr_corrections("Their factbased teligion was mest prodigious."),
            "Their fact-based religion was most prodigious.",
        )

    def test_whole_token_dictionary(self):
        self.assertEqual(
            apply_common_ocr_corrections("It restedupon a shelf upona table."),
            "It restedupon a shelf upon a table.",
        )

    def test_impossible_triple_opening_quote(self):
        self.assertEqual(
            apply_common_ocr_corrections("‘““Quoted words”"),
            "“Quoted words”",
        )


if __name__ == "__main__":
    unittest.main()
