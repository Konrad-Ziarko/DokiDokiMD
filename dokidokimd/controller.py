import imghdr
from io import BytesIO
from os import getcwd, remove, rename, listdir, makedirs, unlink, rmdir
from os.path import join, isdir, isfile
from sys import platform
from typing import List, Dict, Tuple, Union

from tools.make_pdf import PDF
from manga_site import load_dumped_site, MangaSite, Chapter, Manga
from tools.kz_logger import get_logger
from tools.crawlers.base_crawler import BaseCrawler
from tools.crawlers.mangareader import MangareaderCrawler
from tools.crawlers.kissmanga import KissMangaCrawler
from tools.crawlers.mangapanda import MangaPandaCrawler
from tools.translator import translate as _

if platform == 'linux' or platform == 'linux2':
    pass
elif platform == 'darwin':
    pass
elif platform == 'win32':
    pass

logger = get_logger(__name__)

MangaCrawlers = {
    'Mangareader': MangareaderCrawler,
    'MangaPanda': MangaPandaCrawler,
    'KissManga': KissMangaCrawler,
}


def available_sites():
    return MangaCrawlers.keys()


def manga_site_2_crawler(site_name) -> Union[BaseCrawler, None]:
    for name, crawler in MangaCrawlers.items():
        if name.lower() in site_name.lower():
            return crawler()
    return None


class DDMDController:
    def __init__(self) -> None:
        self.cwd_site = None                                        # type: MangaSite
        self.cwd_manga = None                                       # type: Manga
        self.cwd_chapter = None                                     # type: Chapter
        self.cwd_page = -1                                          # type: int

        self.working_dir = getcwd()                                 # type: str
        self.save_location_sites = join(self.working_dir, 'sites')  # type: str

        self.manga_sites = []                                       # type: List[MangaSite]
        self.pdf_converter = PDF()                                  # type: PDF
        self.crawlers = {}                                          # type: Dict[str, BaseCrawler]
        self.load_sites()
        if len(self.manga_sites) == 0 or len(self.manga_sites) != len(MangaCrawlers.items()):
            current_sites = [site.site_name for site in self.manga_sites]
            for site, crawler in MangaCrawlers.items():
                if site not in current_sites:
                    self.manga_sites.append(MangaSite(site))

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
                logger.error(_('Could not get {} crawlers').format(site_name))
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

    def get_cwd_string(self) -> str:
        """
        This method produces string representing path to specified place
        :return: String representing current working directory
        """
        cwd = '/'
        try:
            if self.cwd_site:
                tmp = self.cwd_site
                cwd += '{}'.format(tmp.site_name)
                if self.cwd_manga:
                    tmp = tmp.mangas[self.cwd_manga]
                    cwd += '/{}'.format(tmp.title)
                    if self.cwd_chapter:
                        tmp = tmp.chapters[self.cwd_chapter]
                        cwd += '/{}'.format(tmp.title)
                        if self.cwd_page:
                            cwd += '/{}'.format(self.cwd_page)
        except Exception as e:
            logger.error(_('Could not build path for site_number={}, manga_number={}, chapter_number={}, page={}.\n'
                                  'Exception message: {}').format(self.cwd_site, self.cwd_manga, self.cwd_chapter, self.cwd_page, e))
            self._reset_cwd()
        return cwd

    def list_sites(self, delimiter: str = '\t') -> str:
        i = 0
        output = _('Current manga sites:')
        for site in self.manga_sites:
            output += (_('{}[{}]:{} with {} mangas').format(
                delimiter, i, site.site_name, len(site.mangas) if site.mangas is not None else 0))
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
        output = (_('Site {} contains {} mangas:').format(site.site_name, len(site.mangas)))
        for manga in site.mangas:
            output += (_('{}[{}]:{} with {} chapters').format(
                delimiter, i, manga.title, len(manga.chapters) if manga.chapters is not None else 0))
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
        output = (_('Manga {} contains {} chapters:').format(manga.title, len(manga.chapters)))
        for chapter in manga.chapters:
            output += (_('{}[{}]:{} contains {} pages').format(delimiter, i, chapter.title, len(chapter.pages)))
            if delimiter == '\t' and i != 0 and i % 5 == 0:
                output += '\n'
            i = i + 1
        return output

    def get_chapters(self) -> List[Tuple[int, str]]:
        return [(idx, chapter.title) for idx, chapter in enumerate(self.cwd_manga.chapters)]

    def list_pages(self, delimiter: str = '\t'):
        raise NotImplementedError

    def add_site(self, site_name: str) -> (bool, str):
        sites = [x.lower() for x in MangaCrawlers.keys()]
        if site_name.lower() in sites:
            name, = [x for x in MangaCrawlers.keys() if site_name.lower() == x.lower()]
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
            chapter.downloaded = True
            return chapter

    def convert_chapter_2_pdf(self, chapter: Chapter) -> Tuple[bool, str]:
        pdf_dir = join(self.save_location_sites, 'converted', chapter.manga_ref.site_ref.site_name,
                       chapter.manga_ref.get_path_safe_title())
        try:
            if not isdir(pdf_dir):
                makedirs(pdf_dir, exist_ok=True)
            self.pdf_converter.clear_pages()
            self.pdf_converter.add_chapter(chapter)
            self.pdf_converter.make_pdf(chapter.title)
            self.pdf_converter.save_pdf(join(pdf_dir, chapter.get_path_safe_title()))
            self.pdf_converter.clear_pages()
            chapter.converted = True
        except Exception as e:
            logger.error(_('Could not save PDF to {}\nError message: {}').format(pdf_dir, e))
            return False, pdf_dir
        return True, pdf_dir

    def remove_images(self, chapter: Chapter) -> Tuple[bool, str]:
        images_dir = join(self.save_location_sites, 'downloaded', chapter.manga_ref.site_ref.site_name,
                          chapter.manga_ref.get_path_safe_title())
        try:
            if not isdir(images_dir):
                return False, images_dir
            for the_file in listdir(images_dir):
                file_path = join(images_dir, the_file)
                try:
                    if isfile(file_path):
                        unlink(file_path)
                except Exception as e:
                    logger.error(_('Could not remove image {}\nError message: {}').format(file_path, e))
            rmdir(images_dir)
            chapter.pages = list()
        except Exception as e:
            logger.error(_('Could not remove images from {}\nError message: {}').format(images_dir, e))
            return False, images_dir
        return True, images_dir

    def save_images_from_chapter(self, chapter: Chapter) -> Tuple[bool, str]:
        images_dir = join(self.save_location_sites, 'downloaded', chapter.manga_ref.site_ref.site_name,
                          chapter.manga_ref.get_path_safe_title(), chapter.get_path_safe_title())
        try:
            if not isdir(images_dir):
                makedirs(images_dir, exist_ok=True)
            for idx, page in enumerate(chapter.pages):
                img_type = imghdr.what(BytesIO(page))
                path = join(images_dir, '{:0>2d}_{}.{}'.format(idx, chapter.get_path_safe_title(), img_type))
                with open(path, 'wb') as f:
                    f.write(page)
        except Exception as e:
            logger.error(_('Could not save images to {}\nError message: {}').format(images_dir, e))
            return False, images_dir
        chapter.saved = True
        return True, images_dir

    def store_sites(self) -> bool:
        try:
            if not isdir(self.save_location_sites):
                makedirs(self.save_location_sites, exist_ok=True)
        except Exception as e:
            logger.critical(_('Could not make or access directory {}\nError message: {}').format(
                self.save_location_sites, e))
            return False

        for manga_site in self.manga_sites:
            data = manga_site.dump()

            path_to_file = join(self.save_location_sites, manga_site.site_name)
            path_to_old_file = '{}.old'.format(path_to_file)

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
                    logger.critical(_('Could not save {} site to a file{}\nError message: {}').format(
                        manga_site.site_name, path_to_file, e))
                    pass
            else:
                with open(path_to_file, 'wb') as the_file:
                    the_file.write(data)
        logger.info(_('Data saved to DB'))
        return True

    def load_sites(self) -> bool:
        self.manga_sites = []
        if not isdir(self.save_location_sites):
            makedirs(self.save_location_sites, exist_ok=True)
            logger.info(_('No saved state. Creating dir for fresh DB'))
            return False
        for file_name in listdir(self.save_location_sites):
            if not file_name.endswith('.old'):
                if isfile(join(self.save_location_sites, file_name)):
                    logger.info(_('Loading last state for {}').format(file_name))
                    try:
                        with open(join(self.save_location_sites, file_name), 'rb') as the_file:
                            data = the_file.read()
                            manga_site = load_dumped_site(data)
                            self.manga_sites.append(manga_site)
                    except Exception as e1:
                        logger.warning(_(
                            'Could not load last state, trying older one. Error message: {}').format(e1))
                        try:
                            with open('{}.old'.format(join(self.save_location_sites, file_name)), 'rb') as the_file:
                                data = the_file.read()
                                manga_site = load_dumped_site(data)
                                self.manga_sites.append(manga_site)
                        except Exception as e2:
                            logger.warning(_(
                                'Could not load old last state either. Error message: {}').format(e2))


if __name__ == '__main__':
    pass
