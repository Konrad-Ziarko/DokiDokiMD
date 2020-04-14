import traceback
from functools import lru_cache
from typing import List, Dict, Union

from dokidokimd.models import MangaSite, Chapter, Manga
from dokidokimd.tools.config import ConfigManager
from dokidokimd.tools.crawler import MangaCrawlersMap, BaseCrawler
from dokidokimd.tools.ddmd_logger import get_logger, set_logger_level
from dokidokimd.tools.storage import MangaStorage
from dokidokimd.tools.translator import translate as _

logger = get_logger(__name__)


def manga_site_2_crawler(site_name) -> Union[BaseCrawler, None]:
    for name, crawler in MangaCrawlersMap.items():
        if name.lower() in site_name.lower():
            return crawler()
    return None


class DDMDController:
    def __init__(self, config) -> None:
        self.config = config                                        # type: ConfigManager
        self.ddmd_storage = MangaStorage()                          # type: MangaStorage
        set_logger_level(self.config.log_level)

        self.cwd_site = None                                        # type: MangaSite
        self.cwd_manga = None                                       # type: Manga
        self.cwd_chapter = None                                     # type: Chapter

        self.manga_sites = []                                       # type: List[MangaSite]
        self.crawlers = {}                                          # type: Dict[str, BaseCrawler]
        self.load_db()
        logger.info(_('Program started'))

    def load_db(self):
        self.manga_sites = []
        self.crawlers = {}
        self.manga_sites = self.ddmd_storage.load_sites(self.sites_location)
        if len(self.manga_sites) == 0 or len(self.manga_sites) != len(MangaCrawlersMap.items()):
            current_sites = [site.site_name for site in self.manga_sites]
            for site in MangaCrawlersMap.keys():
                if site not in current_sites:
                    self.manga_sites.append(MangaSite(site))

    def store_sites(self):
        self.ddmd_storage.store_sites(self.sites_location, self.manga_sites)

    @property
    def sites_location(self):
        return self.config.db_path

    @sites_location.setter
    def sites_location(self, path: str):
        self.config.db_path = path

    def _reset_cwd(self):
        self.cwd_chapter = self.cwd_manga = self.cwd_site = None

    @lru_cache()
    def __get_crawler(self, site_name: str) -> Union[BaseCrawler, bool]:
        """
        This method gets proper crawlers for a given site
        :param site_name: String - name of a site
        :return: Appropriate crawlers or False if oen does not exist
        """
        if site_name.lower() in (site.lower() for site in self.crawlers):
            return self.crawlers[site_name]
        else:
            crawler = manga_site_2_crawler(site_name)
            if crawler:
                self.crawlers[site_name] = crawler
                return crawler
            else:
                logger.error(_(F'Could not get {site_name} crawlers'))
                return False

    def set_cwd_site(self, site: MangaSite):
        self.cwd_site = site
        self.cwd_manga = self.cwd_chapter = None

    def set_cwd_manga(self, manga: Manga):
        self.cwd_manga = manga
        self.cwd_chapter = None

    def set_cwd_chapter(self, chapter: Chapter):
        self.cwd_chapter = chapter

    def get_current_site(self):
        return self.cwd_site

    def get_sites(self) -> List[MangaSite]:
        return [site for site in self.manga_sites]

    def get_current_manga(self):
        return self.cwd_manga

    def crawl_site(self) -> MangaSite:
        site = self.cwd_site
        crawler = self.__get_crawler(site.site_name)
        if crawler:
            crawler.crawl_index(site)
            return site

    def crawl_manga(self) -> Manga:
        site = self.cwd_site
        manga = self.cwd_manga
        crawler = self.__get_crawler(site.site_name)
        if crawler:
            crawler.crawl_detail(manga)
            manga.downloaded = True
            return manga

    def crawl_chapter(self, chapter: Chapter):
            site = self.cwd_site
            crawler = self.__get_crawler(site.site_name)
            if crawler:
                crawler.download(chapter)
                chapter.set_downloaded(True)
