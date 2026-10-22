#!/usr/bin/env python3
import tempfile
import unittest
import zipfile
from pathlib import Path

from endnote_recovery import index_records_by_page, replace_visible_token
from epub_quality import find_endnote_like_punctuation, find_typographic_quote_issues, validate_epub_policies
from page_reconstruction import drop_detached_boundary_debris
from section_boundaries import strip_opening_display_blocks


class EndnoteRecoveryTest(unittest.TestCase):
    def test_multiple_markers_on_one_page_keep_distinct_ordinals(self):
        indexed = index_records_by_page([
            {"page": 12, "raw_token": "one.’", "selected": "4", "reviewed": True},
            {"page": 12, "raw_token": "two.’", "selected": "5", "reviewed": True},
        ])
        self.assertEqual([record["ordinal"] for record in indexed[12]], [1, 2])

    def test_replacement_preserves_inline_markers(self):
        self.assertEqual(
            replace_visible_token(
                "word\ue100s\ue101.’ end", "words.’", "words.", "<NOTE>",
                page=1, inline_markers=("\ue100", "\ue101"),
            ),
            "word\ue100s\ue101.<NOTE> end",
        )


class PageBoundaryTest(unittest.TestCase):
    def test_detached_fragment_before_heading_is_removed(self):
        previous, removed = drop_detached_boundary_debris(
            "15. A complete note.\n\nPS", "CHAPTER 11. THE WINTER’S TALE\n\n1. Note"
        )
        self.assertEqual(previous, "15. A complete note.")
        self.assertEqual(removed, ["PS"])

    def test_fragment_before_prose_is_preserved(self):
        previous, removed = drop_detached_boundary_debris("A paragraph.\n\nPS", "More prose")
        self.assertEqual(previous, "A paragraph.\n\nPS")
        self.assertEqual(removed, [])


class GeneratedHeadingTest(unittest.TestCase):
    def test_main_title_and_subtitle_are_both_removed(self):
        source = (
            "Interlude on\nTwo Strange Couples:\n\n"
            "Hal and Falstaff, Montaigne and La Boétie\n\n"
            "As a farewell to Shakespeare, we will look at one connection."
        )
        body, removed = strip_opening_display_blocks(
            source,
            "Interlude on Two Strange Couples: Hal and Falstaff, Montaigne and La Boétie",
        )
        self.assertEqual(len(removed), 2)
        self.assertTrue(body.startswith("As a farewell to Shakespeare"))

    def test_opening_prose_is_not_removed(self):
        body, removed = strip_opening_display_blocks(
            "1. A Chapter\n\nActual prose starts here.", "1. A Chapter"
        )
        self.assertEqual(len(removed), 1)
        self.assertEqual(body, "Actual prose starts here.")


class QuoteAuditTest(unittest.TestCase):
    def test_possessive_in_nested_title_does_not_hide_missing_closer(self):
        self.assertEqual(find_typographic_quote_issues('“The name is called ‘Haddocks’ Eyes.’”'), [])
        self.assertTrue(find_typographic_quote_issues('“The name is called ‘Haddocks’ Eyes.”'))
        self.assertEqual(find_typographic_quote_issues('“She called it ‘James’ Book’ yesterday.”'), [])

    def test_valid_nested_quotes_pass(self):
        self.assertEqual(find_typographic_quote_issues("“He called it ‘no,’” she said."), [])

    def test_contractions_do_not_close_nested_quotes(self):
        self.assertEqual(find_typographic_quote_issues("“He said, ‘No. I’m busy.’ Just like that.”"), [])
        self.assertEqual(find_typographic_quote_issues("“‘We’re going to talk,’ she said.”"), [])

    def test_mismatched_single_inside_double_is_flagged(self):
        issues = find_typographic_quote_issues("opposites “co-act,’” and")
        self.assertTrue(any(issue.character == "’" for issue in issues))

    def test_corrupt_lovers_cluster_is_flagged(self):
        issues = find_typographic_quote_issues("(“all the world loves a lover,’”’ because)")
        self.assertGreaterEqual(len(issues), 2)

    def test_unclosed_reporting_can_be_deferred_at_section_boundaries(self):
        self.assertEqual(
            find_typographic_quote_issues("“continued quotation", report_unclosed=False),
            [],
        )

    def test_endnote_candidate_inventory_does_not_rewrite(self):
        self.assertIn("attached.’", find_endnote_like_punctuation("a person is attached.’ Then"))

    def test_elisions_and_abbreviation_possessives_are_apostrophes(self):
        self.assertEqual(
            find_typographic_quote_issues("’Twixt the Ph.D.’s two choices."),
            [],
        )


class PackagedPolicyTest(unittest.TestCase):
    def test_front_marker_and_broken_link_policies(self):
        with tempfile.TemporaryDirectory() as directory:
            epub = Path(directory) / "test.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("OEBPS/body.xhtml", '<a epub:type="noteref" href="notes.xhtml#n1"><sup>1</sup></a>')
                archive.writestr("OEBPS/notes.xhtml", '<p id="n1">1. Note</p>')
            validate_epub_policies(
                epub, expected_note_references=1, audit_typographic_quotes=True
            )

    def test_quote_audit_can_write_a_nonblocking_review_queue(self):
        with tempfile.TemporaryDirectory() as directory:
            epub = Path(directory) / "test.epub"
            report = Path(directory) / "quotes.json"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("OEBPS/body.xhtml", "<p>opposites “co-act,’” and</p>")
            validate_epub_policies(epub, quote_issue_report=report)
            self.assertIn('"count":', report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
