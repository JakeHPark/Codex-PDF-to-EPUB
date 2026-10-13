import unittest

from italic_markup import EM_START, EM_END, remove_verified_word_hyphens


class VerifiedHyphenTest(unittest.TestCase):
    def test_hyphen_across_style_boundary(self):
        text = 'Wil-' + EM_START + 'liamsburgy' + EM_END
        result = remove_verified_word_hyphens(text, {'Wil-liamsburgy': 'Williamsburgy'})
        self.assertEqual(result, 'Wil' + EM_START + 'liamsburgy' + EM_END)

    def test_whole_word_only_and_real_compounds_remain(self):
        self.assertEqual(remove_verified_word_hyphens(
            'sensitive sensi-tive xsensi-tive well-being', {'sensi-tive': 'sensitive'}),
            'sensitive sensitive xsensi-tive well-being')

    def test_non_hyphen_repair_rejected(self):
        with self.assertRaises(ValueError):
            remove_verified_word_hyphens('wrong', {'wrong': 'right'})


if __name__ == '__main__':
    unittest.main()
