import os

from dokidokimd.pyqt.gui import start_gui
from dokidokimd.tools.config import ConfigManager
from dokidokimd.tools.ddmd_logger import init_logger, PROJECT_NAME
from dokidokimd.tools.misc import get_resource_path

if __name__ == '__main__':
    start_cwd = os.getcwd()
    exe_path = get_resource_path(os.getcwd())
    logger = init_logger(start_cwd)
    try:
        config = ConfigManager(start_cwd)
        start_gui(PROJECT_NAME, config, exe_path, start_cwd)
    except Exception as e:
        logger.critical(F'Application failed due to : {e}')