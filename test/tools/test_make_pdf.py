import unittest
from os import unlink, rmdir
from os.path import dirname, join, isfile, getsize

from dokidokimd.tools.make_pdf import PDF

RESULTS_DIRECTORY = 'unittest_results_temp_dir'


class TestMakePdfMethods(unittest.TestCase):
    def test_make_pdf1(self):
        """
        Correct usage
        """
        directory_name = dirname(__file__)
        pdf = PDF()

        self.assertTrue(len(pdf.files_list) == 0)
        pdf.add_dir(join(directory_name, 'images'))
        self.assertTrue(len(pdf.files_list) == 4)

        pdf_dir = join(directory_name, RESULTS_DIRECTORY)
        pages = pdf.make_pdf('test', join(pdf_dir, 'test_result.pdf'))

        self.assertTrue(pages == 4)
        self.assertTrue(isfile(join(directory_name, RESULTS_DIRECTORY, 'test_result.pdf')))
        self.assertTrue(getsize(join(directory_name, RESULTS_DIRECTORY, 'test_result.pdf')) > 0)
        unlink(join(pdf_dir, 'test_result.pdf'))
        rmdir(pdf_dir)

    def test_make_pdf2(self):
        """
        No source images
        """
        pdf = PDF()
        directory_name = dirname(__file__)
        pdf_dir = join(directory_name, RESULTS_DIRECTORY)
        try:
            pdf.make_pdf('test', join(pdf_dir, 'test_result.pdf'))
        except FileNotFoundError as e:
            raise e

        self.assertTrue(isfile(join(directory_name, RESULTS_DIRECTORY, 'test_result.pdf')))
        self.assertTrue(getsize(join(directory_name, RESULTS_DIRECTORY, 'test_result.pdf')) > 0)
        unlink(join(pdf_dir, 'test_result.pdf'))
        rmdir(pdf_dir)

    def test_make_pdf3(self):
        """
        Empty title
        """
        pdf = PDF()
        directory_name = dirname(__file__)
        pdf_dir = join(directory_name, RESULTS_DIRECTORY)
        try:
            pdf.make_pdf(None, join(pdf_dir, 'test_result.pdf'))
        except FileNotFoundError as e:
            raise e

        self.assertTrue(isfile(join(directory_name, RESULTS_DIRECTORY, 'test_result.pdf')))
        self.assertTrue(getsize(join(directory_name, RESULTS_DIRECTORY, 'test_result.pdf')) > 0)
        unlink(join(pdf_dir, 'test_result.pdf'))
        rmdir(pdf_dir)

    def test_make_pdf4(self):
        """
        Missing pdf file name
        """
        pdf = PDF()
        try:
            pdf.make_pdf('test', '')
        except FileNotFoundError as e:
            self.assertTrue(isinstance(e, FileNotFoundError))

    def test_make_pdf5(self):
        """
        Test clearing pages function
        """
        directory_name = dirname(__file__)
        pdf = PDF()

        pdf.add_dir(join(directory_name, 'images'))

        pdf_dir = join(directory_name, RESULTS_DIRECTORY)
        pdf.clear_pages()
        pages = pdf.make_pdf('test', join(pdf_dir, 'test_result.pdf'))

        self.assertTrue(pages == 0)
        self.assertTrue(len(pdf.files_list) == 0)
        self.assertTrue(isfile(join(directory_name, RESULTS_DIRECTORY, 'test_result.pdf')))
        self.assertTrue(getsize(join(directory_name, RESULTS_DIRECTORY, 'test_result.pdf')) > 0)
        unlink(join(pdf_dir, 'test_result.pdf'))
        rmdir(pdf_dir)


if __name__ == '__main__':
    unittest.main()
