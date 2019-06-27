import configparser

from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


class ConfigManager(object):
    def __init__(self):
        self.config_path = 'ddmd.ini'
        self.config = configparser.ConfigParser()
        self.sot = None
        self.dark_mode = None
        try:
            self.config.read(self.config_path)
            if self.config.has_section('Window'):
                pass
            else:
                self.config.add_section('Window')
        except Exception as e:
            logger.error(_('Could not open config file due to: {}').format(e))

    def read_config(self):
        try:
            self.sot = self.config.getboolean('Window', 'stay_on_top')
        except:
            self.config.set('Window', 'stay_on_top', 'false')
            self.sot = False
        try:
            self.dark_mode = self.config.getboolean('Window', 'dark_mode')
        except:
            self.config.set('Window', 'dark_mode', 'true')
            self.dark_mode = False

    def set_sot(self, boolean):
        self.config.set('Window', 'stay_on_top', str(boolean))

    def set_dark_mode(self, boolean):
        self.config.set('Window', 'dark_mode', str(boolean))

    def write_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
