import inspect
import json


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
        return obj  # instead of return obj in the last line I did this return super(ObjectEncoder, self).default(obj)


class Chapter:

    def __init__(self, json_object=None):
        self.title = None
        self.url = None
        pass

        # if json is passed this means to create instance from json data
        if json_object is not None:
            pass

    def convert_to_json(self):
        return json.dumps(self.__dict__, cls=ObjectEncoder, indent=2)
        pass


class Manga:

    def __init__(self, json_object=None):
        self.title = None
        self.url = None
        self.author = None
        self.cover = None  # serialize to B64?
        self.status = None
        self.genres = None
        self.summary = None
        self.chapters = None
        pass

        # if json is passed this means to create instance from json data
        if json_object is not None:
            # load each chapter in for loop
            pass

    def add_chapter(self, chapter):
        if self.chapters is None:
            self.chapters = list()
            self.chapters.append(chapter)
        else:
            self.chapters.append(chapter)

    def convert_to_json(self):
        return json.dumps(self.__dict__, cls=ObjectEncoder, indent=2)
        pass


class MangaSite:

    def __init__(self, json_object=None):
        self.site_name = None
        self.url = None
        self.mangas = None

        #  python scripts
        self.index_crawler = None
        self.index_detail_crawler = None
        self.downloader = None

        # if json is passed this means to create instance from json data
        if json_object is not None:
            # json.load()
            # load each manga in for loop
            pass

        pass

    def add_manga(self, manga):
        if self.mangas is None:
            self.mangas = list()
            self.mangas.append(manga)
        else:
            self.mangas.append(manga)

    def convert_to_json(self):
        return json.dumps(self.__dict__, cls=ObjectEncoder, indent=2)
        pass


if __name__ == "__main__":
    x = Chapter()
    x.title = "dupa"
    x.url = "www.dupa"

    z = Chapter()
    z.title = "dupa2"
    z.url = "www.dupa2"

    y = Manga()
    y.title = "Naruto"
    y.url = "www.dupa"
    y.add_chapter(x)
    y.add_chapter(z)

    x1 = Chapter()
    x1.title = "ass"
    x1.url = "www.ass"

    z1 = Chapter()
    z1.title = "ass2"
    z1.url = "www.ass2"

    y1 = Manga()
    y1.title = "Bleach"
    y1.url = "www.ass2"
    y1.add_chapter(x1)
    y1.add_chapter(z1)

    a = MangaSite()
    a.site_name = "mangapanda"
    a.add_manga(y)
    a.add_manga(y1)
    print(a.convert_to_json())
    pass
