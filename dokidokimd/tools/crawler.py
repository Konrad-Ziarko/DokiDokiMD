import os
from abc import abstractmethod, ABCMeta
from collections import OrderedDict
from time import sleep
from urllib.parse import urljoin

import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from models import Manga, Chapter, MangaSite
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


def available_sites():
    return MangaCrawlersMap.keys()


class SeleniumDriver(object):
    def __init__(self):
        pass

    def __enter__(self):
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options, firefox_profile=firefox_profile, service_log_path=os.path.devnull)
        self.driver.get('https://www.python.org')
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()


class BaseCrawler:
    __metaclass__ = ABCMeta
    @abstractmethod
    def crawl_index(self, manga_site: MangaSite) -> None:
        raise NotImplementedError

    @abstractmethod
    def crawl_detail(self, manga: Manga) -> None:
        raise NotImplementedError

    @abstractmethod
    def download(self, chapter: Chapter) -> int:
        """
        :return: number of downloaded pages
        """
        raise NotImplementedError


class MangaPandaCrawler(BaseCrawler):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = 'https://www.mangapanda.com/'                           # type: str
        self.manga_index = '/alphabetical'                                      # type: str

        self.re_index_path = '//*[@id="wrapper_body"]/div/div/div/ul/li/a'      # type: str
        self.re_chapter_path = '//*[@id="listing"]/tr/td[1]/a'                  # type: str
        self.re_download_path = '//*[@id="img"]/@src'                           # type: str
        self.re_download_next_path = '//*[@id="navi"]/div[1]/span[2]/a/@href'   # type: str

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
                chapter.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                chapter.url = urljoin(self.base_url, str(element.xpath('@href')[0]))
                manga.add_chapter(chapter)
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
                if nav_next.startswith('/'):
                    nav_next = urljoin(self.base_url, nav_next)
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


class MangaReaderCrawler(MangaPandaCrawler):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = 'https://www.mangareader.net'                           # type: str
        self.manga_index = '/alphabetical'                                      # type: str

        self.re_index_path = '//*[@id="wrapper_body"]/div/div/div/ul/li/a'      # type: str
        self.re_chapter_path = '//*[@id="listing"]/tr/td[1]/a'                  # type: str
        self.re_download_path = '//*[@id="img"]/@src'                           # type: str
        self.re_download_next_path = '//*[@id="navi"]/div[1]/span[2]/a/@href'   # type: str


class MangaSeeCrawler(MangaPandaCrawler):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = 'http://mangaseeonline.us/'                             # type: str
        self.manga_index = '/directory'                                         # type: str

        self.re_index_path = '//*[@id="content"]/p/a'                           # type: str
        self.re_chapter_path = '/html/body/div[1]/div/div[4]/a'                 # type: str
        self.re_download_path = '/html/body/div[2]/div[2]/img/@src'             # type: str
        self.re_download_next_path = '//*[@id="navbar"]/ul/li[3]/a'             # type: str

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


def wait_for_page(driver, x_path):
    wait = True
    while wait:
        sleep(0.5)
        if len(html.fromstring(driver.find_element_by_xpath("//*").get_attribute("outerHTML")).xpath(x_path)) != 0:
            wait = False


class KissMangaCrawler(BaseCrawler):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = 'https://kissmanga.com/'                                            # type: str
        self.manga_index = '/MangaList'                                                     # type: str

        self.re_index_path = '/html/body/div/div/div/div/div/div/table/tbody/tr/td/a'       # type: str
        self.re_index_next_page = '/html/body/div[1]/div[4]/div[2]/div/div[3]/ul/li/a'      # type: str
        self.re_chapter_path = '/html/body/div[1]/div[5]/div[1]/div[2]/div[2]/div[2]/table/tbody/tr/td[1]/a'  # type: str
        self.re_download_path = '/html/body/div[1]/div[4]/div[9]/p/img'                     # type: str

    def crawl_index(self, manga_site: MangaSite) -> None:
        start_url = urljoin(self.base_url, self.manga_index)
        try:
            with SeleniumDriver() as driver:
                collected_all_pages = False
                driver.get(start_url)
                wait_for_page(driver, self.re_index_path)
                manga_site.url = self.base_url
                while collected_all_pages is False:
                    content = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
                    tree = html.fromstring(content)
                    for element in tree.xpath(self.re_index_path):
                        manga = Manga()
                        manga.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                        manga.url = urljoin(self.base_url, str(element.xpath('@href')[0]))
                        manga_site.add_manga(manga)
                    for element2 in tree.xpath(self.re_index_next_page):
                        if 'Next'.lower() in element2.xpath('text()')[0].lower():
                            driver.get(urljoin(self.base_url, element2.xpath('@href')[0]))
                            break
                    else:
                        collected_all_pages = True
        except Exception as e:
            raise ConnectionError(_('Could not connect with {} site, error message: {}').format(start_url, e))

    def crawl_detail(self, manga: Manga) -> None:
        start_url = manga.url
        try:
            with SeleniumDriver() as driver:
                driver.get(start_url)
                wait_for_page(driver, self.re_chapter_path)
                content = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
                tree = html.fromstring(content)
                # crawl for manga chapters
                for element in tree.xpath(self.re_chapter_path):
                    chapter = Chapter()
                    chapter.title = str(element.xpath('text()')[0]).strip().replace('\t', ' ')
                    chapter.url = urljoin(self.base_url, str(element.xpath('@href')[0]))
                    manga.add_chapter(chapter)
        except Exception as e:
            raise ConnectionError(_('Could not connect with {} site, error message: {}').format(start_url, e))

    def download(self, chapter: Chapter) -> int:
        start_url = chapter.url
        try:
            with SeleniumDriver() as driver:
                driver.get(start_url)
                wait_for_page(driver, self.re_download_path)
                chapter.pages = []
                content = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
                tree = html.fromstring(content)
                for element in tree.xpath(self.re_download_path):
                    image_src = str(element.xpath('@src')[0])
                    image = requests.get(image_src, stream=True).content
                    chapter.pages.append(image)
            return len(chapter.pages)
        except Exception as e:
            raise ConnectionError(_('Could not connect with {} site, error message: {}').format(start_url, e))


MangaCrawlersMap = OrderedDict({
    'MangaReader': MangaReaderCrawler,
    'MangaPanda': MangaPandaCrawler,
    'MangaSee': MangaSeeCrawler,
    'KissManga': KissMangaCrawler,
})

