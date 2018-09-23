import logging
import os
from enum import Enum
from dokidokimd.convert.make_pdf import PDF
from dokidokimd.core.manga_site import Manga, Chapter, AvailableSites, load_dumped_site
from dokidokimd.net.crawler.goodmanga import GoodMangaCrawler
from dokidokimd.net.crawler.kissmanga import KissMangaCrawler
from dokidokimd.net.crawler.mangapanda import MangaPandaCrawler
from sys import platform

if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin":
    pass
elif platform == "win32":
    pass

module_logger = logging.getLogger("ddmd.%s" % os.path.splitext((os.path.basename(__file__)))[0])

WORKING_DIR = os.getcwd()
SAVE_LOCATION_SITES = os.path.join(WORKING_DIR, 'sites')


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
        if not os.path.isdir(SAVE_LOCATION_SITES):
            os.mkdir(SAVE_LOCATION_SITES)

        for manga_site in self.manga_sites:
            data = manga_site.dump()

            path_to_file = os.path.join(SAVE_LOCATION_SITES, manga_site.site_name)
            path_to_old_file = path_to_file + '.old'

            if os.path.isfile(path_to_file):
                # check if old file exists and remove it
                if os.path.isfile(path_to_old_file):
                    os.remove(path_to_old_file)
                # rename current file
                os.rename(path_to_file, path_to_old_file)
                try:
                    # create new file
                    with open(path_to_file, 'wb') as the_file:
                        the_file.write(data)
                except Exception as e:
                    module_logger.critical("Could not save %s site to a file %s\nError message: %s" %
                                           (manga_site.site_name, path_to_file, str(e)))
                    pass
            else:
                with open(path_to_file, 'wb') as the_file:
                    the_file.write(data)

        return True

    def load_sites(self):
        self.manga_sites = []
        if not os.path.isdir(SAVE_LOCATION_SITES):
            os.mkdir(SAVE_LOCATION_SITES)
            # fresh run
            return None
        for file_name in os.listdir(SAVE_LOCATION_SITES):
            if not file_name.endswith('.old'):
                if os.path.isfile(os.path.join(SAVE_LOCATION_SITES, file_name)):
                    # try to load state
                    try:
                        with open(os.path.join(SAVE_LOCATION_SITES, file_name), 'rb') as the_file:
                            data = the_file.read()
                            manga_site = load_dumped_site(data)
                            self.manga_sites.append(manga_site)
                    except Exception as e1:
                        # could not load last state, trying older one
                        try:
                            with open(os.path.join(SAVE_LOCATION_SITES, file_name) + '.old', 'rb') as the_file:
                                data = the_file.read()
                                manga_site = load_dumped_site(data)
                                self.manga_sites.append(manga_site)
                        except Exception as e2:
                            pass


if __name__ == "__main__":
    pass
