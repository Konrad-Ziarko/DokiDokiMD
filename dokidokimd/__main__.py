from dokidokimd.cli import cli
from dokidokimd.logging.logger import init_logging

if __name__ == '__main__':
    init_logging()
    cli.start()
