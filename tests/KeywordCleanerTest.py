# coding=utf-8
import unittest
from keyword_cleaner import KeywordCleaner


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.kw_cleaner = KeywordCleaner()

    def test(self):
        test_cases = (
            ("!=shoes'", 'shoes', 5, 1),
            ('"blue shoes"', 'blue shoes', 10, 2),
            ('[black shoes]', 'black shoes', 11, 2),
            ('green      shoes', 'green shoes', 11, 2),
            ('©2012', '2012', 4, 1),
            ('• silver', 'silver', 6, 1)
        )
        for keyword, exp_cleaned_keyword, exp_char_count, exp_word_count in test_cases:
            stats = self.kw_cleaner.process(keyword)

            original = stats['original']
            cleaned = stats['cleaned']
            char_count = stats['char_count']
            word_count = stats['word_count']

            self.assertEqual(original, keyword)
            self.assertEqual(cleaned, exp_cleaned_keyword)
            self.assertEqual(char_count, exp_char_count)
            self.assertEqual(word_count, exp_word_count)

if __name__ == '__main__':
    unittest.main()
