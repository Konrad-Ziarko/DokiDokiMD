from os import getcwd, mkdir, remove, rename, listdir
from os.path import join, isdir, isfile
from sys import platform

from dokidokimd.convert.make_pdf import PDF
from dokidokimd.core.manga_site import load_dumped_site, MangaSite
from dokidokimd.logging.logger import get_logger
from dokidokimd.net.crawler.goodmanga import GoodMangaCrawler
from dokidokimd.net.crawler.kissmanga import KissMangaCrawler
from dokidokimd.net.crawler.mangapanda import MangaPandaCrawler

if platform == 'linux' or platform == 'linux2':
    pass
elif platform == 'darwin':
    pass
elif platform == 'win32':
    pass

module_logger = get_logger('controller')

WORKING_DIR = getcwd()
SAVE_LOCATION_SITES = join(WORKING_DIR, 'sites')

MangaCrawlers = {
    'GoodManga': GoodMangaCrawler,
    'MangaPanda': MangaPandaCrawler,
    'KissManga': KissMangaCrawler,
}


def manga_site_2_crawler(site_name):
    for name, crawler in MangaCrawlers.items():
        if name in site_name:
            return crawler


class DDMDController:

    def __init__(self):
        self.manga_sites = []
        self.pdf_converter = PDF()

    def add_site(self, site_name):
        sites = [x.lower() for x in MangaCrawlers.keys()]
        if site_name.lower() in sites:
            name = [x for x in MangaCrawlers.keys() if site_name.lower() == x.lower()]
            self.manga_sites.append(MangaSite(name))
            return True, name
        return False, site_name

    def list_sites(self):
        i = 0
        print('Current manga sites:')
        for site in self.manga_sites:
            print('\t[{}]:{} with {} mangas'.
                  format(i, site.site_name, len(site.mangas) if site.mangas is not None else 0))
            i = i + 1

    def list_mangas(self, site_number):
        i = 0
        mangas = self.manga_sites[site_number].mangas
        if mangas is None:
            mangas = list()
        print('Site {} contains {} mangas: {}'.
              format(self.manga_sites[site_number].site_name, len(mangas), mangas))

    def list_chapters(self, site_number, manga_number):
        i = 0
        chapters = self.manga_sites[site_number].mangas[manga_number].chapters
        if chapters is None:
            chapters = list()
        print('Site {}, manga {} contains {} chapters: {}'.
              format(self.manga_sites[site_number].site_name, self.manga_sites[site_number].mangas[manga_number].title,
                     len(chapters), self.manga_sites[site_number].mangas[manga_number].chapters))

    def list_pages(self, site_number, manga_number, chapter_number):
        i = 0
        pass # TODO

    def select_chapter(self, site_number, manga_number, chapter_number):
        pass

    def select_manga(self, site_number, manga_number):
        pass

    def select_site(self, site_number):
        pass

    def get_cwd(self, site_number, manga_number, chapter_number):
        cwd = ''
        if site_number >= 0:
            cwd = '{}'.format(self.manga_sites[site_number].site_name)
            if manga_number >= 0:
                cwd = '{}/{}'.format(cwd, self.manga_sites[site_number].mangas[manga_number].title)
                if chapter_number >= 0:
                    cwd = '{}/{}'.format(cwd, self.manga_sites[site_number].mangas[manga_number].chapters[
                        chapter_number].title)
        return cwd

    def store_sites(self):
        if not isdir(SAVE_LOCATION_SITES):
            mkdir(SAVE_LOCATION_SITES)

        for manga_site in self.manga_sites:
            data = manga_site.dump()

            path_to_file = join(SAVE_LOCATION_SITES, manga_site.site_name)
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
                    module_logger.critical('Could not save {} site to a file{}\nError message: {}'.
                                           format(manga_site.site_name, path_to_file, e))
                    pass
            else:
                with open(path_to_file, 'wb') as the_file:
                    the_file.write(data)

        return True

    def load_sites(self):
        self.manga_sites = []
        if not isdir(SAVE_LOCATION_SITES):
            mkdir(SAVE_LOCATION_SITES)
            # fresh run
            return None
        for file_name in listdir(SAVE_LOCATION_SITES):
            if not file_name.endswith('.old'):
                if isfile(join(SAVE_LOCATION_SITES, file_name)):
                    # try to load state
                    try:
                        with open(join(SAVE_LOCATION_SITES, file_name), 'rb') as the_file:
                            data = the_file.read()
                            manga_site = load_dumped_site(data)
                            self.manga_sites.append(manga_site)
                    except Exception as e1:
                        # could not load last state, trying older one
                        try:
                            with open('{}.old'.format(join(SAVE_LOCATION_SITES, file_name)), 'rb') as the_file:
                                data = the_file.read()
                                manga_site = load_dumped_site(data)
                                self.manga_sites.append(manga_site)
                        except Exception as e2:
                            pass


if __name__ == '__main__':
    manga_site_2_crawler('KissManga')
