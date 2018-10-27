import argparse
import os
from os.path import basename

from dokidokimd.logging.logger import get_logger

module_logger = get_logger((basename(__file__))[0])


class CommandLineInterface:
    def __init__(self):
        self.STORE_FILES_PATH = os.path.dirname(os.getcwd())
        self.EXIT_COMMAND = ['e', 'exit', 'q', 'quit']
        self.HELP_COMMAND = ['h', 'help']
        self.LIST_COMMAND = ['l', 'list']
        self.GET_COMMAND = ['g', 'get']
        self.SET_COMMAND = ['s', 'set']
        self.COMMANDS = {}

        for item in self.LIST_COMMAND:
            self.COMMANDS[item] = self.list_cmd
        for item in self.GET_COMMAND:
            self.COMMANDS[item] = self.get_variable
        for item in self.SET_COMMAND:
            self.COMMANDS[item] = self.set_variable

        self.manga_sites = None
        pass

    def load_cmd(self, args):
        parser = argparse.ArgumentParser(description='Lists chosen object.')
        parser.add_argument('all', nargs='?', type=str, help='List all manga sites.')
        parser.add_argument('--site', nargs='?', type=str, help='Name of manga site(used in regex).')
        parser.add_argument('--manga', nargs='?', type=str, help='Name of manga(used in regex).')
        parser.add_argument('--chapter', nargs='?', type=int, help='Chapter number(integer).')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)

    def list_cmd(self, args):
        parser = argparse.ArgumentParser(description='Lists chosen object.')
        parser.add_argument('all', nargs='?', type=str, help='List all manga sites.')
        parser.add_argument('--site', nargs='?', type=str, help='Name of manga site(used in regex).')
        parser.add_argument('--manga', nargs='?', type=str, help='Name of manga(used in regex).')
        parser.add_argument('--chapter', nargs='?', type=int, help='Chapter number(integer).')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)
            if parsed.all is not None:
                print('Avaliable manga sites: {}'.format(self.manga_sites))
            else:
                if parsed.site is not None:
                    print(parsed.site)
                if parsed.manga is not None:
                    print(parsed.manga)
                if parsed.chapter is not None:
                    print(parsed.chapter)

    def set_variable(self, args):
        parser = argparse.ArgumentParser(description='Set variable value.')
        parser.add_argument('--path', nargs='?', type=str, help='Set path for downloaded files to be stored in.')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)
            if parsed.path is not None:
                if os.path.isdir(os.path.normpath(parsed.path)):
                    self.STORE_FILES_PATH = os.path.normpath(parsed.path)
                    print('Path for storage set to: {}\n'.format(self.STORE_FILES_PATH))
                else:
                    print('Cannot set path to this location ({}).\n'.format(os.path.normpath(parsed.path)))

    def get_variable(self, args):
        parser = argparse.ArgumentParser(description='Get variable value.')
        parser.add_argument('path', nargs='?', type=str, help='Get path for downloaded files.')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)
            if parsed.path is not None:
                print('Path for storage set to: {}\n'.format(self.STORE_FILES_PATH))

    def show_help(self, command=None):
        if command is None:
            print('Available commands:')
            print([cmd for cmd in [self.EXIT_COMMAND, self.HELP_COMMAND]])
            print('')
            print([cmd for cmd in self.COMMANDS.keys()])
        else:
            if command in self.COMMANDS.keys():
                if command in self.LIST_COMMAND:
                    self.list_cmd('-h')
                elif command in self.GET_COMMAND:
                    self.get_variable('-h')
                elif command in self.SET_COMMAND:
                    self.set_variable('-h')

    def main_loop(self):
        running = True
        print('※ DokiDokiMangaDownloader©®℠™℗ 2018 † ‡ KZiarko ※')
        print('')
        print('Current location for storing mangas is: \n\t\t{}\\\n'.format(self.STORE_FILES_PATH))

        manga_sites = []

        while running:
            try:
                input_line = input('DDMD/>')
            except KeyboardInterrupt as e:
                # save progress ?
                print('Going to sleep ;_;')
                break
            if input_line in self.EXIT_COMMAND:
                running = False
            elif input_line in self.HELP_COMMAND:
                self.show_help()
            else:
                parts = input_line.split()
                if len(parts) == 1:
                    try:
                        self.COMMANDS[parts[0]]()
                    except TypeError:
                        print('This command requires more arguments!')
                    except KeyError:
                        print('"{}" is not a command'.format(parts[0]))
                        self.show_help()
                elif len(parts) >= 2:
                    try:
                        if parts[0] in self.HELP_COMMAND:
                            self.show_help(parts[1])
                        else:
                            self.COMMANDS[parts[0]](parts[1:])
                    except KeyError:
                        print('Command {} does not accept {} arguments'.format(parts[0], parts[1:]))

        # exit stuff
        pass


def start():
    cli = CommandLineInterface()
    cli.main_loop()


if __name__ == '__main__':
    start()
