from pyqt.gui import start_gui
from tools.kz_logger import init_logger, PROJECT_NAME
from tools.config import ConfigManager

config = ConfigManager()
config.read_config()
init_logger(config.log_level)
start_gui(PROJECT_NAME)
