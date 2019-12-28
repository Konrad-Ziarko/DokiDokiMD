import imghdr
import os
from io import BytesIO
from typing import List, Dict, Tuple, Union

from dokidokimd import DATA_DIR
from dokidokimd.models import MangaSite, Chapter, Manga
from dokidokimd.tools.config import ConfigManager
from dokidokimd.tools.crawler import MangaCrawlersMap, BaseCrawler
from dokidokimd.tools.ddmd_logger import get_logger, set_logger_level
from dokidokimd.tools.translator import translate as _

logger = get_logger(__name__)


def manga_site_2_crawler(site_name) -> Union[BaseCrawler, None]:
    for name, crawler in MangaCrawlersMap.items():
        if name.lower() in site_name.lower():
            return crawler()
    return None


class DDMDController:
    def __init__(self, config, start_dir) -> None:
        self.config = config                                        # type: ConfigManager
        self.site_extension = 'ddmd'                                # type: str

        self.cwd_site = None                                        # type: MangaSite
        self.cwd_manga = None                                       # type: Manga
        self.cwd_chapter = None                                     # type: Chapter
        self.cwd_page = -1                                          # type: int

        set_logger_level(self.config.log_level)
        logger.info(_('Program started'))
        if self.sites_location == '':
            self.sites_location = os.path.join(start_dir, DATA_DIR, 'sites')
        self.manga_sites = []                                       # type: List[MangaSite]
        self.crawlers = {}                                          # type: Dict[str, BaseCrawler]
        self.load_db()

    def load_db(self):
        self.manga_sites = []
        self.crawlers = {}
        self.load_sites()
        if len(self.manga_sites) == 0 or len(self.manga_sites) != len(MangaCrawlersMap.items()):
            current_sites = [site.site_name for site in self.manga_sites]
            for site in MangaCrawlersMap.keys():
                if site not in current_sites:
                    self.manga_sites.append(MangaSite(site))

    @property
    def sites_location(self):
        return self.config.db_path

    @sites_location.setter
    def sites_location(self, path: str):
        self.config.db_path = path

    def _reset_cwd(self):
        self.cwd_chapter = self.cwd_manga = self.cwd_site = self.cwd_page = None

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
        self.cwd_manga = self.cwd_chapter = self.cwd_page = None

    def set_cwd_manga(self, manga: Manga):
        self.cwd_manga = manga
        self.cwd_chapter = self.cwd_page = None

    def set_cwd_chapter(self, chapter: Chapter):
        self.cwd_chapter = chapter
        self.cwd_page = None

    def list_sites(self, delimiter: str = '\t') -> str:
        i = 0
        output = _('Current manga sites:')
        for site in self.manga_sites:
            output += (_(F'{delimiter}[{i}]:{site.site_name} with {len(site.mangas) if site.mangas is not None else 0} mangas'))
            i = i + 1
        return output

    def get_current_site(self):
        return self.cwd_site

    def get_sites(self) -> List[MangaSite]:
        return [site for site in self.manga_sites]

    def list_mangas(self, delimiter: str = '\t') -> str:
        i = 0
        site = self.cwd_site
        if site.mangas is None:
            site.mangas = list()
        output = (_(F'Site {site.site_name} contains {len(site.mangas)} mangas:'))
        for manga in site.mangas:
            output += (_(F'{delimiter}[{i}]:{manga.title} with {len(manga.chapters) if manga.chapters is not None else 0} chapters'))
            i = i + 1
        return output

    def get_current_manga(self):
        return self.cwd_manga

    def get_mangas(self, ) -> List[Tuple[int, str]]:
        return [(idx, manga.title) for idx, manga in enumerate(self.cwd_site.mangas)]

    def list_chapters(self, delimiter: str = '\t') -> str:
        i = 0
        manga = self.cwd_manga
        if manga.chapters is None:
            manga.chapters = list()
        output = (_(F'Manga {manga.title} contains {len(manga.chapters)} chapters:'))
        for chapter in manga.chapters:
            output += (_(F'{delimiter}[{i}]:{chapter.title} contains {len(chapter.pages)} pages'))
            if delimiter == '\t' and i != 0 and i % 5 == 0:
                output += '\n'
            i = i + 1
        return output

    def get_chapters(self) -> List[Tuple[int, str]]:
        return [(idx, chapter.title) for idx, chapter in enumerate(self.cwd_manga.chapters)]

    def list_pages(self, delimiter: str = '\t'):
        raise NotImplementedError

    def add_site(self, site_name: str) -> (bool, str):
        sites = [x.lower() for x in MangaCrawlersMap.keys()]
        if site_name.lower() in sites:
            name, = [x for x in MangaCrawlersMap.keys() if site_name.lower() == x.lower()]
            self.manga_sites.append(MangaSite(name))
            return True, name
        return False, site_name

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

    def crawl_chapter(self, chapter: Chapter) -> Chapter:
        site = self.cwd_site
        crawler = self.__get_crawler(site.site_name)
        if crawler:
            crawler.download(chapter)
            chapter.set_downloaded()
            return chapter

    def store_sites(self) -> bool:
        try:
            if not os.path.isdir(self.sites_location):
                os.makedirs(self.sites_location, exist_ok=True)
        except Exception as e:
            logger.critical(_(F'Could not make or access directory {self.sites_location}\nError message: {e}'))
            return False

        for manga_site in self.manga_sites:
            data = manga_site.dump()
            path_to_file = os.path.join(self.sites_location, F'{manga_site.site_name}.{self.site_extension}')

            try:
                # create new file
                with open(path_to_file, 'wb') as the_file:
                    the_file.write(data)
            except Exception as e:
                logger.critical(_(F'Could not save {manga_site.site_name} site to a file{path_to_file}\nError message: {e}'))
        return True

    def load_sites(self) -> None:
        self.manga_sites = []
        if not os.path.isdir(self.sites_location):
            os.makedirs(self.sites_location, exist_ok=True)
            logger.info(_('No saved state. Creating dir for fresh DB'))
        for file_name in os.listdir(self.sites_location):
            if file_name.endswith(self.site_extension):
                if os.path.isfile(os.path.join(self.sites_location, file_name)):
                    logger.info(_(F'Loading last state for {file_name}'))
                    try:
                        with open(os.path.join(self.sites_location, file_name), 'rb') as the_file:
                            data = the_file.read()
                            manga_site = MangaSite.load_dumped_site(data)
                            self.manga_sites.append(manga_site)
                    except Exception as e1:
                        logger.warning(_(F'Could not load last state. Error message: {e1}'))
