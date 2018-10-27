import os
import tkinter as tk

import pygubu


class Application:
    def __init__(self, master):

        # 1: Create a builder
        self.builder = builder = pygubu.Builder()

        # 2: Load an ui file
        builder.add_from_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'window.ui'))

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
