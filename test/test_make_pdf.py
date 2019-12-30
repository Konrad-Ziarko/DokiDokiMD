import os
import shutil
import unittest

from dokidokimd.models import Chapter, Manga, MangaSite
RESULTS_DIRECTORY = 'unittest_results_temp_dir'


class TestMakePdfMethods(unittest.TestCase):
    def test_make_pdf1(self):
        """
        Make pdf from previously downloaded images - simulated on copied files
        """
        directory_name = os.path.dirname(__file__)
        dummy_manga_site = MangaSite('test_site')
        dummy_manga = Manga('test_manga', 'test_manga_url', dummy_manga_site)
        dummy_chapter = Chapter(dummy_manga, 'test_chapter_title')

        self.assertTrue(dummy_chapter.number_of_pages() == 0)

        source_images_dir = os.path.join(directory_name, 'images')
        test_tmp_dir = os.path.join(directory_name, RESULTS_DIRECTORY)
        images_dir = dummy_chapter.get_download_path(test_tmp_dir)
        os.makedirs(images_dir, exist_ok=True)
        for file in os.listdir(source_images_dir):
            file_path = os.path.join(source_images_dir, file)
            if os.path.isfile(file_path):
                shutil.copy(file_path, images_dir)
        result, path_to_pdf = dummy_chapter.make_pdf(test_tmp_dir)

        self.assertTrue(result)
        self.assertTrue(dummy_chapter.number_of_pages() == 0)
        self.assertTrue(os.path.isfile(path_to_pdf))
        self.assertTrue(os.path.getsize(path_to_pdf) > 0)
        os.unlink(path_to_pdf)
        shutil.rmtree(test_tmp_dir, ignore_errors=True)

    def test_make_pdf2(self):
        """
        Make pdf from pages in memory - simulated by manually added pages
        """
        directory_name = os.path.dirname(__file__)
        dummy_manga_site = MangaSite('test_site')
        dummy_manga = Manga('test_manga', 'test_manga_url', dummy_manga_site)
        dummy_chapter = Chapter(dummy_manga, 'test_chapter_title')

        self.assertTrue(dummy_chapter.number_of_pages() == 0)

        source_images_dir = os.path.join(directory_name, 'images')
        test_tmp_dir = os.path.join(directory_name, RESULTS_DIRECTORY)
        for file in os.listdir(source_images_dir):
            file_path = os.path.join(source_images_dir, file)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    dummy_chapter.add_page(f.read())
        result, path_to_pdf = dummy_chapter.make_pdf(test_tmp_dir)

        self.assertTrue(result)
        self.assertTrue(dummy_chapter.number_of_pages() == 4)
        self.assertTrue(os.path.isfile(path_to_pdf))
        self.assertTrue(os.path.getsize(path_to_pdf) > 0)
        os.unlink(path_to_pdf)
        shutil.rmtree(test_tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
