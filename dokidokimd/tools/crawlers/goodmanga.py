from urllib.parse import urljoin

import requests
from lxml import html

from dokidokimd.manga_site import Manga, Chapter, available_sites, MangaSite
from dokidokimd.tools.kz_logger import KzLogger
from dokidokimd.tools.crawlers.base_crawler import BaseCrawler
from dokidokimd.tools.translator import translate as _

module_logger = KzLogger().get_logger('crawlers.goodmanga')


class GoodMangaCrawler(BaseCrawler):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = available_sites['GoodManga']  # type: str

    def crawl_index(self, manga_site: MangaSite) -> None:
        start_url = urljoin(self.base_url, '/manga-list')

        response = requests.get(start_url)
        if response.status_code == 200:
            manga_site.url = self.base_url

            tree = html.fromstring(response.content)

            for element in tree.xpath('//*[@id="content"]/table/tr/td/a'):
                manga = Manga()
                manga.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                manga.url = str(element.xpath('@href')[0])

                manga_site.add_manga(manga)
        else:
            raise ConnectionError(_('Could not connect with {} site, status code: {}').format(start_url, response.status_code))

    def crawl_detail(self, manga: Manga) -> None:
        start_url = manga.url

        response = requests.get(start_url)
        if response.status_code == 200:
            tree = html.fromstring(response.content)

            # crawl for manga chapters
            for element in tree.xpath('//*[@id="chapters"]/ul/li/a'):
                chapter = Chapter()
                chapter.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                chapter.url = str(element.xpath('@href')[0])

                manga.add_chapter(chapter)

            # TODO 1: crawl for manga details
            # https://api.jikan.moe/

            # chapters are in descending order so
            manga.chapters.reverse()
        else:
            raise ConnectionError(_('Could not connect with {} site, status code: {}').format(start_url, response.status_code))

    def download(self, chapter: Chapter) -> None:
        # FIXME 1: split single page chapters
        start_url = chapter.url
        url = start_url
        chapter.pages = []
        retrieved_all_pages = False

        while not retrieved_all_pages:
            response = requests.get(url)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                image_src = str(tree.xpath('//*[@id="manga_viewer"]/a/img/@src')[0])
                image = requests.get(image_src, stream=True).content
                chapter.pages.append(image)

                try:
                    nav_next = str(tree.xpath('//*[@id="manga_nav_top"]/span/a[2]/@href')[0])
                except IndexError:
                    nav_next = str(tree.xpath('//*[@id="manga_nav_top"]/span/a/@href')[0])
                if start_url in nav_next:
                    # next button navigates to next page of a chapter
                    url = nav_next
                else:
                    # next button navigates to next chapter
                    retrieved_all_pages = True
            else:
                raise ConnectionError(_('Could not connect with {} site, status code: {}').format(start_url, response.status_code))
