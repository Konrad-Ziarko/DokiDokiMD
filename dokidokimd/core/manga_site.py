import pickle

from dokidokimd.dd_logger.dd_logger import get_logger
from dokidokimd.translation.translator import translate

_ = translate

module_logger = get_logger('manga_site')

AvailableSites = {
    'GoodManga': 'http://www.goodmanga.net/',
    'MangaPanda': 'https://www.mangapanda.com/',
    'KissManga': 'http://kissmanga.com/',
}


def load_dumped_site(dump_object):
    return pickle.loads(dump_object)


class Chapter:
    def __init__(self, title=None):
        self.title = title
        self.url = None
        self.pages = []

        self.downloaded = False
        self.converted = False

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

    def flush_pages(self):
        self.pages = None


class Manga:

    def __init__(self, title=None):
        self.title = title
        self.url = None
        self.author = None
        self.cover = None  # serialize to B64
        self.status = None
        self.genres = None
        self.summary = None
        self.chapters = []

        self.downloaded = False

    def add_chapter(self, chapter):
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

    def __init__(self, site_name=None):
        self.site_name = site_name
        self.url = None
        self.mangas = []

    def add_manga(self, manga):
        ln = len(manga.title)
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
