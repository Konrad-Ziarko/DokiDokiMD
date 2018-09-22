import argparse


def list_cmd(args):
    parser = argparse.ArgumentParser(description='Lists choosen object.')
    parser.add_argument('site', nargs='?', type=str, help='Name of manga site(used in regex).')
    parser.add_argument('manga', nargs='?', type=str, help='Name of manga(used in regex).')
    parser.add_argument('chapter', nargs='?', type=int, help='Chapter number(integer).')

    if '-h' in args or '--help' in args:
        parser.print_help()
    else:
        parsed, unknown = parser.parse_known_args(args)
        print(vars(parsed))


def show_help():
    print('※ DokiDokiMangaDownloader©®℠™℗ 2018 † ‡ KZiarko ※')
    print('')
    print('Available commands:')


EXIT_COMMAND = ['e', 'exit', 'q', 'quit']
HELP_COMMAND = ['h', 'help', '']

COMMANDS = {
    'l': list_cmd, 'list': list_cmd

}


def main_loop():
    running = True
    while running:
        try:
            input_line = input('DDMD/>')
        except KeyboardInterrupt as e:
            # save progress ?
            print('Going to sleep ;_;')
            break
        if input_line in EXIT_COMMAND:
            running = False
        elif input_line in HELP_COMMAND:
            show_help()
        else:
            parts = input_line.split()
            if len(parts) == 1:
                try:
                    COMMANDS[parts[0]]()
                except TypeError as e:
                    print('This command requires more arguments!')
            elif len(parts) >= 2:
                COMMANDS[parts[0]](parts[1:])


        # detect command
        # execute command

    # post exit stuff
    pass


def start():
    main_loop()


if __name__ == "__main__":
    start()

