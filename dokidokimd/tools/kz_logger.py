import logging

from tools.translator import translate as _

PROJECT_NAME = "DokiDokiMD"
logging_level = logging.DEBUG


def init_logger() -> None:
    logger = logging.getLogger('{}'.format(PROJECT_NAME))
    logger.setLevel(logging_level)
    fh = logging.FileHandler('{}.log'.format(PROJECT_NAME))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(_('Program started'))


def get_logger(module_name) -> logging.Logger:
    return logging.getLogger('{}.{}'.format(PROJECT_NAME, module_name))