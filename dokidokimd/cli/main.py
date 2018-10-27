import argparse
import os


class CommandLineInterface:
    def __init__(self):
        self.STORE_FILES_PATH = os.path.dirname(os.getcwd())
        self.EXIT_COMMAND = ['e', 'exit', 'q', 'quit']
        self.HELP_COMMAND = ['h', 'help', '']

        self.COMMANDS = {
            'list': self.list_cmd,
            'set': self.set_variable,
            'get': self.get_variable,
        }

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

    def show_help(self):
        print('※ DokiDokiMangaDownloader©®℠™℗ 2018 † ‡ KZiarko ※')
        print('')
        print('Available commands:')
        print([cmd for cmd in [self.EXIT_COMMAND, self.HELP_COMMAND]])
        print('\n')
        print([cmd for cmd in self.COMMANDS.keys()])

    def main_loop(self):
        running = True
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
                    except TypeError as e:
                        print('This command requires more arguments!')
                elif len(parts) >= 2:
                    self.COMMANDS[parts[0]](parts[1:])

        # exit stuff
        pass


def start():
    cli = CommandLineInterface()
    cli.main_loop()


if __name__ == '__main__':
    start()

