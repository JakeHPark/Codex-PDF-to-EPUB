#!/usr/bin/env python3
"""Render, OCR, and classify italic candidates for a range of PDF pages.

Each page is written independently so an interrupted whole-book run can resume.
Rendered images and hOCR are temporary; the compact JSON evidence is retained.
"""

import argparse
import concurrent.futures
import json
import os
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

from detect_italics import detect


def analyze_page(job):
    page, config = job
    output = Path(config["output"]) / f"{page:04d}.json"
    if output.exists() and output.stat().st_size > 200:
        return page, "cached", 0
    with tempfile.TemporaryDirectory(prefix=f"italic-page-{page}-", dir="/tmp") as temp:
        stem = Path(temp) / "page"
        image = stem.with_suffix(".png")
        hocr_stem = Path(temp) / "ocr"
        hocr = hocr_stem.with_suffix(".hocr")
        subprocess.run(
            [
                config["pdftoppm"], "-f", str(page), "-l", str(page),
                "-r", str(config["dpi"]), "-gray", "-png", "-singlefile",
                config["pdf"], str(stem),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        environment = os.environ.copy()
        environment["TESSDATA_PREFIX"] = config["tessdata"]
        subprocess.run(
            [
                config["tesseract"], str(image), str(hocr_stem), "-l", "eng",
                "--psm", "3", "-c", "tessedit_create_hocr=1",
                "-c", "hocr_font_info=1",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=environment,
        )
        arguments = SimpleNamespace(
            image=image,
            hocr=hocr,
            threshold=config["threshold"],
            min_chars=4,
            min_slant=0.08,
            min_gain=0.07,
            short_min_chars=2,
            short_min_slant=0.15,
            short_min_gain=0.15,
            max_slant=0.35,
            step=0.05,
            include_all_words=True,
        )
        result = detect(arguments)
        result["page"] = page
        result["dpi"] = config["dpi"]
        result["image"] = f"temporary-render:pdf-page-{page}"
        result["hocr"] = f"temporary-hocr:pdf-page-{page}"
        candidates = sum(word["likely_italic"] for word in result["words"])
        temporary = output.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output)
    return page, "done", candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--first-page", type=int, required=True)
    parser.add_argument("--last-page", type=int, required=True)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--threshold", type=int, default=150)
    parser.add_argument("--pdftoppm", default="/run/current-system/sw/bin/pdftoppm")
    parser.add_argument("--tesseract", required=True)
    parser.add_argument("--tessdata", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    config = {
        "pdf": str(args.pdf.resolve()),
        "output": str(args.output.resolve()),
        "dpi": args.dpi,
        "threshold": args.threshold,
        "pdftoppm": args.pdftoppm,
        "tesseract": args.tesseract,
        "tessdata": str(args.tessdata.resolve()),
    }
    pages = range(args.first_page, args.last_page + 1)
    total_candidates = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = ((page, config) for page in pages)
        for completed, (page, status, candidates) in enumerate(
            pool.map(analyze_page, jobs), 1
        ):
            total_candidates += candidates
            if completed % 20 == 0 or page == args.last_page:
                print(
                    f"page {page}/{args.last_page} ({status}); "
                    f"{total_candidates} candidates so far",
                    flush=True,
                )


if __name__ == "__main__":
    main()
