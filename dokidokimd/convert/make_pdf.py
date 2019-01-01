import imghdr
from io import BytesIO
from os import listdir
from os.path import isfile, join
from typing import List

from PIL import Image

from dokidokimd import PROJECT_NAME
from dokidokimd.convert.FPDFV2 import FPDFV2
from dokidokimd.core.manga_site import Chapter
from dokidokimd.dd_logger.dd_logger import get_logger
from dokidokimd.translation.translator import translate

_ = translate

module_logger = get_logger('make_pdf')


class PDF:
    def __init__(self) -> None:
        self.pages_binary = list()  # type: List[bytes]
        self.files_list = list()  # type: List[str]
        self.builder = None  # type: FPDFV2

    def clear_pages(self) -> None:
        self.pages_binary = list()

    def add_chapter(self, chapter: Chapter):
        self.pages_binary += chapter.pages

    def add_page_from_file(self, image_path: str, index: int = None) -> None:
        if index is None:
            self.files_list.append(image_path)
        elif index is not None:
            self.files_list.insert(index, image_path)

    def add_dir(self, dir_path: str, extension_filter: str = None) -> None:
        module_logger.debug(_('Added {} directory in pdf module. With extension filter equal to {}').format(dir_path, extension_filter))
        if extension_filter is None:
            files = [join(dir_path, f) for f in listdir(dir_path) if isfile(join(dir_path, f))]
        else:
            files = [join(dir_path, f) for f in listdir(dir_path) if
                     isfile(join(dir_path, f) and f.endswith('.{}'.format(extension_filter)))]
        files = sorted(files)
        self.files_list += files

    def make_pdf(self, title: str) -> None:
        module_logger.debug(_('Started make_pdf #if orientation=L x and y are swapped.'))
        use_binary = False
        if len(self.pages_binary) > 0:
            use_binary = True
            width, height = Image.open(BytesIO(self.pages_binary[0])).size
        else:
            width, height = Image.open(self.files_list[0]).size

        self.builder = FPDFV2(unit='pt', format=[width, height])
        self.builder.compress = False
        self.builder.set_title(title)
        self.builder.set_author(PROJECT_NAME)

        if use_binary:
            num_pages = len(self.pages_binary)
        else:
            num_pages = len(self.files_list)

        for i in range(num_pages):
            if use_binary:
                width2, height2 = Image.open(BytesIO(self.pages_binary[0])).size
            else:
                width2, height2 = Image.open(self.pages_binary[i]).size
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

            if use_binary:
                img = BytesIO(self.pages_binary[i])
                img_type = imghdr.what(img)
                if orientation is 'L':
                    self.builder.image('', y, x, width2, height2, type=img_type, link=None, file=img)
                else:
                    self.builder.image('', x, y, width2, height2, type=img_type, link=None, file=img)
            else:
                if orientation is 'L':
                    self.builder.image(self.pages_binary[i], y, x, width2, height2)
                else:
                    self.builder.image(self.pages_binary[i], x, y, width2, height2)

            module_logger.debug(_('Page no. {} oriented {}, added to pdf, width={}, height={}, x={}, y={} ').format(i, orientation, width2, height2, x, y))

    def save_pdf(self, path: str) -> None:
        self.builder.output(path, 'F')
        module_logger.info(_('PDF saved to a {} file.').format(path))


if __name__ == '__main__':
    pass
