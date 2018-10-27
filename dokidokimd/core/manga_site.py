import pickle
from enum import Enum
from os.path import basename

from dokidokimd.logging.logger import get_logger

module_logger = get_logger((basename(__file__))[0])


class AvailableSites(Enum):
    GoodManga = 'http://www.goodmanga.net/'
    MangaPanda = 'https://www.mangapanda.com/'
    KissManga = 'http://kissmanga.com/'


def load_dumped_site(dump_object):
    return pickle.loads(dump_object)


class Chapter:
    def __init__(self):
        self.title = None
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

    def __init__(self):
        self.title = None
        self.url = None
        self.author = None
        self.cover = None  # serialize to B64?
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
        module_logger.debug('Added [{}] chapter {} to manga {}.'.format(len(self.chapters), chapter.title, self.title))

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class MangaSite:

    def __init__(self):
        self.site_name = None
        self.url = None
        self.mangas = None

    def add_manga(self, manga):
        if self.mangas is None:
            self.mangas = list()
            self.mangas.append(manga)
        else:
            self.mangas.append(manga)
        module_logger.debug('Added [{}] manga {} to site {}.'.format(len(self.mangas), manga.title, self.site_name))

    def dump(self):
        module_logger.debug('Dumped {} site with {} mangas.'.format(self.site_name, len(self.mangas)))
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == '__main__':
    chap = Chapter()
    chap.title = 'example'
    chap.url = ''
    dum = chap.dump()

    chapter2 = load_dumped_site(dum)

    man = Manga()
    man.title = 'Naruto'
    man.url = 'www.example2.com'
    man.add_chapter(chap)

    dum = pickle.dumps(man)

    x1 = Chapter()
    x1.title = 'ass'
    x1.url = 'www.ass'

    z1 = Chapter()
    z1.title = 'ass2'
    z1.url = 'www.ass2.com'

    y1 = Manga()
    y1.title = 'Bleach'
    y1.url = 'www.ass2.com'
    y1.add_chapter(x1)
    y1.add_chapter(z1)

    a = MangaSite()
    a.site_name = 'mangapanda'
    a.add_manga(man)
    a.add_manga(y1)

    dum2 = a.dump()
    b = load_dumped_site(dum2)

    from dokidokimd.core.controller import DDMDController

    # gmcrawler = GoodMangaCrawler()
    xx = MangaSite()
    # gmcrawler.crawl_index(xx)

    controller = DDMDController()
    # controller.manga_sites.append(xx)

    # controller.store_sites()
    controller.load_sites()
    site = controller.manga_sites
    pass
