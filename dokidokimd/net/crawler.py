from abc import abstractmethod

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import scrapy

from dokidokimd.core.manga_site import Manga, MangaSite


class BaseCrawler(scrapy.Spider):
    name = "manga"
    _rules = (
        Rule(LinkExtractor(allow=()),
             callback="parse",
             follow=True),)

    @abstractmethod
    def parse(self, response):
        pass

    def __init__(self, manga_site):
        super().__init__()
        self.manga_site = manga_site


class GoodMangaCrawler(BaseCrawler):
    def __init__(self, manga_site):
        super().__init__(manga_site=manga_site)

    def parse(self, response):
        # print('Processing..' + response.url)
        xpath = '//*[@id="content"]/table/tr/td/a'
        table = response.xpath(xpath)
        for entry in table:
            manga = Manga()
            manga.title = entry.xpath('text()').extract()
            manga.url = entry.xpath('@href').extract()

            self.manga_site.add_manga(manga)


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    manga_site = MangaSite()
    manga_site.site_name = "goodmanga"
    manga_site.url = "www.goodmanga.net"

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    })

    GoodMangaCrawler.start_urls = ['http://www.goodmanga.net/manga-list']
    GoodMangaCrawler.allowed_domains = ["www.goodmanga.net"]
    process.crawl(GoodMangaCrawler, manga_site)
    process.start()
    #d = runner.join()
    #d.addBoth(lambda _: reactor.stop())
    #reactor.run()

    print(manga_site.convert_to_json())
