from abc import abstractmethod, ABCMeta

from models import MangaSite, Manga, Chapter


class BaseCrawler:
    __metaclass__ = ABCMeta
    @abstractmethod
    def crawl_index(self, manga_site: MangaSite) -> None:
        raise NotImplementedError

    @abstractmethod
    def crawl_detail(self, manga: Manga) -> None:
        raise NotImplementedError

    @abstractmethod
    def download(self, chapter: Chapter) -> int:
        """
        :return: number of downloaded pages
        """
        raise NotImplementedError
