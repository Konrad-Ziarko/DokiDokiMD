import imghdr
from io import BytesIO
from os import getcwd, remove, rename, listdir, makedirs, unlink, rmdir
from os.path import join, isdir, isfile
from typing import List, Dict, Tuple, Union

from models import load_dumped_site, MangaSite, Chapter, Manga
from tools.config import ConfigManager
from tools.crawler import MangaCrawlersMap, BaseCrawler
from tools.kz_logger import get_logger
from tools.make_pdf import PDF
from tools.translator import translate as _

logger = get_logger(__name__)


def manga_site_2_crawler(site_name) -> Union[BaseCrawler, None]:
    for name, crawler in MangaCrawlersMap.items():
        if name.lower() in site_name.lower():
            return crawler()
    return None


class DDMDController:
    def __init__(self, config) -> None:
        self.config = config                                        # type: ConfigManager

        self.site_extension = 'ddmd'                                # type: str
        self.old_site_extension = 'old'                                # type: str

        self.downloaded_pages = 0                                   # type: int
        self.downloaded_chapters = 0                                # type: int
        self.converted_chapters = 0                                 # type: int

        self.cwd_site = None                                        # type: MangaSite
        self.cwd_manga = None                                       # type: Manga
        self.cwd_chapter = None                                     # type: Chapter
        self.cwd_page = -1                                          # type: int

        self.start_dir = getcwd()                                   # type: str
        if self.sites_location == '':
            self.sites_location = join(self.start_dir, 'sites')
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
            number_of_pages = crawler.download(chapter)
            chapter.set_downloaded()
            self.downloaded_pages += number_of_pages
            self.downloaded_chapters += 1
            return chapter

    def chapter_images_present(self, chapter: Chapter) -> bool:
        images_dir = join(self.sites_location, 'downloaded', chapter.manga_ref.site_ref.site_name,
                          chapter.manga_ref.get_path_safe_title(), chapter.get_path_safe_title())
        if not isdir(images_dir):
            return False
        if not listdir(images_dir):
            return False
        return True

    def convert_images_2_pdf(self, chapter: Chapter) -> Tuple[bool, str]:
        """
        Convert images stored on disk
        """
        pdf_dir = chapter.get_convert_path(self.sites_location)
        images_dir = chapter.get_download_path(self.sites_location)
        if not isdir(images_dir):
            logger.warning(_('Could not convert to PDF, source path with images does not exist'))
            return False, pdf_dir
        try:
            if not isdir(pdf_dir):
                makedirs(pdf_dir, exist_ok=True)
            pdf_converter = PDF()
            pdf_converter.clear_pages()
            pdf_converter.add_dir(images_dir)
            pdf_converter.make_pdf(chapter.title, join(pdf_dir, F'{chapter.get_path_safe_title()}.pdf'))
            chapter.converted = True
            self.converted_chapters += 1
        except Exception as e:
            logger.error(_(F'Could not save PDF to {pdf_dir}\nError message: {e}'))
            return False, pdf_dir
        return True, pdf_dir

    def convert_chapter_2_pdf(self, chapter: Chapter) -> Tuple[bool, str]:
        """
        Convert freshly downloaded chapter (stored only in memory)
        """
        pdf_dir = chapter.get_convert_path(self.sites_location)
        try:
            if not isdir(pdf_dir):
                makedirs(pdf_dir, exist_ok=True)
            pdf_converter = PDF()
            pdf_converter.clear_pages()
            pdf_converter.add_chapter(chapter)
            pdf_converter.make_pdf(chapter.title, join(pdf_dir, F'{chapter.get_path_safe_title()}.pdf'))
            chapter.converted = True
            self.converted_chapters += 1
        except Exception as e:
            logger.error(_(F'Could not save PDF to {pdf_dir}\nError message: {e}'))
            return False, pdf_dir
        return True, pdf_dir

    def remove_chapter_images(self, chapter: Chapter) -> Tuple[bool, str]:
        images_dir = chapter.get_download_path(self.sites_location)
        try:
            if not isdir(images_dir):
                return False, images_dir
            for the_file in listdir(images_dir):
                file_path = join(images_dir, the_file)
                try:
                    if isfile(file_path):
                        unlink(file_path)
                except Exception as e:
                    logger.error(_(F'Could not remove image {file_path}\nError message: {e}'))
            rmdir(images_dir)
            chapter.pages = list()
        except Exception as e:
            logger.error(_(F'Could not remove images from {images_dir}\nError message: {e}'))
            return False, images_dir
        return True, images_dir

    def save_images_from_chapter(self, chapter: Chapter) -> Tuple[bool, str]:
        images_dir = chapter.get_download_path(self.sites_location)
        try:
            if not isdir(images_dir):
                makedirs(images_dir, exist_ok=True)
            for idx, page in enumerate(chapter.pages):
                img_type = imghdr.what(BytesIO(page))
                path = join(images_dir, F'{idx:0>3d}.{img_type}')
                with open(path, 'wb') as f:
                    f.write(page)
        except Exception as e:
            logger.error(_(F'Could not save images to {images_dir}\nError message: {e}'))
            return False, images_dir
        chapter.saved = True
        return True, images_dir

    def store_sites(self) -> bool:
        try:
            if not isdir(self.sites_location):
                makedirs(self.sites_location, exist_ok=True)
        except Exception as e:
            logger.critical(_(F'Could not make or access directory {self.sites_location}\nError message: {e}'))
            return False

        for manga_site in self.manga_sites:
            data = manga_site.dump()

            path_to_file = join(self.sites_location, F'{manga_site.site_name}.{self.site_extension}')
            path_to_old_file = F'{path_to_file}.{self.old_site_extension}'

            if isfile(path_to_file):
                # check if old file exists and remove it
                if isfile(path_to_old_file):
                    remove(path_to_old_file)
                # rename current file
                rename(path_to_file, path_to_old_file)
                try:
                    # create new file
                    with open(path_to_file, 'wb') as the_file:
                        the_file.write(data)
                except Exception as e:
                    logger.critical(_(F'Could not save {manga_site.site_name} site to a file{path_to_file}\nError message: {e}'))
            else:
                with open(path_to_file, 'wb') as the_file:
                    the_file.write(data)
        logger.info(_('Data saved to DB'))
        logger.info(_(F'Stats: Downloaded Pages({self.downloaded_pages}), Downloaded Chapters ({self.downloaded_chapters}), Converted PDFs ({self.converted_chapters})'))
        return True

    def load_sites(self) -> bool:
        self.manga_sites = []
        if not isdir(self.sites_location):
            makedirs(self.sites_location, exist_ok=True)
            logger.info(_('No saved state. Creating dir for fresh DB'))
            return False
        for file_name in listdir(self.sites_location):
            if not file_name.endswith(F'.{self.old_site_extension}') and file_name.endswith(self.site_extension):
                if isfile(join(self.sites_location, file_name)):
                    logger.info(_(F'Loading last state for {file_name}'))
                    try:
                        with open(join(self.sites_location, file_name), 'rb') as the_file:
                            data = the_file.read()
                            manga_site = load_dumped_site(data)
                            self.manga_sites.append(manga_site)
                    except Exception as e1:
                        logger.warning(_(
                            F'Could not load last state, trying older one. Error message: {e1}'))
                        try:
                            with open(F'{join(self.sites_location, file_name)}.{self.old_site_extension}', 'rb') as the_file:
                                data = the_file.read()
                                manga_site = load_dumped_site(data)
                                self.manga_sites.append(manga_site)
                        except Exception as e2:
                            logger.warning(_(
                                F'Could not load old last state either. Error message: {e2}'))


