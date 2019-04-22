import logging

from dokidokimd.tools.translator import translate as _

logging_level = logging.DEBUG


class Singleton(type):
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    _instances = {}


class KzLogger(metaclass=Singleton):
    def __init__(self) -> None:
        self.name = 'ddmd'
        logger = logging.getLogger('{}'.format(self.name))
        logger.setLevel(logging_level)
        fh = logging.FileHandler('{}.log'.format(self.name))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info(_('Program started'))

    def get_logger(self, module_name) -> logging.Logger:
        return logging.getLogger('{}.{}'.format(self.name, module_name))

