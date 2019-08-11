from urllib.parse import urljoin

import requests
from lxml import html

from models import Manga, Chapter, MangaSite
from tools.crawlers.base_crawler import BaseCrawler
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


class MangaSeeCrawler(BaseCrawler):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = 'http://mangaseeonline.us/'                             # type: str
        self.manga_index = '/directory'                                         # type: str

        self.re_index_path = '//*[@id="content"]/p/a'                           # type: str
        self.re_chapter_path = '/html/body/div[1]/div/div[4]/a'                 # type: str
        self.re_download_path = '/html/body/div[2]/div[2]/img/@src'             # type: str
        self.re_download_next_path = '//*[@id="navbar"]/ul/li[3]/a'             # type: str

    def crawl_index(self, manga_site: MangaSite) -> None:
        start_url = urljoin(self.base_url, self.manga_index)
        response = requests.get(start_url)
        if response.status_code == 200:
            manga_site.url = self.base_url
            tree = html.fromstring(response.content)
            for element in tree.xpath(self.re_index_path):
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
            for element in tree.xpath(self.re_chapter_path):
                chapter = Chapter()
                chapter.title = str(element.xpath('span/text()')[0]).strip().replace('\t', ' ')
                chapter.url = urljoin(self.base_url, str(element.xpath('@href')[0]))

                manga.add_chapter(chapter, True)
        else:
            raise ConnectionError(
                _('Could not connect with {} site, status code: {}').format(start_url, response.status_code))

    def download(self, chapter: Chapter) -> int:
        start_url = chapter.url
        url = start_url
        chapter.pages = []
        with requests.Session() as s:
            response = s.get(url)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                for page_num in range(1, 1 + len(tree.xpath('/html/body/div[2]/div[4]/div/div/span/select[2]/option'))):
                    image_src = str(tree.xpath(self.re_download_path)[0])
                    image = s.get(image_src, stream=True).content
                    chapter.pages.append(image)
                    url = start_url[:-6] + str(page_num) + start_url[-5:]
                    response = s.get(url)
                    tree = html.fromstring(response.content)
            else:
                raise ConnectionError(
                    _('Could not connect with {} site, status code: {}').format(start_url, response.status_code))
        return len(chapter.pages)
