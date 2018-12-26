import pickle
import re
from typing import List

from PIL import Image

from dokidokimd.dd_logger.dd_logger import get_logger
from dokidokimd.translation.translator import translate

_ = translate

module_logger = get_logger('manga_site')

PathSafeRegEx = r"[^a-zA-Z0-9_\- \+,%\(\)\[\]'~@]+"
PathSafeReplaceChar = r'_'

AvailableSites = {
    'GoodManga': 'http://www.goodmanga.net/',
    'MangaPanda': 'https://www.mangapanda.com/',
    'KissManga': 'http://kissmanga.com/',
}


def load_dumped_site(dump_object):
    return pickle.loads(dump_object)


class Chapter:
    def __init__(self, title: str = None) -> None:
        self.manga_ref = None       # type: Manga
        self.title = title          # type: str
        self.url = None             # type: str
        self.pages = []             # type: List[Image]

        self.downloaded = False     # type: bool
        self.converted = False      # type: bool

    def get_path_safe_title(self) -> str:
        pattern = re.compile(PathSafeRegEx, re.UNICODE)
        return pattern.sub(PathSafeReplaceChar, self.title)

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        try:
            # del state['pages']
            state['pages'] = []
        except Exception as e:
            pass
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if not hasattr(self, 'downloaded'):
            self.downloaded = False
        if not hasattr(self, 'converted'):
            self.converted = False
        if not hasattr(self, 'pages'):
            self.pages = []

    def flush_pages(self) -> None:
        self.pages = None


class Manga:

    def __init__(self, title=None) -> None:
        self.site_ref = None        # type: MangaSite
        self.title = title          # type: str
        self.url = None             # type: str
        self.author = None          # type: str
        self.cover = None           # serialized to B64 type: str
        self.status = None          # type: str
        self.genres = None          # type: str
        self.summary = None         # type: str
        self.chapters = []          # type: List[Chapter]

        self.downloaded = False  # type: bool

    def get_path_safe_title(self) -> str:
        pattern = re.compile(PathSafeRegEx, re.UNICODE)
        return pattern.sub(PathSafeReplaceChar, self.title)

    def add_chapter(self, chapter) -> None:
        chapter.manga_ref = self
        if self.chapters is None:
            self.chapters = list()
            self.chapters.append(chapter)
        elif chapter.url not in [x.url for x in self.chapters if x.url == chapter.url]:
            self.chapters.append(chapter)
        module_logger.debug(_('Added [{}] chapter {} to manga {}.').format(len(self.chapters), chapter.title, self.title))

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if not hasattr(self, 'downloaded'):
            self.downloaded = False


class MangaSite:

    def __init__(self, site_name=None) -> None:
        self.site_name = site_name      # type: str
        self.url = None                 # type: str
        self.mangas = []                # type: List[Manga]

    def add_manga(self, manga) -> None:
        manga.site_ref = self
        if self.mangas is None:
            self.mangas = list()
            self.mangas.append(manga)
        elif manga.url not in [x.url for x in self.mangas if x.url == manga.url]:
            self.mangas.append(manga)
        module_logger.debug(_('Added [{}] manga {} to site {}.').format(len(self.mangas), manga.title, self.site_name))

    def dump(self):
        module_logger.debug(_('Dumped {} site with {} mangas.').format(self.site_name, len(self.mangas)))
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == '__main__':
    pass
