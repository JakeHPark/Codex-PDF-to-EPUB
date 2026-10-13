"""Check measurement behavior independently of book-specific font thresholds."""
import unittest

import numpy as np

from scan_styles import measure_word


class ScanStyleTest(unittest.TestCase):
    def stems(self, width, background=240, slant=0):
        image = np.full((80, 150), background, dtype=np.uint8)
        for y in range(10, 65):
            for x in (15, 45, 75, 105):
                left = x + round(slant * (79 - y))
                image[y, left:left + width] = 30
        return image

    def measure(self, image):
        return measure_word(image, (0, 0, 150, 80))

    def test_thick_strokes_survive_more_erosion(self):
        thin = self.measure(self.stems(3))
        thick = self.measure(self.stems(8))
        self.assertGreater(thick['stroke_survival'], thin['stroke_survival'] + .3)

    def test_paper_gray_does_not_become_ink(self):
        self.assertEqual(self.measure(self.stems(4, 120)), self.measure(self.stems(4)))
        blank = self.measure(np.full((80, 150), 120, dtype=np.uint8))
        self.assertEqual(blank['ink_pixels'], 0)

    def test_shear_distinguishes_slanted_from_upright_stems(self):
        upright = self.measure(self.stems(4))
        slanted = self.measure(self.stems(4, slant=.2))
        self.assertEqual(upright['slant'], 0)
        self.assertAlmostEqual(slanted['slant'], .2, delta=.05)
        self.assertGreater(slanted['gain'], .2)

    def test_empty_box_has_no_formatting_evidence(self):
        result = measure_word(self.stems(4), (200, 200, 220, 220))
        self.assertEqual(result['ink_pixels'], 0)
        self.assertEqual(result['stroke_survival'], 0)


if __name__ == '__main__':
    unittest.main()
