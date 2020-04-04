import os
from typing import List

from dokidokimd.models import MangaSite
from dokidokimd.tools.ddmd_logger import get_logger
from dokidokimd.tools.translator import translate as _

logger = get_logger(__name__)


class MangaStorage(object):
    def __init__(self):
        self.site_extension = 'ddmd'  # type: str

    def store_sites(self, sites_location, sites_to_store) -> bool:
        try:
            if not os.path.isdir(sites_location):
                os.makedirs(sites_location, exist_ok=True)
        except Exception as e:
            logger.critical(_(F'Could not make or access directory {sites_location}\nError message: {e}'))
            return False

        for manga_site in sites_to_store:
            data = manga_site.dump()
            path_to_file = os.path.join(sites_location, F'{manga_site.site_name}.{self.site_extension}')

            try:
                # create new file
                with open(path_to_file, 'wb') as the_file:
                    the_file.write(data)
            except Exception as e:
                logger.critical(
                    _(F'Could not save {manga_site.site_name} site to a file{path_to_file}\nError message: {e}'))
        return True

    def load_sites(self, sites_location) -> List[MangaSite]:
        restored_manga_sites = []
        if not os.path.isdir(sites_location):
            os.makedirs(sites_location, exist_ok=True)
            logger.info(_('No saved state. Creating dir for fresh DB'))
        for file_name in os.listdir(sites_location):
            if file_name.endswith(self.site_extension):
                if os.path.isfile(os.path.join(sites_location, file_name)):
                    logger.info(_(F'Loading last state for {file_name}'))
                    try:
                        with open(os.path.join(sites_location, file_name), 'rb') as the_file:
                            data = the_file.read()
                            manga_site = MangaSite.load_dumped_site(data)
                            restored_manga_sites.append(manga_site)
                    except Exception as e1:
                        logger.warning(_(F'Could not load last state. Error message: {e1}'))
        return restored_manga_sites
