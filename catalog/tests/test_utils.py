from django.test import SimpleTestCase
from catalog.utils import extract_chapter_number

class ExtractChapterNumberTest(SimpleTestCase):
    def test_explicit_chapter_formats(self):
        self.assertEqual(extract_chapter_number("Chapter 12.zip"), 12.0)
        self.assertEqual(extract_chapter_number("ch.12.cbz"), 12.0)
        self.assertEqual(extract_chapter_number("ch12.pdf"), 12.0)
        self.assertEqual(extract_chapter_number("c12.zip"), 12.0)
        self.assertEqual(extract_chapter_number("chap 12.5.zip"), 12.5)

    def test_implicit_chapter_formats(self):
        self.assertEqual(extract_chapter_number("One Piece 1000.zip"), 1000.0)
        self.assertEqual(extract_chapter_number("Naruto 50.5.cbz"), 50.5)
        self.assertEqual(extract_chapter_number("012.zip"), 12.0)
        
    def test_complex_filenames(self):
        self.assertEqual(extract_chapter_number("[Group] Series Name - 012 [Hash].zip"), 12.0)
        self.assertEqual(extract_chapter_number("Series Name v1 ch2.5.zip"), 2.5)
        # Fallback to last number if no explicit chapter marker
        self.assertEqual(extract_chapter_number("Series 2023 05.zip"), 5.0) 

    def test_no_number(self):
        self.assertIsNone(extract_chapter_number("credits.txt"))
        self.assertIsNone(extract_chapter_number("logo.png"))
