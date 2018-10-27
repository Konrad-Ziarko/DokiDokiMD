import argparse
from os import getcwd
from os.path import dirname, isdir, normpath

from dokidokimd.core.controller import DDMDController
from dokidokimd.core.manga_site import AvailableSites
from dokidokimd.logging.logger import get_logger

module_logger = get_logger('cli')


def list_supported_sites():
    print('Supported sites: {}'.
          format(['{}:{}'.format(name, value) for name, value in AvailableSites.items()]))


class CommandLineInterface:
    def __init__(self, controller):
        self.no_site = -1
        self.no_manga = -1
        self.no_chapter = -1
        self.cwd = ''

        self.STORE_FILES_PATH = dirname(getcwd())
        self.EXIT_COMMAND = ['e', 'exit', 'q', 'quit']
        self.HELP_COMMAND = ['h', 'help']

        self.LIST_COMMAND = ['l', 'ls', 'list']
        self.GET_COMMAND = ['g', 'get']
        self.SET_COMMAND = ['s', 'set']
        self.ADD_SITE_COMMEND = ['a', 'add']
        self.CHANGE_COMMAND = ['cd']

        self.COMMANDS = {}
        for item in self.LIST_COMMAND:
            self.COMMANDS[item] = self.list_cmd
        for item in self.GET_COMMAND:
            self.COMMANDS[item] = self.get_variable
        for item in self.SET_COMMAND:
            self.COMMANDS[item] = self.set_variable
        for item in self.ADD_SITE_COMMEND:
            self.COMMANDS[item] = self.add_empty_site
        for item in self.CHANGE_COMMAND:
            self.COMMANDS[item] = self.change_directory

        self.controller = controller

    def add_empty_site(self, args):
        parser = argparse.ArgumentParser(prog='add', description='Add new object.')
        parser.add_argument('name', nargs=1, type=str, help='name of an object.')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)
            if parsed.name is not None:
                name = parsed.name[0]
                boolean, ret_name = self.controller.add_site(name)
                if boolean:
                    sites = [x.site_name for x in self.controller.manga_sites]
                    print('[{}]{} added to current sites list'.
                          format([i for i, x in enumerate(sites) if x == ret_name][0], ret_name))
                else:
                    print('Could not add "{}" to current sites'.format(name))
                    list_supported_sites()

    def load_cmd(self, args):
        parser = argparse.ArgumentParser(prog='load', description='Lists chosen object.')
        parser.add_argument('all', nargs='?', type=str, help='List all manga sites.')
        parser.add_argument('--site', nargs='?', type=str, help='Name of manga site(used in regex).')
        parser.add_argument('--manga', nargs='?', type=str, help='Name of manga(used in regex).')
        parser.add_argument('--chapter', nargs='?', type=int, help='Chapter number(integer).')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)

    def list_cmd(self, args=''):
        parser = argparse.ArgumentParser(prog='ls', description='Lists chosen object.')
        parser.add_argument('l', nargs='?', type=str, help='Print output in single column.')
        parser.add_argument('a', nargs='?', type=str, help='Print detailed output.')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)
            delimiter = '\t'
            details = False
            if parsed.l is not None:
                delimiter = '\n'
            if parsed.a is not None:
                details = True

            if self.no_site >= 0:
                if self.no_manga >= 0:
                    if self.no_chapter >= 0:
                        self.controller.list_pages(self.no_site, self.no_manga, self.no_chapter)
                    else:
                        self.controller.list_chapters(self.no_site, self.no_manga)
                else:
                    self.controller.list_mangas(self.no_site)
            else:
                list_supported_sites()
                self.controller.list_sites()

    def set_variable(self, args):
        parser = argparse.ArgumentParser(prog='set', description='Set variable value.')
        parser.add_argument('--path', nargs='?', type=str, help='Set path for downloaded files to be stored in.')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)
            if parsed.path is not None:
                if isdir(normpath(parsed.path)):
                    self.STORE_FILES_PATH = normpath(parsed.path)
                    print('Path for storage set to: {}\n'.format(self.STORE_FILES_PATH))
                else:
                    print('Cannot set path to this location ({}).\n'.format(normpath(parsed.path)))

    def get_variable(self, args):
        parser = argparse.ArgumentParser(prog='get', description='Get variable value.')
        parser.add_argument('path', nargs='?', type=str, help='Get path for downloaded files.')

        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)
            if parsed.path is not None: # TODO
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
                elif command in self.CHANGE_COMMAND:
                    self.change_directory('-h')

    def main_loop(self):
        running = True
        print('※ DokiDokiMangaDownloader©®℠™℗ 2018 † ‡ KZiarko ※')
        print('')
        print('Current location for storing mangas is: \n\t\t{}\\\n'.format(self.STORE_FILES_PATH))

        while running:
            try:
                input_line = input('DDMD/{}>'.format(self.cwd))
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
                if parts[0] in self.COMMANDS:
                    try:
                        if parts[0] in self.HELP_COMMAND:
                            self.show_help(parts[1])
                        else:
                            self.COMMANDS[parts[0]](parts[1:])
                    except KeyError:
                        print('Command {} does not accept {} arguments'.format(parts[0], parts[1:]))
                else:
                    print('"{}" is not a command'.format(parts[0]))
                    self.show_help()

        # exit stuff
        pass

    def change_directory(self, args):
        parser = argparse.ArgumentParser(prog='cd', description='Change location.')
        parser.add_argument('path', nargs='?', type=str, help='location to navigate to.')
        if '-h' in args or '--help' in args:
            parser.print_help()
        else:
            parsed, unknown = parser.parse_known_args(args)
            if parsed.path is not None:
                if parsed.path == '.':
                    pass
                elif parsed.path == '..':
                    if self.cwd == '/':
                        pass
                    else:
                        if self.no_site >= 0:
                            if self.no_manga >= 0:
                                if self.no_chapter >= 0:
                                    self.no_chapter = -1
                                else:
                                    self.no_manga = -1
                            else:
                                self.no_site = -1
                else:
                    if parsed.path.isdigit():
                        if self.no_site >= 0:
                            if self.no_manga >= 0:
                                if self.no_chapter >= 0:
                                    pass  # TODO cant change dir, already at bottom
                                else:
                                    self.controller.select_chapter(self.no_site, self.no_manga, int(parsed.path))
                            else:
                                self.controller.select_manga(self.no_site, int(parsed.path))
                        else:
                            self.controller.select_site(int(parsed.path))
                    else:
                        pass  # passed name instead of digit
                self.set_new_cwd()
            else:
                print(self.cwd)

    def set_new_cwd(self):
        self.cwd = self.controller.get_cwd(self.no_site, self.no_manga, self.no_chapter)


def start():
    controller = DDMDController()
    cli = CommandLineInterface(controller)
    cli.main_loop()


if __name__ == '__main__':
    start()
