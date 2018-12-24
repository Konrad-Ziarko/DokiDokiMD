from os import getcwd, mkdir, remove, rename, listdir
from os.path import join, isdir, isfile
from sys import platform

from dokidokimd.convert.make_pdf import PDF
from dokidokimd.core.manga_site import load_dumped_site, MangaSite
from dokidokimd.logging.logger import get_logger
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


def manga_site_2_crawler(site_name):
    for name, crawler in MangaCrawlers.items():
        if name.lower() in site_name.lower():
            return crawler()
    return False


class DDMDController:

    @staticmethod
    def available_sites():
        return MangaCrawlers.keys()

    def __init__(self):
        self.working_dir = getcwd()
        self.save_location_sites = join(self.working_dir, 'sites')

        self.manga_sites = []
        self.pdf_converter = PDF()
        self.crawlers = {}
        self.load_sites()
        if len(self.manga_sites) == 0:
            for site, crawler in MangaCrawlers.items():
                self.manga_sites.append(MangaSite(site))

    def __get_crawler(self, site_name):
        """
        This method gets proper crawler for a given site
        :param site_name: String - name of a site
        :return: Appropriate crawler or False if oen does not exist
        """
        if site_name.lower() in (site.lower() for site in self.crawlers):
            return self.crawlers[site_name]
        else:
            crawler = manga_site_2_crawler(site_name)
            if crawler is False:
                return False
            else:
                self.crawlers[site_name] = crawler
                return crawler

    def get_cwd_string(self, site_number=-1, manga_number=-1, chapter_number=-1):
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
            module_logger.error(_('Could not build path for site_number={}, manga_number={}, chapter_number={}').format(site_number, manga_number, chapter_number))
        return cwd

    def is_valid_path(self, site_number=None, manga_number=None, chapter_number=None):
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

    def list_sites(self, delimiter='\t'):
        i = 0
        output = _('Current manga sites:')
        for site in self.manga_sites:
            output += (_('{}[{}]:{} with {} mangas').format(delimiter, i, site.site_name, len(site.mangas) if site.mangas is not None else 0))
            i = i + 1
        return output

    def get_sites(self):
        return [(idx, site.site_name) for idx, site in enumerate(self.manga_sites)]

    def list_mangas(self, site_number, delimiter='\t'):
        i = 0
        mangas = self.manga_sites[site_number].mangas
        if mangas is None:
            mangas = list()
        output = (_('Site {} contains {} mangas:').format(self.manga_sites[site_number].site_name, len(mangas)))
        for manga in mangas:
            output += (_('{}[{}]:{} with {} chapters').format(delimiter, i, manga.title, len(manga.chapters) if manga.chapters is not None else 0))
            i = i + 1
        return output

    def get_mangas(self, site_number):
        return [(idx, manga.title) for idx, manga in enumerate(self.manga_sites[site_number].mangas)]

    def list_chapters(self, site_number, manga_number, delimiter='\t'):
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

    def get_chapters(self, site_number, manga_number):
        return [(idx, chapter.title) for idx, chapter in enumerate(self.manga_sites[site_number].mangas[manga_number])]

    def list_pages(self, site_number, manga_number, chapter_number, delimiter='\t'):
        i = 0
        raise NotImplementedError

    def add_site(self, site_name):
        sites = [x.lower() for x in MangaCrawlers.keys()]
        if site_name.lower() in sites:
            name, = [x for x in MangaCrawlers.keys() if site_name.lower() == x.lower()]
            self.manga_sites.append(MangaSite(name))
            return True, name
        return False, site_name

    def crawl_site(self, site_number):
        site = self.manga_sites[site_number]
        crawler = self.__get_crawler(site.site_name)
        crawler.crawl_index(site)
        return site

    def crawl_manga(self, site_number, manga_number):
        site = self.manga_sites[site_number]
        manga = self.manga_sites[site_number].mangas[manga_number]
        crawler = self.__get_crawler(site.site_name)
        crawler.crawl_detail(manga)
        manga.downloaded = True
        return manga

    def crawl_chapter(self, site_number, manga_number, chapter_number):
        site = self.manga_sites[site_number]
        chapter = self.manga_sites[site_number].mangas[manga_number].chapters[chapter_number]
        crawler = self.__get_crawler(site.site_name)
        crawler.download(chapter)
        chapter.downloaded = True
        return chapter

    def store_sites(self):
        try:
            if not isdir(self.save_location_sites):
                mkdir(self.save_location_sites)
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

    def load_sites(self):
        self.manga_sites = []
        if not isdir(self.save_location_sites):
            mkdir(self.save_location_sites)
            # fresh run
            return None
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
    manga_site_2_crawler('KissManga')
