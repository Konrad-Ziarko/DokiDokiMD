import configparser

from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


class ConfigManager(object):
    def __init__(self):
        self.config_path = 'ddmd.ini'
        self.config = configparser.ConfigParser()

        self._sot = False               # type: bool
        self._dark_mode = False         # type: bool
        self._db_path = ''              # type: str
        self._max_threads = 10          # type: int
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
        self.write_config()

    @property
    def dark_mode(self):
        return self._dark_mode

    @dark_mode.setter
    def dark_mode(self, dark_mode: bool):
        self.config.set('Window', 'dark_mode', str(dark_mode))
        self._dark_mode = dark_mode
        self.write_config()

    @property
    def db_path(self):
        return self._db_path

    @db_path.setter
    def db_path(self, db_path: str):
        self.config.set('Manga', 'db_path', db_path)
        self._db_path = db_path
        self.write_config()

    @property
    def max_threads(self):
        return self._max_threads

    @max_threads.setter
    def max_threads(self, max_threads: int):
        self.config.set('Manga', 'max_threads', str(max_threads))
        self._max_threads = max_threads
        self.write_config()

    def read_config(self):
        try:
            self.sot = self.config.getboolean('Window', 'stay_on_top')
        except (configparser.NoOptionError, ValueError):
            self.sot = False
        try:
            self.dark_mode = self.config.getboolean('Window', 'dark_mode')
        except (configparser.NoOptionError, ValueError):
            self.dark_mode = False
        try:
            self.db_path = self.config.get('Manga', 'db_path')
        except (configparser.NoOptionError, ValueError):
            self.db_path = ''
        try:
            self.max_threads = self.config.getint('Manga', 'max_threads')
        except (configparser.NoOptionError, ValueError):
            self.max_threads = 10

    def write_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
