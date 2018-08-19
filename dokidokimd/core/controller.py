from enum import Enum

from dokidokimd.convert.make_pdf import PDF
from dokidokimd.core.manga_site import Manga, Chapter, AvailableSites
from dokidokimd.net.crawler.goodmanga import GoodMangaCrawler
from dokidokimd.net.crawler.kissmanga import KissMangaCrawler
from dokidokimd.net.crawler.mangapanda import MangaPandaCrawler


class MangaCrawlers(Enum):
    GoodManga = GoodMangaCrawler
    MangaPanda = MangaPandaCrawler
    KissManga = KissMangaCrawler


def manga_site_2_crawler(site_name):
    for crawler in MangaCrawlers:
        if crawler.name in site_name:
            return crawler.value()


class DDMDController:

    def __init__(self):
        self.manga_sites = []
        self.pdf_converter = PDF()

        pass


if __name__ == "__main__":
    pass