"""Read Tesseract TSV without interpreting recognized prose as CSV quoting."""
from pathlib import Path


def read_tesseract_tsv(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("Empty Tesseract TSV")
    header = lines[0].split("\t")
    if header[-1] != "text" or len(header) != 12:
        raise ValueError("Unexpected Tesseract TSV header")
    rows = []
    for number, line in enumerate(lines[1:], 2):
        cells = line.split("\t", 11)
        if len(cells) != 12:
            raise ValueError(f"Malformed Tesseract TSV row {number}")
        rows.append(dict(zip(header, cells)))
    return rows
