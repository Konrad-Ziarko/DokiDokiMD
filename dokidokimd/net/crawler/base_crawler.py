from abc import abstractmethod

from dokidokimd.core.manga_site import MangaSite, Manga, Chapter


class BaseCrawler:
    @abstractmethod
    def crawl_index(self, manga_site: MangaSite) -> None:
        pass

    @abstractmethod
    def crawl_detail(self, manga: Manga) -> None:
        pass

    @abstractmethod
    def download(self, chapter: Chapter) -> None:
        pass
