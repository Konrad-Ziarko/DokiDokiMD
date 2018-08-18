from abc import abstractmethod


class BaseCrawler:
    @abstractmethod
    def crawl_index(self, manga_site):
        pass

    @abstractmethod
    def crawl_detail(self, manga):
        pass

    @abstractmethod
    def download(self, chapter):
        pass
