#!/usr/bin/env python3
"""Detect likely italic OCR words by measuring glyph slant in page pixels.

This is intended for scanned books whose OCR exposes word bounding boxes but
does not retain reliable font metadata. Its JSON output is evidence for review,
not permission to alter prose without checking the rendered source page.
"""

import argparse
import json
import re
from pathlib import Path

from PIL import Image
from lxml import html

BBOX_RE = re.compile(r"\bbbox (\d+) (\d+) (\d+) (\d+)\b")


def word_elements(document):
    return document.xpath(
        '//*[contains(concat(" ", normalize-space(@class), " "), " ocrx_word ")]'
    )


def line_id(element):
    line = element.getparent()
    while line is not None:
        classes = (line.get("class") or "").split()
        if "ocr_line" in classes:
            return line.get("id") or ""
        line = line.getparent()
    return ""


def slant_measure(image, bbox, threshold, max_slant, step):
    x0, y0, x1, y1 = bbox
    crop = image.crop((x0, y0, x1, y1))
    width, height = crop.size
    ink = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if crop.getpixel((x, y)) < threshold
    ]
    if not ink or height < 5:
        return 0.0, 0.0, len(ink)

    def projection_score(slant):
        # Italic type in these left-to-right books leans right, so the batch
        # workflow searches zero and positive corrections only. A dense list
        # is materially faster than a dictionary for page-scale analysis.
        offset = round(slant * (height - 1)) + 1
        columns = [0] * (width + offset + 2)
        for x, y in ink:
            corrected_x = round(x - slant * (height - 1 - y)) + offset
            columns[corrected_x] += 1
        return sum(value * value for value in columns) / len(ink)

    zero_score = projection_score(0.0)
    steps = round(max_slant / step)
    candidates = [
        (projection_score(index * step), index * step)
        for index in range(steps + 1)
    ]
    best_score, best_slant = max(candidates)
    gain = (best_score / zero_score - 1.0) if zero_score else 0.0
    return best_slant, gain, len(ink)


def detect(args):
    image = Image.open(args.image).convert("L")
    document = html.parse(str(args.hocr))
    words = []
    for element in word_elements(document):
        text = "".join(element.itertext()).strip()
        match = BBOX_RE.search(element.get("title", ""))
        if not text or not match:
            continue
        bbox = tuple(map(int, match.groups()))
        slant, gain, ink_pixels = slant_measure(
            image, bbox, args.threshold, args.max_slant, args.step
        )
        alphabetic = sum(character.isalpha() for character in text)
        long_word = (
            alphabetic >= args.min_chars
            and slant >= args.min_slant
            and gain >= args.min_gain
        )
        # Very short words contain too little geometry for the ordinary
        # threshold, but strongly slanted examples are still recoverable.
        # Keep this deliberately stricter than the long-word test.
        short_word = (
            args.short_min_chars <= alphabetic < args.min_chars
            and slant >= args.short_min_slant
            and gain >= args.short_min_gain
        )
        likely = long_word or short_word
        words.append(
            {
                "text": text,
                "line": line_id(element),
                "bbox": bbox,
                "slant": round(slant, 4),
                "gain": round(gain, 4),
                "ink_pixels": ink_pixels,
                "likely_italic": likely,
            }
        )

    # A short word inside an otherwise italic run is hard to classify alone.
    # Promote it only when both immediate neighbors on the same OCR line agree.
    for index in range(1, len(words) - 1):
        current, previous, following = words[index], words[index - 1], words[index + 1]
        if (
            not current["likely_italic"]
            and current["line"] == previous["line"] == following["line"]
            and previous["likely_italic"]
            and following["likely_italic"]
        ):
            current["likely_italic"] = True
            current["inferred_from_neighbors"] = True

    spans = []
    active = []
    for word in words:
        if word["likely_italic"]:
            if active and word["line"] != active[-1]["line"]:
                spans.append(active)
                active = []
            active.append(word)
        elif active:
            spans.append(active)
            active = []
    if active:
        spans.append(active)

    result = {
        "method": "hocr-word-box pixel-slant projection",
        "image": str(args.image),
        "hocr": str(args.hocr),
        "parameters": {
            "threshold": args.threshold,
            "min_chars": args.min_chars,
            "min_slant": args.min_slant,
            "min_gain": args.min_gain,
            "short_min_chars": args.short_min_chars,
            "short_min_slant": args.short_min_slant,
            "short_min_gain": args.short_min_gain,
            "max_slant": args.max_slant,
            "step": args.step,
        },
        "spans": [
            {
                "line": span[0]["line"],
                "text": " ".join(word["text"] for word in span),
                "words": span,
            }
            for span in spans
        ],
    }
    if args.include_all_words:
        result["words"] = words
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Rendered page image used for OCR")
    parser.add_argument("hocr", type=Path, help="Tesseract hOCR for the same image")
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--threshold", type=int, default=150)
    parser.add_argument("--min-chars", type=int, default=4)
    parser.add_argument("--min-slant", type=float, default=0.08)
    parser.add_argument("--min-gain", type=float, default=0.07)
    parser.add_argument("--short-min-chars", type=int, default=2)
    parser.add_argument("--short-min-slant", type=float, default=0.15)
    parser.add_argument("--short-min-gain", type=float, default=0.15)
    parser.add_argument("--max-slant", type=float, default=0.45)
    parser.add_argument("--step", type=float, default=0.05)
    parser.add_argument("--include-all-words", action="store_true")
    args = parser.parse_args()
    result = detect(args)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
