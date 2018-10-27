import logging
from os.path import splitext


def init_logging():
    logger = logging.getLogger('ddmd')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('ddmd.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info('Program started\n')


def get_logger(module_name):
    return logging.getLogger('ddmd.{}'.format(splitext(module_name)))
