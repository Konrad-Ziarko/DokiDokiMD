import imghdr
import os
import pickle
import shutil
from io import BytesIO
from typing import List, Tuple

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from dokidokimd.tools.ddmd_logger import get_logger
from dokidokimd.tools.misc import get_object_mem_size, make_path_os_safe
from dokidokimd.tools.translator import translate as _

logger = get_logger(__name__)


class Chapter:
    def __init__(self, manga, title: str = None) -> None:
        self.manga = manga      # type: Manga
        self.title = title          # type: str
        self.url = None             # type: str
        self.pages = []             # type: List[bytes]

        self.downloaded = False     # type: bool
        self.saved_images = False   # type: bool
        self.converted = False      # type: bool
        self.in_memory = False      # type: bool

    def number_of_pages(self):
        return len(self.pages)

    def add_page(self, page_as_bytes: bytes):
        self.pages.append(page_as_bytes)

    def set_downloaded(self, state=True):
        self.downloaded = state
        self.in_memory = state

    def clear_state(self):
        self.pages = []
        self.downloaded = False
        self.saved_images = False
        self.in_memory = False
        self.converted = False

    def get_download_path(self, base_path: str) -> str:
        return os.path.join(self.manga.get_download_path(base_path), self.get_title())

    def get_pdf_path(self, base_path: str) -> str:
        return self.manga.get_pdf_path(base_path)

    def get_title(self) -> str:
        return make_path_os_safe(self.title)

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        try:
            state['pages'] = []
            state['in_memory'] = False
        except KeyError as e:
            logger.error(_(F'Could not drop filed while dumping object, reason {e}'))
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def save_images(self, base_path: str) -> Tuple[bool, str]:
        images_dir = self.get_download_path(base_path)
        try:
            if not os.path.isdir(images_dir):
                os.makedirs(images_dir, exist_ok=True)
            for idx, page in enumerate(self.pages):
                img_type = imghdr.what(BytesIO(page))
                path = os.path.join(images_dir, F'{idx:0>3d}.{img_type}')
                with open(path, 'wb') as f:
                    f.write(page)
        except Exception as e:
            logger.error(_(F'Could not save images to {images_dir}\nError message: {e}'))
            return False, images_dir
        self.saved_images = True
        return True, images_dir

    def make_pdf(self, base_path: str) -> Tuple[bool, str]:
        pdf_dir = self.get_pdf_path(base_path)
        if not os.path.isdir(pdf_dir):
            os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, F'{self.get_title()}.pdf')
        builder = Canvas(pdf_path, pageCompression=False, pagesize=A4)
        builder.setTitle(self.title)
        if len(self.pages) > 0:
            for i in range(len(self.pages)):
                image = Image.open(BytesIO(self.pages[i]))
                builder.setPageSize(image.size)
                builder.drawImage(ImageReader(image), 0, 0)
                builder.showPage()
        else:
            images_dir = self.get_download_path(base_path)
            if not os.path.isdir(images_dir):
                logger.warning(_('Could not convert to PDF, source path with images does not exist or images not downloaded'))
                return False, pdf_path
            try:
                files = [os.path.join(images_dir, f) for f in os.listdir(images_dir)
                         if os.path.isfile(os.path.join(images_dir, f))]
                files = sorted(files)
                for i in range(len(files)):
                    builder.setPageSize(Image.open(files[i]).size)
                    builder.drawImage(files[i], 0, 0)
                    builder.showPage()
            except Exception as e:
                logger.error(_(F'Could not save PDF to {pdf_path}\nError message: {e}'))
                return False, pdf_path

        if not os.path.exists(os.path.dirname(pdf_path)):
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        builder.save()
        self.converted = True
        logger.info(_(F'PDF saved to a {pdf_path} file.'))
        return True, pdf_path

    def chapter_images_present(self, base_path) -> bool:
        images_dir = self.get_download_path(base_path)
        if not os.path.isdir(images_dir):
            return False
        if not os.listdir(images_dir):
            return False
        return True

    def remove_from_disk(self, base_path):
        shutil.rmtree(self.get_download_path(base_path), ignore_errors=True)
        shutil.rmtree(self.get_pdf_path(base_path), ignore_errors=True)


class Manga:
    def __init__(self, title, url, manga_site) -> None:
        self.manga_site = manga_site  # type: MangaSite
        self.title = title          # type: str
        self.url = url              # type: str
        self.author = ''            # type: str
        self.cover = ''             # type: str
        self.status = ''            # type: str
        self.genres = ''            # type: str
        self.summary = ''           # type: str
        self.chapters = []          # type: List[Chapter]

        self.downloaded = False     # type: bool

    def clear_state(self):
        self.chapters = []
        self.downloaded = False

    def get_download_path(self, base_path: str) -> str:
        return os.path.join(base_path, 'downloaded', self.manga_site.site_name, self.get_title())

    def get_pdf_path(self, base_path: str) -> str:
        return os.path.join(base_path, 'converted', self.manga_site.site_name, self.get_title())

    def get_title(self) -> str:
        return make_path_os_safe(self.title)

    def add_chapter(self, chapter, reverse=False) -> None:
        if self.chapters is None:
            self.chapters = list()
            if reverse:
                self.chapters.insert(0, chapter)
            else:
                self.chapters.append(chapter)
        elif chapter.url not in [x.url for x in self.chapters if x.url == chapter.url]:
            if reverse:
                self.chapters.insert(0, chapter)
            else:
                self.chapters.append(chapter)

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if not hasattr(self, 'downloaded'):
            self.downloaded = False

    def remove_from_disk(self, base_path):
        shutil.rmtree(self.get_download_path(base_path), ignore_errors=True)
        shutil.rmtree(self.get_pdf_path(base_path), ignore_errors=True)


class MangaSite:
    def __init__(self, site_name=None) -> None:
        self.site_name = site_name      # type: str
        self.url = None                 # type: str
        self.mangas = []                # type: List[Manga]

    def clear_state(self):
        self.mangas = []

    def add_manga(self, manga) -> None:
        if self.mangas is None:
            self.mangas = list()
            self.mangas.append(manga)
        elif manga.url not in [x.url for x in self.mangas if x.url == manga.url]:
            self.mangas.append(manga)

    def dump(self):
        logger.debug(_(F'Dumped {self.site_name} site with {len(self.mangas)} mangas - size in memory = {get_object_mem_size(self)} bytes.'))
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    @staticmethod
    def load_dumped_site(dump_object):
        return pickle.loads(dump_object)


if __name__ == '__main__':
    pass
