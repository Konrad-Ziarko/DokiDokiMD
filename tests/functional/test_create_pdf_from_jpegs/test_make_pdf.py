import os

from dokidokimd.convert.make_pdf import PDF


def test_make_pdf():
    dirname = os.path.dirname(__file__)
    pdf = PDF('test')

    pdf.add_dir(os.path.join(dirname, 'images'))

    pdf.make_pdf()

    pdf.save_pdf(os.path.join(dirname, 'results', 'test_result.pdf'))

    assert os.path.isfile(os.path.join(dirname, 'results', 'test_result.pdf')) is True
    assert os.path.getsize(os.path.join(dirname, 'results', 'test_result.pdf')) > 0

