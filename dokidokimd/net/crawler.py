from abc import ABC, abstractmethod


class Crawler(ABC):
    def __init__(self):

        pass

    @abstractmethod
    def crawl_index(self, url):
        """

        :param url:
        :return: MangaSite object with basic info(title,cover) for each entry
        """

        pass

    @abstractmethod
    def crawl_detail(self, url):
        """

        :param url:
        :return: Manga object with detailed info for entry
        """

        pass

    @abstractmethod
    def download(self, url):
        """

        :param url:
        :return: chapter images for given url
        """

        pass


if __name__ == "__main__":

    pass
