from io import BytesIO
from os import listdir
from os.path import isfile, join
from typing import List

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from models import Chapter
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


class PDF:
    def __init__(self) -> None:
        self.pages_binary = list()  # type: List[bytes]
        self.files_list = list()    # type: List[str]
        self.builder = None         # type: Canvas

    def clear_pages(self) -> None:
        self.pages_binary = list()

    def add_chapter(self, chapter: Chapter):
        self.pages_binary.extend(chapter.pages)

    def add_page_from_file(self, image_path: str, index: int = None) -> None:
        if index is None:
            self.files_list.append(image_path)
        elif index is not None:
            self.files_list.insert(index, image_path)

    def add_dir(self, dir_path: str, extension_filter: str = None) -> None:
        logger.debug(
            _(F'Added {dir_path} directory in pdf module. With extension filter equal to {extension_filter}'))
        if extension_filter is None:
            files = [join(dir_path, f) for f in listdir(dir_path) if isfile(join(dir_path, f))]
        else:
            files = [join(dir_path, f) for f in listdir(dir_path) if
                     isfile(join(dir_path, f) and f.endswith(F'.{extension_filter}'))]
        files = sorted(files)
        self.files_list += files

    def make_pdf(self, title: str, path: str) -> int:
        use_binary = False
        if len(self.pages_binary) > 0:
            use_binary = True

        self.builder = Canvas(path, pageCompression=False, pagesize=A4)
        self.builder.setTitle(title)
        if use_binary:
            num_pages = len(self.pages_binary)
        else:
            num_pages = len(self.files_list)

        for i in range(num_pages):
            if use_binary:
                width, height = Image.open(BytesIO(self.pages_binary[i])).size
            else:
                width, height = Image.open(self.files_list[i]).size
            self.builder.setPageSize((width, height))

            if use_binary:
                self.builder.drawImage(ImageReader(Image.open(BytesIO(self.pages_binary[i]))), 0, 0)
                self.builder.showPage()
            else:
                self.builder.drawImage(self.files_list[i], 0, 0)
                self.builder.showPage()
        self.builder.save()
        logger.info(_(F'PDF saved to a {path} file.'))
        return num_pages


if __name__ == '__main__':
    pass
