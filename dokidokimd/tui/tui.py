import sys
from os import getcwd
import os

WORKING_DIR = getcwd()





if __name__ == '__main__':
    from sys import platform, executable, stdin
    cmd = ''
    python = 'python'  # 'python3'
    if platform == 'linux' or platform == 'linux2':
        cmd = 'gnome-terminal -e "{python} {path}"'
    elif platform == 'darwin':
        raise Exception('OSX not yet supported')
    elif platform == 'win32':
        cmd = 'start cmd /K {python} {path}'

    if sys.__stdin__.isatty():  # stdin.isatty():
        print('hello')
        print(executable)
        input()
    else:
        # program started without command line interface
        # start itself in appropriate terminal
        print('ehlo')
        os.system(cmd.format(python=python, path=__file__))


