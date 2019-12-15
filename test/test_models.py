import os
import unittest

from dokidokimd.models import Chapter, Manga, MangaSite


RESULTS_DIRECTORY = 'unittest_results_temp_dir'


class TestChapterMethods(unittest.TestCase):
    def test_chapter_1(self):
        chapter = Chapter()
        self.assertIsNone(chapter.title)
        chapter2 = Chapter('test_title')
        self.assertTrue(chapter2.title == 'test_title')
        chapter2.set_downloaded(True)
        self.assertTrue(chapter2.downloaded)
        self.assertTrue(chapter2.in_memory)
        chapter2.clear_state()
        self.assertFalse(chapter2.downloaded)
        self.assertFalse(chapter2.in_memory)
        try:
            chapter2.get_download_path(os.getcwd())
        except Exception as e:
            self.assertIsInstance(e, AttributeError)
            self.assertTrue("NoneType" in str(e))
        dump = chapter2.dump()
        self.assertIsInstance(dump, bytes)
        self.assertTrue(len(dump) > 0)


class TestMangaMethods(unittest.TestCase):
    def test_manga_1(self):
        manga = Manga()
        self.assertIsNone(manga.title)
        manga2 = Manga('test_title')
        self.assertTrue(manga2.title == 'test_title')
        manga2.downloaded = True
        self.assertTrue(manga2.downloaded)
        chapter = Chapter()
        manga2.add_chapter(chapter)
        self.assertTrue(len(manga2.chapters) > 0)
        manga2.clear_state()
        self.assertFalse(manga2.downloaded)
        self.assertTrue(len(manga2.chapters) == 0)
        try:
            manga2.get_download_path(os.getcwd())
        except Exception as e:
            self.assertIsInstance(e, AttributeError)
            self.assertTrue("NoneType" in str(e))
        dump = manga2.dump()
        self.assertIsInstance(dump, bytes)
        self.assertTrue(len(dump) > 0)


class TestMangaSiteMethods(unittest.TestCase):
    def test_manga_site_1(self):
        manga_site = MangaSite()
        self.assertIsNone(manga_site.site_name)
        manga = Manga()
        manga_site.add_manga(manga)
        self.assertTrue(len(manga_site.mangas) > 0)
        manga_site.clear_state()
        self.assertTrue(len(manga_site.mangas) == 0)
        dump = manga_site.dump()
        self.assertIsInstance(dump, bytes)
        self.assertTrue(len(dump) > 0)


if __name__ == '__main__':
    unittest.main()
