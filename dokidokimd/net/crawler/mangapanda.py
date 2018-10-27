from urllib.parse import urljoin

import requests
from lxml import html

from dokidokimd.core.manga_site import Manga, Chapter, AvailableSites
from dokidokimd.logging.logger import get_logger
from dokidokimd.net.crawler.base_crawler import BaseCrawler

module_logger = get_logger('crawler.mangapanda')


class MangaPandaCrawler(BaseCrawler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = AvailableSites.MangaPanda.value

    def crawl_index(self, manga_site):
        start_url = urljoin(self.base_url, '/alphabetical')

        response = requests.get(start_url)

        if response.status_code == 200:
            manga_site.site_name = AvailableSites.MangaPanda.name
            manga_site.url = self.base_url

            tree = html.fromstring(response.content)

            for element in tree.xpath('//*[@id="wrapper_body"]/div/div/div/ul/li/a'):
                manga = Manga()
                manga.title = str(element.xpath('text()')[0])
                manga.url = urljoin(self.base_url, str(element.xpath('@href')[0]))

                manga_site.add_manga(manga)
        else:
            raise ConnectionError('Could not connect with {} site, status code: {}'.
                                  format(start_url, response.status_code))

    def crawl_detail(self, manga):
        start_url = manga.url

        response = requests.get(start_url)
        if response.status_code == 200:
            tree = html.fromstring(response.content)

            # crawl for manga chapters
            for element in tree.xpath('//*[@id="listing"]/tr/td[1]/a'):
                chapter = Chapter()
                chapter.title = str(element.xpath('text()')[0])
                chapter.url = urljoin(self.base_url, str(element.xpath('@href')[0]))

                manga.add_chapter(chapter)

            # TODO 1: crawl for manga details
            # https://api.jikan.moe/

        else:
            raise ConnectionError('Could not connect with {} site, status code: {}'.
                                  format(start_url, response.status_code))

    def download(self, chapter):
        start_url = chapter.url
        url = start_url
        chapter.pages = []
        retrieved_all_pages = False

        while not retrieved_all_pages:
            response = requests.get(url)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                image_src = str(tree.xpath('//*[@id="img"]/@src')[0])
                image = requests.get(image_src, stream=True).content
                chapter.pages.append(image)

                nav_next = str(tree.xpath('//*[@id="navi"]/div[1]/span[2]/a/@href')[0])
                if start_url in nav_next:
                    # next button navigates to next page of a chapter
                    url = nav_next
                else:
                    # next button navigates to next chapter
                    retrieved_all_pages = True
            else:
                raise ConnectionError('Could not connect with {} site, status code: {}'.
                                      format(start_url, response.status_code))
