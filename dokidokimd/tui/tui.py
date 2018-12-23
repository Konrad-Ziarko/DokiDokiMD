import sys
from os import getcwd
import os
import urwid

from dokidokimd.core.controller import DDMDController

WORKING_DIR = getcwd()


def exit_program(key):
    raise urwid.ExitMainLoop()


focus_map = {
    'heading': 'focus heading',
    'options': 'focus options',
    'line': 'focus line'}

palette = [
    (None, 'light gray', 'black'),
    ('heading', 'black', 'light gray'),
    ('line', 'black', 'light gray'),
    ('options', 'dark gray', 'black'),
    ('focus heading', 'white', 'dark red'),
    ('focus line', 'black', 'dark red'),
    ('focus options', 'black', 'light gray'),
    ('selected', 'white', 'dark blue')]

divider = urwid.Divider(u'\N{LOWER ONE QUARTER BLOCK}')


class MenuButton(urwid.Button):
    def __init__(self, caption, callback):
        super(MenuButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrMap(urwid.SelectableIcon([u'  \N{BULLET} ', caption], 2), None, 'selected')


class ColumnChapters(urwid.WidgetWrap):
    def __init__(self, root, caption, row, choices=None):
        self.root = root
        self.row = row
        super(ColumnChapters, self).__init__(MenuButton(['{} ({})'.format(caption, len(choices)), u"\N{HORIZONTAL ELLIPSIS}"], self.clicked))
        if choices is None:
            choices = list()
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [urwid.AttrMap(urwid.Text([u"\n  ", '{} ({})'.format(caption, len(choices))]), 'heading'), urwid.AttrMap(divider, 'line'), urwid.Divider()] + choices + [
                    urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.chapter_number = self.row
        self.root.open_box(self.menu)


class ColumnMangas(urwid.WidgetWrap):
    def __init__(self, root, caption, row, choices=None):
        self.root = root
        self.row = row
        super(ColumnMangas, self).__init__(MenuButton(['{} ({})'.format(caption, len(choices)), u"\N{HORIZONTAL ELLIPSIS}"], self.clicked))
        if choices is None:
            choices = list()
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [urwid.AttrMap(urwid.Text([u"\n  ", '{} ({})'.format(caption, len(choices))]), 'heading'), urwid.AttrMap(divider, 'line'), urwid.Divider()] + choices + [
                    urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.manga_number = self.row
        self.root.open_box(self.menu)


class ColumnSites(urwid.WidgetWrap):
    def __init__(self, root, caption, row, choices=None):
        self.root = root
        self.row = row
        super(ColumnSites, self).__init__(MenuButton(['{} ({})'.format(caption, len(choices)), u"\N{HORIZONTAL ELLIPSIS}"], self.clicked))
        if choices is None:
            choices = list()
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [urwid.AttrMap(urwid.Text([u"\n  ", '{} ({})'.format(caption, len(choices))]), 'heading'), urwid.AttrMap(divider, 'line'), urwid.Divider()] + choices + [
                    urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.site_number = self.row
        self.root.open_box(self.menu)


class MainWidget(urwid.WidgetWrap):
    def __init__(self, root, caption, choices=None):
        self.root = root
        super(MainWidget, self).__init__(MenuButton([caption, u"\N{HORIZONTAL ELLIPSIS}"], self.clicked))
        if choices is None:
            choices = list()
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker([urwid.AttrMap(urwid.Text([u"\n  ", caption]), 'heading'), urwid.AttrMap(divider, 'line'), urwid.Divider()] + choices + [urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.open_box(self.menu)


class RootWidget(urwid.Columns):
    def __init__(self, controller):
        self.controller = controller
        self.site_number = -1
        self.manga_number = -1
        self.chapter_number = -1
        super(RootWidget, self).__init__([], dividechars=1)

    def open_box(self, box):
        if self.contents:
            del self.contents[self.focus_position + 1:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map), self.options('given', 24)))
        self.focus_position = len(self.contents) - 1

    def fresh_open(self, box):
        del self.contents[:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map), self.options('given', 24)))
        self.focus_position = 0


class Window:

    def change_footer(self, text):
        self.frame.footer = urwid.Text(text)

    def handle_key(self, key):
        if key in ('q', 'Q'):
            exit_program(key)
        if key in ('s', 'S'):
            try:
                self.controller.store_sites()
                self.change_footer("Data saved!")
            except Exception as e:
                self.change_footer("{}".format(e))
        if key in ('d', 'D'):

            col = self.root.get_focus_column()
            if col == 0:
                self.change_footer("You can't download sites")
            elif col == 1:  # Site
                # self.controller.crawl_site(site_number)
                # self.root.clear_content()
                try:
                    self.controller.crawl_site(self.root.site_number)
                    self.root.fresh_open(self.sites_to_menu().menu)
                    self.change_footer("Indexed {} mangas".format(len(self.controller.manga_sites[self.root.site_number].mangas)))
                except Exception as e:
                    self.change_footer("{}".format(e))
            elif col == 2:  # Manga
                try:
                    self.controller.crawl_manga(self.root.site_number, self.root.manga_number)
                    name = self.controller.manga_sites[self.root.site_number].mangas[self.root.manga_number].title
                    self.root.fresh_open(self.sites_to_menu().menu)
                    self.change_footer("Indexed {} chapters for manga {}".format(len(self.controller.manga_sites[self.root.site_number].mangas), name))
                except Exception as e:
                    self.change_footer("{}".format(e))
            else:
                pass  # Details?

            pass

    def sites_to_menu(self):
        sites = []
        for site in self.controller.manga_sites:
            mangas = []
            for manga in site.mangas:
                chapters = []
                for chapter in manga.chapters:
                    #TODO for each page ?
                    chapters.append(ColumnChapters(self.root, chapter.title, manga.chapters.index(chapter), []))
                mangas.append(ColumnMangas(self.root, manga.title, site.mangas.index(manga), chapters))
            # add to columnsites
            sites.append(ColumnSites(self.root, site.site_name, self.controller.manga_sites.index(site), mangas))
        to_return = MainWidget(self.root, "Manga Sites ({})".format(len(self.controller.manga_sites)), sites)
        return to_return

    def __init__(self, controller):
        self.controller = controller
        self.frame = None
        self.footer = urwid.Text('DokiDokiMD  |  [D]ownload  [S]ave')
        # self.header = urwid.Text('DokiDokiMD  |  [D]ownload  [S]ave')

        # for site in self.controller.manga_sites:
        # self.manga_sites.add_choices(MangaSiteWidget(self.controller, u'{}'.format(site.site_name), []))
        self.root = RootWidget(self.controller)

        self.manga_data = self.sites_to_menu()

    def start(self):

        self.root.open_box(self.manga_data.menu)
        self.frame = urwid.Frame(self.root, footer=self.footer)
        urwid.MainLoop(self.frame, palette, unhandled_input=self.handle_key).run()


if __name__ == '__main__':
    from sys import platform, executable, stdin

    cmd = ''
    python = 'python3.7'
    if platform == 'linux' or platform == 'linux2':
        cmd = 'gnome-terminal --  {python} {path}'
    elif platform == 'darwin':
        raise Exception('OSX not supported')
    elif platform == 'win32':
        cmd = 'start cmd /K {python} {path}'

    if sys.__stdin__.isatty():  # stdin.isatty():
        w = Window(DDMDController())
        w.start()
    else:
        # program started without command line interface
        # start itself in appropriate terminal
        os.system(cmd.format(python=python, path=__file__))
