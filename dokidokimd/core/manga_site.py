import pickle

from dokidokimd.logging.logger import get_logger
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
        self.pages = None

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['pages']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class Manga:

    def __init__(self, title=None):
        self.title = title
        self.url = None
        self.author = None
        self.cover = None  # serialize to B64
        self.status = None
        self.genres = None
        self.summary = None
        self.chapters = None

    def add_chapter(self, chapter):
        if self.chapters is None:
            self.chapters = list()
            self.chapters.append(chapter)
        else:
            self.chapters.append(chapter)
        module_logger.debug(_('Added [{}] chapter {} to manga {}.').format(len(self.chapters), chapter.title, self.title))

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class MangaSite:

    def __init__(self, site_name=None):
        self.site_name = site_name
        self.url = None
        self.mangas = None

    def add_manga(self, manga):
        if self.mangas is None:
            self.mangas = list()
            self.mangas.append(manga)
        else:
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
