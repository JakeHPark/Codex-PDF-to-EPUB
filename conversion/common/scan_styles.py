"""Pixel evidence for scanned-book bold and italics, independent of OCR fonts.

Coordinates must refer to the supplied grayscale image. These measurements
are evidence, not universal classification thresholds: calibrate against
verified roman/bold/italic examples at the same rendering scale and type size.
"""

import numpy as np


def measure_word(image, bbox, *, threshold=155, background_margin=45):
    x0, y0, x1, y1 = map(round, bbox)
    crop = np.asarray(image)[max(0, y0 - 3):y1 + 3, max(0, x0 - 2):x1 + 2]
    if crop.size == 0 or min(crop.shape) < 5:
        return {"stroke_survival": 0.0, "slant": 0.0, "gain": 0.0, "ink_pixels": 0}
    cutoff = min(threshold, float(np.percentile(crop, 90)) - background_margin)
    ink = crop < cutoff
    count = int(ink.sum())
    if count < 10:
        return {"stroke_survival": 0.0, "slant": 0.0, "gain": 0.0, "ink_pixels": count}
    # One-pixel four-neighbor erosion measures the fraction of interior ink.
    # Thick strokes retain more interior pixels than thin strokes. Unlike
    # raw density, this is less dependent on the letters present in a word.
    interior = (ink[1:-1, 1:-1] & ink[:-2, 1:-1] & ink[2:, 1:-1]
                & ink[1:-1, :-2] & ink[1:-1, 2:])
    ys, xs = np.nonzero(ink)
    height, width = ink.shape
    scores = []
    for slant in np.arange(0, 0.351, 0.05):
        columns = np.rint(xs - slant * (height - 1 - ys)).astype(int)
        columns -= columns.min()
        projection = np.bincount(columns)
        scores.append(float(np.dot(projection, projection)) / count)
    best = int(np.argmax(scores))
    return {
        "stroke_survival": round(float(interior.sum()) / count, 4),
        "slant": round(best * 0.05, 4),
        "gain": round(scores[best] / scores[0] - 1, 4),
        "ink_pixels": count,
    }
