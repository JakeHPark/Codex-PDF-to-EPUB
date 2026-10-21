#!/usr/bin/env python3
import unittest

from ocr_corrections import apply_common_ocr_corrections


class CommonOcrCorrectionsTest(unittest.TestCase):
    def test_slashes_for_italic_ll_require_complete_prose_token(self):
        self.assertEqual(apply_common_ocr_corrections('a// of them; (a//), a//—yes. a//'),
                         'all of them; (all), all—yes. all')
        source = 'a//b a//2 a // b /a// https://a//b call// a///b'
        self.assertEqual(apply_common_ocr_corrections(source), source)
    def test_fused_a_system_is_whole_token_only(self):
        self.assertEqual(
            apply_common_ocr_corrections("asystem... (Asystem). ecosystem parasystem asystems ASYSTEM"),
            "a system... (A system). ecosystem parasystem asystems ASYSTEM",
        )

    def test_fused_i_am_is_case_sensitive_whole_token_only(self):
        self.assertEqual(apply_common_ocr_corrections("Iam ready. (Iam here.) IAM Iams William iambic."),
                         "I am ready. (I am here.) IAM Iams William iambic.")

    def test_yoii_is_whole_token_only(self):
        self.assertEqual(apply_common_ocr_corrections('Yoii can; yoii will. Yoiiko ayoii.'),
                         'You can; you will. Yoiiko ayoii.')
    def test_double_quote_in_its_contraction(self):
        self.assertEqual(
            apply_common_ocr_corrections('It"s warm; it"s useful. transit"s'),
            "It's warm; it's useful. transit\"s",
        )

    def test_fused_it_is_is_a_whole_token_repair(self):
        self.assertEqual(
            apply_common_ocr_corrections("Itis clear; (Itis true). Otitis arthritis Itison."),
            "It is clear; (It is true). Otitis arthritis Itison.",
        )

    def test_mosi_is_a_whole_token_repair(self):
        self.assertEqual(apply_common_ocr_corrections("Mosi of them, mosi often. Mosiac mosiac osmosis."),
                         "Most of them, most often. Mosiac mosiac osmosis.")

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

    def test_false_internal_word_spaces(self):
        self.assertEqual(
            apply_common_ocr_corrections(
                "dan gerous claims encour aged the dom inant but imagina ble account"
            ),
            "dangerous claims encouraged the dominant but imaginable account",
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

    def test_doubled_single_curly_marks_become_double_quotes(self):
        self.assertEqual(
            apply_common_ocr_corrections("‘‘Quoted words,’’ then prose."),
            "“Quoted words,” then prose.",
        )

    def test_malformed_primary_double_quote_cluster(self):
        self.assertEqual(
            apply_common_ocr_corrections(
                "opposites “co-act,’” and (“all the world loves a lover,’”’ because)"
            ),
            "opposites “co-act,” and (“all the world loves a lover,” because)",
        )

    def test_valid_nested_single_quote_is_untouched(self):
        source = "“He called it ‘no,’” she said."
        self.assertEqual(apply_common_ocr_corrections(source), source)

    def test_quote_cleanup_does_not_consume_layout_marker_evidence(self):
        source = "“Nothing better.’”°"
        self.assertEqual(apply_common_ocr_corrections(source), source)


if __name__ == "__main__":
    unittest.main()
