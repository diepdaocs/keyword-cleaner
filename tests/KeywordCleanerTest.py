# coding=utf-8
import unittest
from keyword_cleaner import KeywordCleaner


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.kw_cleaner = KeywordCleaner()

    def test_basic(self):
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

    def test_more(self):
        test_cases = (
            # Rule 1: Remove any of the following characters.. Replace with a space
            ("!=shoes'! = ? @ % ^ *; ~ `, (){} <> | [] \" - . ", 'shoes'),
            ("!=shoes'! = ? @ % ^ *; ~ `, (){}big@size<> | [] \" - . ", 'shoes big size'),

            # Rule 2: Remove all non-ascii characters. replace with space
            ('"blue shoes"', 'blue shoes'),
            ('[black shoes]', 'black shoes'),

            # Rule 3: Remove Tab found within the keyword strings. replace with space
            ('lovely        shoes   ', 'lovely shoes'),

            # Rule 4: Remove any string that matches the following.. replace with nothing
            # site:
            # url:
            # allinurl:
            # allintitle:
            ('watching movie on site:cnn.com allinurl: ', 'watching movie on cnn com'),
            ('check this url: url: to get help', 'check this to get help'),

            # Rule 5: Remove EXCESSIVE spaces .. meaning if more than 2 spaces found
            ('hello      world', 'hello world'),

            # Rule 6: Remove leading and trailing spaces (Trim)
            ('   hello   world   ', 'hello world')

        )
        for keyword, exp_clean_keyword in test_cases:
            self.assertEqual(self.kw_cleaner.clean(keyword), exp_clean_keyword)

if __name__ == '__main__':
    unittest.main()
