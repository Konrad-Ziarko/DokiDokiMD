import pickle


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

        #  python scripts
        self.index_crawler = None
        self.detail_crawler = None
        self.downloader = None

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

