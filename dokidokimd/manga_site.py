import pickle
import re
from os.path import join
from typing import List

from tools.kz_logger import get_logger
from tools.misc import get_object_mem_size
from tools.translator import translate as _

logger = get_logger(__name__)

path_safe_regex = r"[^a-zA-Z0-9_\- \+,%\(\)\[\]'~@]+"
path_safe_replace_char = r'_'
compiled_regex = re.compile(path_safe_regex, re.UNICODE)


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
        self.in_memory = False      # type: bool

    def set_downloaded(self, state=True):
        self.downloaded = state
        self.in_memory = state

    def clear_state(self):
        self.pages = []
        self.downloaded = False
        self.in_memory = False
        self.converted = False

    def get_download_path(self, base_path: str) -> str:
        return join(base_path, 'downloaded', self.manga_ref.site_ref.site_name,
                    self.manga_ref.get_path_safe_title(), self.get_path_safe_title())

    def get_convert_path(self, base_path: str) -> str:
        return join(base_path, 'converted', self.manga_ref.site_ref.site_name, self.manga_ref.get_path_safe_title())

    def get_path_safe_title(self) -> str:
        return compiled_regex.sub(path_safe_replace_char, self.title)

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        try:
            state['pages'] = []
            state['in_memory'] = False
        except KeyError as e:
            logger.debug(_('Could not drop filed while dumping object, reason {}').format(e))
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if not hasattr(self, 'downloaded'):
            self.downloaded = False
        if not hasattr(self, 'converted'):
            self.converted = False
        if not hasattr(self, 'in_memory'):
            self.in_memory = False
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

        self.downloaded = False     # type: bool

    def clear_state(self):
        self.chapters = []
        self.downloaded = False

    def get_download_path(self, base_path: str) -> str:
        return join(base_path, 'downloaded', self.site_ref.site_name, self.get_path_safe_title())

    def get_convert_path(self, base_path: str) -> str:
        return join(base_path, 'converted', self.site_ref.site_name, self.get_path_safe_title())

    def get_path_safe_title(self) -> str:
        return compiled_regex.sub(path_safe_replace_char, self.title)

    def add_chapter(self, chapter, reverse=False) -> None:
        chapter.manga_ref = self
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


class MangaSite:

    def __init__(self, site_name=None) -> None:
        self.site_name = site_name      # type: str
        self.url = None                 # type: str
        self.mangas = []                # type: List[Manga]

    def clear_state(self):
        self.mangas = []

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
