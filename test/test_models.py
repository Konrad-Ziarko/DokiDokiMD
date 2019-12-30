import os
import unittest

from dokidokimd.models import Chapter, Manga, MangaSite


RESULTS_DIRECTORY = 'unittest_results_temp_dir'


class TestChapterMethods(unittest.TestCase):
    def test_chapter_1(self):
        dummy_manga_site = MangaSite('test_site')
        dummy_manga = Manga('test_manga', 'test_manga_url', dummy_manga_site)

        dummy_chapter1 = Chapter(dummy_manga)
        self.assertTrue(dummy_chapter1.number_of_pages() == 0)
        self.assertIsNone(dummy_chapter1.title)

        dummy_chapter2 = Chapter(dummy_manga, 'test_chapter_title')
        self.assertTrue(dummy_chapter2.title == 'test_chapter_title')
        dummy_chapter2.set_downloaded(True)
        self.assertTrue(dummy_chapter2.downloaded)
        self.assertTrue(dummy_chapter2.in_memory)
        dummy_chapter2.clear_state()
        self.assertFalse(dummy_chapter2.downloaded)
        self.assertFalse(dummy_chapter2.in_memory)
        try:
            dummy_chapter2.get_download_path(os.getcwd())
        except Exception as e:
            self.assertIsInstance(e, AttributeError)
            self.assertTrue("NoneType" in str(e))
        dump = dummy_chapter2.dump()
        self.assertIsInstance(dump, bytes)
        self.assertTrue(len(dump) > 0)


class TestMangaMethods(unittest.TestCase):
    def test_manga_1(self):
        dummy_manga_site = MangaSite('test_site')
        dummy_manga1 = Manga('test_manga', 'test_manga_url', dummy_manga_site)

        self.assertTrue(dummy_manga1.title == 'test_manga')
        dummy_manga1.downloaded = True
        self.assertTrue(dummy_manga1.downloaded)

        dummy_chapter1 = Chapter(dummy_manga1)
        dummy_manga1.add_chapter(dummy_chapter1)
        self.assertTrue(len(dummy_manga1.chapters) > 0)
        dummy_manga1.clear_state()
        self.assertFalse(dummy_manga1.downloaded)
        self.assertTrue(len(dummy_manga1.chapters) == 0)
        try:
            dummy_manga1.get_download_path(os.getcwd())
        except Exception as e:
            self.assertIsInstance(e, AttributeError)
            self.assertTrue("NoneType" in str(e))
        dump = dummy_manga1.dump()
        self.assertIsInstance(dump, bytes)
        self.assertTrue(len(dump) > 0)


class TestMangaSiteMethods(unittest.TestCase):
    def test_manga_site_1(self):
        dummy_manga_site1 = MangaSite()
        self.assertIsNone(dummy_manga_site1.site_name)

        dummy_manga_site2 = MangaSite('test_site')
        dummy_manga1 = Manga('test_manga', 'test_manga_url', dummy_manga_site2)

        dummy_manga_site2.add_manga(dummy_manga1)
        self.assertTrue(len(dummy_manga_site2.mangas) > 0)
        dummy_manga_site2.clear_state()
        self.assertTrue(len(dummy_manga_site2.mangas) == 0)
        dump = dummy_manga_site2.dump()
        self.assertIsInstance(dump, bytes)
        self.assertTrue(len(dump) > 0)


if __name__ == '__main__':
    unittest.main()
