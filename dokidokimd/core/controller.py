from enum import Enum
from os import getcwd, mkdir, remove, rename, listdir
from os.path import basename, join, isdir, isfile
from sys import platform

from dokidokimd.convert.make_pdf import PDF
from dokidokimd.core.manga_site import load_dumped_site
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

module_logger = get_logger((basename(__file__))[0])

WORKING_DIR = getcwd()
SAVE_LOCATION_SITES = join(WORKING_DIR, 'sites')


class MangaCrawlers(Enum):
    GoodManga = GoodMangaCrawler
    MangaPanda = MangaPandaCrawler
    KissManga = KissMangaCrawler


def manga_site_2_crawler(site_name):
    for crawler in MangaCrawlers:
        if crawler.name in site_name:
            return crawler.value()


class DDMDController:

    def __init__(self):
        self.manga_sites = []
        self.pdf_converter = PDF()

        # show ui
        pass

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
    pass
