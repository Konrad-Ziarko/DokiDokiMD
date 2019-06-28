import configparser

from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


class ConfigManager(object):
    def __init__(self):
        self.config_path = 'ddmd.ini'
        self.config = configparser.ConfigParser()

        self._sot = None                # type: bool
        self._dark_mode = None          # type: bool
        self._db_path = ''              # type: str
        try:
            self.config.read(self.config_path)
            if not self.config.has_section('Window'):
                self.config.add_section('Window')
            if not self.config.has_section('Manga'):
                self.config.add_section('Manga')
        except Exception as e:
            logger.error(_('Could not open config file due to: {}').format(e))

    @property
    def sot(self): return self._sot

    @sot.setter
    def sot(self, sot: bool):
        self.config.set('Window', 'stay_on_top', str(sot))
        self._sot = sot

    @property
    def dark_mode(self):
        return self._dark_mode

    @dark_mode.setter
    def dark_mode(self, dark_mode: bool):
        self.config.set('Window', 'dark_mode', str(dark_mode))
        self._dark_mode = dark_mode

    @property
    def db_path(self):
        return self._db_path

    @db_path.setter
    def db_path(self, db_path: str):
        self.config.set('Manga', 'db_path', db_path)
        self._db_path = db_path

    def read_config(self):
        try:
            self.sot = self.config.getboolean('Window', 'stay_on_top')
        except configparser.NoOptionError:
            self.sot = False
        try:
            self.dark_mode = self.config.getboolean('Window', 'dark_mode')
        except configparser.NoOptionError:
            self.dark_mode = False
        try:
            self.db_path = self.config.get('Manga', 'db_path')
        except configparser.NoOptionError:
            self.db_path = ''

    def write_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
