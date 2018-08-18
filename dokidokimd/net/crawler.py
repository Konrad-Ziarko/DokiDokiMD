from dokidokimd.core.manga_site import MangaSite
from dokidokimd.net.crawler.goodmanga import GoodMangaCrawler

if __name__ == "__main__":

    manga_site = MangaSite()
    manga_site.site_name = "goodmanga"
    manga_site.url = "www.goodmanga.net"
    crawler = GoodMangaCrawler()
    crawler.crawl_index(manga_site)

    manga = manga_site.mangas[0]
    crawler.crawl_detail(manga)

    print(manga.title)

