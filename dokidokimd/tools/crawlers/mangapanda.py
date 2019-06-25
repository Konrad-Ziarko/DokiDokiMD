from urllib.parse import urljoin

import requests
from lxml import html

from manga_site import Manga, Chapter, available_sites, MangaSite
from tools.kz_logger import get_logger
from tools.crawlers.base_crawler import BaseCrawler
from tools.translator import translate as _

logger = get_logger(__name__)


class MangaPandaCrawler(BaseCrawler):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = available_sites['MangaPanda']  # type: str

    def crawl_index(self, manga_site: MangaSite) -> None:
        start_url = urljoin(self.base_url, '/alphabetical')

        response = requests.get(start_url)

        if response.status_code == 200:
            manga_site.url = self.base_url

            tree = html.fromstring(response.content)

            for element in tree.xpath('//*[@id="wrapper_body"]/div/div/div/ul/li/a'):
                manga = Manga()
                manga.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                manga.url = urljoin(self.base_url, str(element.xpath('@href')[0]))

                manga_site.add_manga(manga)
        else:
            raise ConnectionError(_('Could not connect with {} site, status code: {}').format(start_url, response.status_code))

    def crawl_detail(self, manga: Manga) -> None:
        start_url = manga.url

        response = requests.get(start_url)
        if response.status_code == 200:
            tree = html.fromstring(response.content)

            # crawl for manga chapters
            for element in tree.xpath('//*[@id="listing"]/tr/td[1]/a'):
                chapter = Chapter()
                chapter.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                chapter.url = urljoin(self.base_url, str(element.xpath('@href')[0]))

                manga.add_chapter(chapter)

            # TODO 1: crawl for manga details
            # https://api.jikan.moe/

        else:
            raise ConnectionError(_('Could not connect with {} site, status code: {}').format(start_url, response.status_code))

    def download(self, chapter: Chapter) -> int:
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
                if nav_next.startswith('/'):
                    nav_next = 'https://www.mangapanda.com{}'.format(nav_next)
                if start_url in nav_next:
                    # next button navigates to next page of a chapter
                    url = nav_next
                else:
                    # next button navigates to next chapter
                    retrieved_all_pages = True
            else:
                raise ConnectionError(_('Could not connect with {} site, status code: {}').format(start_url, response.status_code))
        return len(chapter.pages)
