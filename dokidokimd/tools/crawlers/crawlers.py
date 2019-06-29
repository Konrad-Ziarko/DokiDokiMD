from collections import OrderedDict

from tools.crawlers.mangapanda import MangaPandaCrawler
from tools.crawlers.mangareader import MangaReaderCrawler
from tools.crawlers.mangasee import MangaSeeCrawler

MangaCrawlersMap = OrderedDict({
    'MangaReader': MangaReaderCrawler,
    'MangaPanda': MangaPandaCrawler,
    'MangaSee': MangaSeeCrawler,
})


def available_sites():
    return MangaCrawlersMap.keys()
