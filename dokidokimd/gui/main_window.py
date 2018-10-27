import tkinter as tk
from os.path import realpath, dirname, join

import pygubu

from dokidokimd.logging.logger import get_logger

module_logger = get_logger('main_window')


class Application:
    def __init__(self, master):
        # 1: Create a builder
        self.builder = builder = pygubu.Builder()

        # 2: Load an ui file
        builder.add_from_file(join(dirname(realpath(__file__)), 'window.ui'))

        # 3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('main_frame', master)

        # + Configure layout of the master. Set master resizable:
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        # -


def start():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()


if __name__ == '__main__':
    start()
