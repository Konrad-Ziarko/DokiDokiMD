from os.path import dirname, join, isfile, getsize

from dokidokimd.convert.make_pdf import PDF


def test_make_pdf():
    directory_name = dirname(__file__)
    pdf = PDF()

    pdf.add_dir(join(directory_name, 'images'))

    pdf.make_pdf('test')

    pdf.save_pdf(join(directory_name, 'results', 'test_result.pdf'))

    assert isfile(join(directory_name, 'results', 'test_result.pdf')) is True
    assert getsize(join(directory_name, 'results', 'test_result.pdf')) > 0

