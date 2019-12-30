import os
import logging

PROJECT_NAME = "DokiDokiMD"


def init_logger(cwd) -> logging.Logger:
    logger = logging.getLogger(F'{PROJECT_NAME}')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.join(cwd, F'{PROJECT_NAME}.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def get_logger(module_name) -> logging.Logger:
    return logging.getLogger(F'{PROJECT_NAME}.{module_name}')


def set_logger_level(level) -> None:
    logger = logging.getLogger(F'{PROJECT_NAME}')
    logger.setLevel(level*10)
