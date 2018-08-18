from dokidokimd.core.manga_site import MangaSite
from dokidokimd.net.crawler.goodmanga import GoodMangaCrawler

# TODO remove this
from dokidokimd.net.crawler.mangapanda import MangaPandaCrawler

if __name__ == "__main__":

    manga_site = MangaSite()
    crawler = MangaPandaCrawler()
    crawler.crawl_index(manga_site)

    manga = manga_site.mangas[4]
    crawler.crawl_detail(manga)

    chapter = manga.chapters[0]
    pages = crawler.download(chapter)

