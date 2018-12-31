import imghdr
from io import BytesIO
from os import getcwd, remove, rename, listdir, makedirs, unlink, rmdir
from os.path import join, isdir, isfile
from sys import platform
from typing import List, Dict, Tuple, Union

from dokidokimd.convert.make_pdf import PDF
from dokidokimd.core.manga_site import load_dumped_site, MangaSite, Chapter, Manga
from dokidokimd.dd_logger.dd_logger import get_logger
from dokidokimd.net.crawler.base_crawler import BaseCrawler
from dokidokimd.net.crawler.goodmanga import GoodMangaCrawler
from dokidokimd.net.crawler.kissmanga import KissMangaCrawler
from dokidokimd.net.crawler.mangapanda import MangaPandaCrawler
from dokidokimd.translation.translator import translate

_ = translate

if platform == 'linux' or platform == 'linux2':
    pass
elif platform == 'darwin':
    pass
elif platform == 'win32':
    pass

module_logger = get_logger('controller')

MangaCrawlers = {
    'GoodManga': GoodMangaCrawler,
    'MangaPanda': MangaPandaCrawler,
    'KissManga': KissMangaCrawler,
}


def manga_site_2_crawler(site_name) -> Union[BaseCrawler, bool]:
    for name, crawler in MangaCrawlers.items():
        if name.lower() in site_name.lower():
            return crawler()
    return False


class DDMDController:

    @staticmethod
    def available_sites():
        return MangaCrawlers.keys()

    def __init__(self) -> None:
        self.working_dir = getcwd()                                 # type: str
        self.save_location_sites = join(self.working_dir, 'sites')  # type: str

        self.manga_sites = []                                       # type: List[MangaSite]
        self.pdf_converter = PDF()                                  # type: PDF
        self.crawlers = {}                                          # type: Dict[str, BaseCrawler]
        self.load_sites()
        if len(self.manga_sites) == 0:
            for site, crawler in MangaCrawlers.items():
                self.manga_sites.append(MangaSite(site))

    def __get_crawler(self, site_name: str) -> Union[BaseCrawler, bool]:
        """
        This method gets proper crawler for a given site
        :param site_name: String - name of a site
        :return: Appropriate crawler or False if oen does not exist
        """
        if site_name.lower() in (site.lower() for site in self.crawlers):
            return self.crawlers[site_name]
        else:
            crawler = manga_site_2_crawler(site_name)
            if crawler:
                self.crawlers[site_name] = crawler
                return crawler
            else:
                module_logger.error(_('Could not get {} crawler').format(site_name))
                return False

    def get_cwd_string(self, site_number: int = -1, manga_number: int = -1, chapter_number: int = -1) -> str:
        """
        This method produces string representing path to specified place
        :param site_number:
        :param manga_number:
        :param chapter_number:
        :return:
        """
        cwd = '/'
        try:
            if site_number >= 0:
                cwd = '/{}'.format(self.manga_sites[site_number].site_name)
                if manga_number >= 0:
                    cwd = '{}/{}'.format(cwd, self.manga_sites[site_number].mangas[manga_number].title)
                    if chapter_number >= 0:
                        cwd = '{}/{}'.format(cwd, self.manga_sites[site_number].mangas[manga_number].chapters[
                            chapter_number].title)
        except Exception as e:
            module_logger.error(_('Could not build path for site_number={}, manga_number={}, chapter_number={}.\nException message: {}').
                                format(site_number, manga_number, chapter_number, e))
        return cwd

    def is_valid_path(self, site_number: int = None, manga_number: int = None, chapter_number: int = None) -> bool:
        if site_number is None:
            return True
        elif 0 <= site_number <= len(self.manga_sites) - 1:
            if manga_number is None:
                return True
            elif 0 <= manga_number <= len(self.manga_sites[site_number].mangas) - 1:
                if chapter_number is None:
                    return True
                elif 0 <= chapter_number <= len(self.manga_sites[site_number].mangas[manga_number].chapters) - 1:
                    return True
        return False

    def list_sites(self, delimiter: str = '\t') -> str:
        i = 0
        output = _('Current manga sites:')
        for site in self.manga_sites:
            output += (_('{}[{}]:{} with {} mangas').format(delimiter, i, site.site_name, len(site.mangas) if site.mangas is not None else 0))
            i = i + 1
        return output

    def get_sites(self) -> List[Tuple[int, str]]:
        return [(idx, site.site_name) for idx, site in enumerate(self.manga_sites)]

    def list_mangas(self, site_number: int, delimiter: str = '\t') -> str:
        i = 0
        mangas = self.manga_sites[site_number].mangas
        if mangas is None:
            mangas = list()
        output = (_('Site {} contains {} mangas:').format(self.manga_sites[site_number].site_name, len(mangas)))
        for manga in mangas:
            output += (_('{}[{}]:{} with {} chapters').format(delimiter, i, manga.title, len(manga.chapters) if manga.chapters is not None else 0))
            i = i + 1
        return output

    def get_mangas(self, site_number: int) -> List[Tuple[int, str]]:
        return [(idx, manga.title) for idx, manga in enumerate(self.manga_sites[site_number].mangas)]

    def list_chapters(self, site_number: int, manga_number: int, delimiter: str = '\t') -> str:
        i = 0
        chapters = self.manga_sites[site_number].mangas[manga_number].chapters
        manga_title = self.manga_sites[site_number].mangas[manga_number].title
        if chapters is None:
            chapters = list()
        output = (_('Manga {} contains {} chapters:').format(manga_title, len(chapters)))
        for chapter in chapters:
            output += (_('{}[{}]:{} contains {} pages').format(delimiter, i, chapter.title, len(chapter.pages)))
            if delimiter == '\t' and i != 0 and i % 5 == 0:
                output += '\n'
            i = i + 1
        return output

    def get_chapters(self, site_number: int, manga_number: int) -> List[Tuple[int, str]]:
        return [(idx, chapter.title) for idx, chapter in enumerate(self.manga_sites[site_number].mangas[manga_number].chapters)]

    def list_pages(self, site_number: int, manga_number: int, chapter_number: int, delimiter: str = '\t'):
        raise NotImplementedError

    def add_site(self, site_name: str) -> (bool, str):
        sites = [x.lower() for x in MangaCrawlers.keys()]
        if site_name.lower() in sites:
            name, = [x for x in MangaCrawlers.keys() if site_name.lower() == x.lower()]
            self.manga_sites.append(MangaSite(name))
            return True, name
        return False, site_name

    def crawl_site(self, site_number: int) -> MangaSite:
        site = self.manga_sites[site_number]
        crawler = self.__get_crawler(site.site_name)
        if crawler:
            crawler.crawl_index(site)
            return site

    def crawl_manga(self, site_number: int, manga_number: int) -> Manga:
        site = self.manga_sites[site_number]
        manga = self.manga_sites[site_number].mangas[manga_number]
        crawler = self.__get_crawler(site.site_name)
        if crawler:
            crawler.crawl_detail(manga)
            manga.downloaded = True
            return manga

    def crawl_chapter(self, site_number: int, manga_number: int, chapter_number: int) -> Chapter:
        site = self.manga_sites[site_number]
        chapter = self.manga_sites[site_number].mangas[manga_number].chapters[chapter_number]
        crawler = self.__get_crawler(site.site_name)
        if crawler:
            crawler.download(chapter)
            chapter.downloaded = True
            return chapter

    def convert_chapter_2_pdf(self, chapter: Chapter) -> Tuple[bool, str]:
        pdf_dir = join(self.save_location_sites, 'converted', chapter.manga_ref.site_ref.site_name, chapter.manga_ref.get_path_safe_title())
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
            module_logger.error(_('Could not save PDF to {}\nError message: {}').format(pdf_dir, e))
            return False, pdf_dir
        return True, pdf_dir

    def remove_images(self, chapter: Chapter) -> Tuple[bool, str]:
        images_dir = join(self.save_location_sites, 'downloaded', chapter.manga_ref.site_ref.site_name, chapter.manga_ref.get_path_safe_title())
        try:
            if not isdir(images_dir):
                return False, images_dir
            for the_file in listdir(images_dir):
                file_path = join(images_dir, the_file)
                try:
                    if isfile(file_path):
                        unlink(file_path)
                except Exception as e:
                    module_logger.error(_('Could not remove image {}\nError message: {}').format(file_path, e))
            rmdir(images_dir)
            chapter.pages = list()
        except Exception as e:
            module_logger.error(_('Could not remove images from {}\nError message: {}').format(images_dir, e))
            return False, images_dir
        return True, images_dir

    def save_images_from_chapter(self, chapter: Chapter) -> Tuple[bool, str]:
        images_dir = join(self.save_location_sites, 'downloaded', chapter.manga_ref.site_ref.site_name, chapter.manga_ref.get_path_safe_title())
        try:
            if not isdir(images_dir):
                makedirs(images_dir, exist_ok=True)
            idx = 1
            for page in chapter.pages:
                img_type = imghdr.what(BytesIO(page))
                with open(join(images_dir, '{:0>3d}'.format(idx) + '_' + chapter.get_path_safe_title() + '.' + img_type), 'wb') as f:
                    f.write(page)
                    idx += 1
        except Exception as e:
            module_logger.error(_('Could not save images to {}\nError message: {}').format(images_dir, e))
            return False, images_dir
        return True, images_dir

    def store_sites(self) -> bool:
        try:
            if not isdir(self.save_location_sites):
                makedirs(self.save_location_sites, exist_ok=True)
        except Exception as e:
            module_logger.critical(_('Could not make or access directory {}\nError message: {}').format(self.save_location_sites, e))
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
                    module_logger.critical(_('Could not save {} site to a file{}\nError message: {}').format(manga_site.site_name, path_to_file, e))
                    pass
            else:
                with open(path_to_file, 'wb') as the_file:
                    the_file.write(data)

        return True

    def load_sites(self) -> bool:
        self.manga_sites = []
        if not isdir(self.save_location_sites):
            makedirs(self.save_location_sites, exist_ok=True)
            # fresh run
            return False
        for file_name in listdir(self.save_location_sites):
            if not file_name.endswith('.old'):
                if isfile(join(self.save_location_sites, file_name)):
                    # try to load state
                    try:
                        with open(join(self.save_location_sites, file_name), 'rb') as the_file:
                            data = the_file.read()
                            manga_site = load_dumped_site(data)
                            self.manga_sites.append(manga_site)
                    except Exception as e1:
                        # could not load last state, trying older one
                        try:
                            with open('{}.old'.format(join(self.save_location_sites, file_name)), 'rb') as the_file:
                                data = the_file.read()
                                manga_site = load_dumped_site(data)
                                self.manga_sites.append(manga_site)
                        except Exception as e2:
                            pass


if __name__ == '__main__':
    pass
