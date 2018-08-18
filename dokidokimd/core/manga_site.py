import inspect
import json
import ast
import pickle

class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj


def json_string_to_dict(json_string):
    strr = json_string
    x = json.loads(strr, cls=ObjectEncoder, indent=2)
    return ast.literal_eval(strr)


class Chapter:
    def __init__(self, json_object=None):
        self.title = ""
        self.url = ""
        self.pages = None

        # if json is passed this means to create instance from json data
        if json_object is not None:
            json_dict = json_string_to_dict(json_object)
            self.title = json_dict['title']
            self.url = json_dict['url']

    def convert_to_json(self):
        object_dict = self.__dict__
        self.__dict__.pop('pages', None)  # remove downloaded pages
        return json.dumps(object_dict, cls=ObjectEncoder, indent=2)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['pages']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class Manga:

    def __init__(self, json_object=None):
        self.title = ""
        self.url = ""
        self.author = ""
        self.cover = ""  # serialize to B64?
        self.status = ""
        self.genres = ""
        self.summary = ""
        self.chapters = list()

        # if json is passed this means to create instance from json data
        if json_object is not None:
            # load each chapter in for loop
            json_dict = json_string_to_dict(json_object)
            self.title = json_dict['title']
            self.url = json_dict['url']
            self.author = json_dict['author']
            self.cover = json_dict['cover']
            self.status = json_dict['status']
            self.genres = json_dict['genres']
            self.summary = json_dict['summary']
            self.chapters = json_dict['chapters']

    def add_chapter(self, chapter):
        if self.chapters is None:
            self.chapters = list()
            self.chapters.append(chapter)
        else:
            self.chapters.append(chapter)

    def convert_to_json(self):
        return json.dumps(self.__dict__, cls=ObjectEncoder, indent=2)


class MangaSite:

    def __init__(self, json_object=None):
        self.site_name = ""
        self.url = ""
        self.mangas = None

        #  python scripts
        self.index_crawler = None
        self.detail_crawler = None
        self.downloader = None

        # if json is passed this means to create instance from json data
        if json_object is not None:
            # json.load()
            # load each manga in for loop
            pass

    def add_manga(self, manga):
        if self.mangas is None:
            self.mangas = list()
            self.mangas.append(manga)
        else:
            self.mangas.append(manga)

    def convert_to_json(self):
        return json.dumps(self.__dict__, cls=ObjectEncoder, indent=2)


if __name__ == "__main__":
    chapter = Chapter()
    chapter.title = "example"
    chapter.url = ""

    asd = chapter.convert_to_json()

    manga = Manga()
    manga.title = "Naruto"
    manga.url = "www.example2.com"
    manga.add_chapter(chapter)

    dum = pickle.dumps(manga)

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
    print(y1.convert_to_json())

    manga2 = Manga(y1.convert_to_json())

    a = MangaSite()
    a.site_name = "mangapanda"
    a.add_manga(manga)
    a.add_manga(y1)
    print(a.convert_to_json())

    b = MangaSite(a.convert_to_json())
