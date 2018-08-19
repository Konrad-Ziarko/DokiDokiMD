import pickle
from enum import Enum


class AvailableSites(Enum):
    GoodManga = "http://www.goodmanga.net/"
    MangaPanda = "https://www.mangapanda.com/"
    KissManga = "http://kissmanga.com/"


def load_dumped_object(dump_object):
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

    def dump(self):
        return pickle.dumps(self)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == "__main__":
    chap = Chapter()
    chap.title = "example"
    chap.url = ""
    dum = chap.dump()

    chapter2 = load_dumped_object(dum)

    man = Manga()
    man.title = "Naruto"
    man.url = "www.example2.com"
    man.add_chapter(chap)

    dum = pickle.dumps(man)

    x1 = Chapter()
    x1.title = "ass"
    x1.url = "www.ass"

    z1 = Chapter()
    z1.title = "ass2"
    z1.url = "www.ass2.com"

    y1 = Manga()
    y1.title = "Bleach"
    y1.url = "www.ass2.com"
    y1.add_chapter(x1)
    y1.add_chapter(z1)

    a = MangaSite()
    a.site_name = "mangapanda"
    a.add_manga(man)
    a.add_manga(y1)

    dum2 = a.dump()
    b = load_dumped_object(dum2)
