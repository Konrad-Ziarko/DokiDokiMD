import logging

from dokidokimd.cli import main


def init():
    logger = logging.getLogger('ddmd')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('ddmd.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info('Program started\n')


if __name__ == '__main__':
    init()
    main.start()
