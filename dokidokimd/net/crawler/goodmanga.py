from dokidokimd.core.manga_site import Manga, Chapter
from dokidokimd.net.crawler.base_crawler import BaseCrawler

import requests
from lxml import html


class GoodMangaCrawler(BaseCrawler):
    name = "GoodManga"
    allowed_domains = ["www.goodmanga.net"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def crawl_index(self, manga_site):
        start_url = 'http://www.goodmanga.net/manga-list'

        response = requests.get(start_url)
        tree = html.fromstring(response.content)

        for element in tree.xpath('//*[@id="content"]/table/tr/td/a'):
            manga = Manga()
            manga.title = element.xpath('text()')[0]
            manga.url = element.xpath('@href')[0]

            manga_site.add_manga(manga)
        print(manga_site.site_name)

    def crawl_detail(self, manga):
        start_url = manga.url

        response = requests.get(start_url)
        tree = html.fromstring(response.content)

        # crawl for manga chapters
        for element in tree.xpath('//*[@id="chapters"]/ul/li/a'):
            chapter = Chapter()
            chapter.title = element.xpath('text()')[0].lstrip()  # lstrip() removes leading newline
            chapter.url = element.xpath('@href')[0]

            manga.add_chapter(chapter)

        # crawl for manga details
        # https://api.jikan.moe/

    def download(self, chapter):
        pass

