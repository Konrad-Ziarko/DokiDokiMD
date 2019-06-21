import pickle
import re
from typing import List

from tools.kz_logger import get_logger
from tools.misc import get_object_mem_size
from tools.translator import translate as _

logger = get_logger(__name__)

path_safe_regex = r"[^a-zA-Z0-9_\- \+,%\(\)\[\]'~@]+"
path_safe_replace_char = r'_'
compiled_regex = re.compile(path_safe_regex, re.UNICODE)

available_sites = {
    'Mangareader': 'https://www.mangareader.net',
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
        self.pages = []             # type: List[bytes]

        self.downloaded = False     # type: bool
        self.converted = False      # type: bool

    def get_path_safe_title(self) -> str:
        return compiled_regex.sub(path_safe_replace_char, self.title)

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
        self.cover = None           # type: str
        self.status = None          # type: str
        self.genres = None          # type: str
        self.summary = None         # type: str
        self.chapters = []          # type: List[Chapter]

        self.downloaded = False  # type: bool

    def get_path_safe_title(self) -> str:
        return compiled_regex.sub(path_safe_replace_char, self.title)

    def add_chapter(self, chapter) -> None:
        chapter.manga_ref = self
        if self.chapters is None:
            self.chapters = list()
            self.chapters.append(chapter)
        elif chapter.url not in [x.url for x in self.chapters if x.url == chapter.url]:
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

    def dump(self):
        logger.debug(_('Dumped {} site with {} mangas - size in memory = {} bytes.').format(
            self.site_name, len(self.mangas), get_object_mem_size(self)))
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == '__main__':
    pass
