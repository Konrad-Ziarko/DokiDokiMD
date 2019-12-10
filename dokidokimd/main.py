import os

from pyqt.gui import start_gui
from tools.config import ConfigManager
from tools.ddmd_logger import init_logger, PROJECT_NAME
from tools.misc import get_resource_path

if __name__ == '__main__':
    start_cwd = get_resource_path(os.getcwd())
    logger = init_logger(start_cwd)
    try:
        config = ConfigManager(start_cwd)
        start_gui(PROJECT_NAME, config, start_cwd)
    except Exception as e:
        logger.critical(F'Application failed due to : {e}')
