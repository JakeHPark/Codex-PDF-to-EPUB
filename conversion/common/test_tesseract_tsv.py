import tempfile
import unittest
from pathlib import Path

from conversion.common.tesseract_tsv import read_tesseract_tsv


class TesseractTSVTests(unittest.TestCase):
    def test_recognized_quotes_are_literal_and_do_not_swallow_following_rows(self):
        header = "level page_num block_num par_num line_num word_num left top width height conf text".split()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ocr.tsv"
            path.write_text("\t".join(header) + "\n" + "\n".join(
                "\t".join(["5", "1", "1", "1", "1", str(i), "20", "30", "40", "50", "90", text])
                for i, text in enumerate(['"', 'next', '"quoted"', 'last'], 1)
            ) + "\n")
            rows = read_tesseract_tsv(path)
            self.assertEqual([row["text"] for row in rows], ['"', 'next', '"quoted"', 'last'])
            self.assertEqual(len(rows), 4)


if __name__ == "__main__":
    unittest.main()
