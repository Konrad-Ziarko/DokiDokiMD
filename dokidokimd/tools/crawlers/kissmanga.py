from urllib.parse import urljoin

import requests
from lxml import html

from manga_site import Manga, Chapter, MangaSite
from tools.crawlers.base_crawler import BaseCrawler
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


class KissMangaCrawler(BaseCrawler):
    # TODO use selenium to bypass cloudflair

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = 'http://kissmanga.com/'                                             # type: str
        self.manga_index = '/MangaList'                                                     # type: str

        self.re_index_path = '//*[@id="leftside"]/div/div[2]/div[4]/table/tr/td[1]/a'       # type: str
        self.re_chapter_path = '//*[@id="listing"]/tr/td[1]/a'                              # type: str
        self.re_download_path = '//*[@id="img"]/@src'                                       # type: str
        self.re_download_next_path = '//*[@id="navi"]/div[1]/span[2]/a/@href'               # type: str

    def crawl_index(self, manga_site: MangaSite) -> None:
        start_url = urljoin(self.base_url, self.re_index_path)
        with requests.Session() as session:
            response = session.get(start_url, allow_redirects=True)
            if response.status_code == 200:
                manga_site.url = self.base_url

                tree = html.fromstring(response.content)

                for element in tree.xpath(self.re_chapter_path):
                    manga = Manga()
                    manga.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                    manga.url = urljoin(self.base_url, str(element.xpath('@href')[0]))

                    manga_site.add_manga(manga)
            else:
                raise ConnectionError(
                    _('Could not connect with {} site, status code: {}').format(start_url, response.status_code))

    def crawl_detail(self, manga: Manga) -> None:
        start_url = manga.url

        response = requests.get(start_url)
        if response.status_code == 200:
            tree = html.fromstring(response.content)

            # crawl for manga chapters
            for element in tree.xpath(self.re_chapter_path):
                chapter = Chapter()
                chapter.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                chapter.url = urljoin(self.base_url, str(element.xpath('@href')[0]))

                manga.add_chapter(chapter)

            # TODO 1: crawl for manga details
            # https://api.jikan.moe/

        else:
            raise ConnectionError(
                _('Could not connect with {} site, status code: {}').format(start_url, response.status_code))

    def download(self, chapter: Chapter) -> int:
        start_url = chapter.url
        url = start_url
        chapter.pages = []
        retrieved_all_pages = False

        while not retrieved_all_pages:
            response = requests.get(url)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                image_src = str(tree.xpath(self.re_download_path)[0])
                image = requests.get(image_src, stream=True).content
                chapter.pages.append(image)

                nav_next = str(tree.xpath(self.re_download_next_path)[0])
                if start_url in nav_next:
                    # next button navigates to next page of a chapter
                    url = nav_next
                else:
                    # next button navigates to next chapter
                    retrieved_all_pages = True
            else:
                raise ConnectionError(
                    _('Could not connect with {} site, status code: {}').format(start_url, response.status_code))
        return len(chapter.pages)
