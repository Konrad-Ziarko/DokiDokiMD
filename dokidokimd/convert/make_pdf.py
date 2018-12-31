from os import listdir
from os.path import isfile, join
from typing import List

from PIL import Image
from fpdf import FPDF

from dokidokimd import PROJECT_NAME
from dokidokimd.dd_logger.dd_logger import get_logger
from dokidokimd.translation.translator import translate

_ = translate

module_logger = get_logger('make_pdf')


class PDF:
    def __init__(self) -> None:
        self.pages = list()     # type: List[str]
        self.builder = None     # type: FPDF

    def clear_pages(self) -> None:
        self.pages = list()

    def add_page_from_file(self, image_path: str, index: int = None) -> None:
        if index is None:
            self.pages.append(image_path)
        elif index is not None:
            self.pages.insert(index, image_path)

    def remove_page(self, index: int = None) -> None:
        if len(self.pages) >= 1:
            if index is None:
                self.pages.pop(len(self.pages) - 1)
            elif index is not None:
                self.pages.pop(index)

    def make_pdf(self, title: str) -> None:
        module_logger.debug(_('Started make_pdf #if orientation=L x and y are swapped.'))
        cover = Image.open(self.pages[0])
        width, height = cover.size
        module_logger.debug(_('Cover size {}x{}.'.format(width, height)))
        self.builder = FPDF(unit='pt', format=[width, height])

        self.builder.set_title(title)
        self.builder.set_author(PROJECT_NAME)

        for i in range(len(self.pages)):
            width2, height2 = Image.open(self.pages[i]).size
            if width2 > height2:
                orientation = 'L'
            else:
                orientation = 'P'
            self.builder.add_page(orientation)

            x = y = 0
            if width2 != width and height2 != height:
                w = width2 / width
                h = height2 / height
                if w < h:
                    height2 = height
                    x = (width - width2 / h) / 2
                    width2 = 0
                else:
                    width2 = width
                    y = (height - height2 / w) / 2
                    height2 = 0

            if orientation is 'L':
                self.builder.image(self.pages[i], y, x, width2, height2)
            else:
                self.builder.image(self.pages[i], x, y, width2, height2)

            module_logger.debug(_('Page no. {} oriented {}, added to pdf, width={}, height={}, x={}, y={} ').format(i, orientation, width2, height2, x, y))

    def add_dir(self, dir_path: str, extension_filter: str = None) -> None:
        module_logger.debug(_('Added {} directory in pdf module. With extension filter equal to {}').format(dir_path, extension_filter))
        if extension_filter is None:
            files = [join(dir_path, f) for f in listdir(dir_path) if isfile(join(dir_path, f))]
        else:
            files = [join(dir_path, f) for f in listdir(dir_path) if
                     isfile(join(dir_path, f) and f.endswith('.{}'.format(extension_filter)))]
        files = sorted(files)
        for f in files:
            self.add_page_from_file(f)

    def save_pdf(self, path: str) -> None:
        module_logger.debug(_('PDF saved to a {} file.').format(path))
        self.builder.output(path, 'F')


if __name__ == '__main__':
    pass
