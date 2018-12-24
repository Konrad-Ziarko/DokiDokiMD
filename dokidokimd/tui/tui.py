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

divider = urwid.Divider('\N{Lower One Quarter Block}')
white_bullet = '\N{White Bullet}'
bullet = '\N{Bullet}'
normal_brackets = '\N{Left Corner Bracket}{}\N{Right Corner Bracket}'
empty_brackets = '\N{Left White Corner Bracket}{}\N{Right White Corner Bracket}'


class MenuButton(urwid.Button):
    def __init__(self, caption, callback, bullet_point):
        super(MenuButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrMap(urwid.SelectableIcon([bullet_point, caption], 0), None, 'selected')


class ColumnChapters(urwid.WidgetWrap):
    def __init__(self, root, caption, row, downloaded, converted, pages=0):
        self.pages = str(pages)
        self.root = root
        self.row = row
        self.downloaded = downloaded
        self.converted = converted
        self.length = '「Pages {}」'.format(self.pages) if not self.downloaded else '『Pages {}』'.format(self.pages)
        self.caption = caption
        self.bullet = white_bullet if self.downloaded else bullet
        super(ColumnChapters, self).__init__(MenuButton(self.caption, self.clicked, self.bullet))
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [urwid.AttrMap(urwid.Text(['  ', self.caption]), 'heading'), urwid.AttrMap(divider, 'line')]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        state = '{}\nDownloaded - {}\nPDF - {}\n'.format(self.length, self.downloaded, self.converted)

        response = urwid.AttrMap(urwid.Text([state, '\n', self.caption]), 'heading')
        done_button = MenuButton('Back', self.go_back, self.bullet)
        convert_button = MenuButton('Make PDF', self.go_back, self.bullet)  # TODO make pdf
        response_box = urwid.Filler(urwid.Pile([response, done_button, convert_button]))
        self.root.chapter_number = self.row
        self.root.open_box(response_box)

    def go_back(self, button):
        self.root.set_focus(self.root.focus_position-1)


class ColumnMangas(urwid.WidgetWrap):
    def __init__(self, root, caption, row, choices=None):
        if choices is None:
            choices = list()
        self.choices = choices
        self.root = root
        self.row = row
        self.caption = '{} 「{}」'.format(caption, len(choices))
        super(ColumnMangas, self).__init__(MenuButton(self.caption, self.clicked, bullet))

        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [urwid.AttrMap(urwid.Text(['\n', self.caption]), 'heading'), urwid.AttrMap(divider, 'line')] + choices))
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.manga_number = self.row
        self.root.open_box(self.menu)


class ColumnSites(urwid.WidgetWrap):
    def __init__(self, root, caption, row, choices=None):
        if choices is None:
            choices = list()
        self.choices = choices
        self.root = root
        self.row = row
        self.caption = '{} 「{}」'.format(caption, len(choices))
        super(ColumnSites, self).__init__(MenuButton(self.caption, self.clicked, bullet))
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [urwid.AttrMap(urwid.Text(['\n', self.caption]), 'heading'), urwid.AttrMap(divider, 'line')] + choices))
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.site_number = self.row
        self.root.open_box(self.menu)


class MainWidget(urwid.WidgetWrap):
    def __init__(self, root, caption, choices=None):
        if choices is None:
            choices = list()
        self.choices = choices
        self.root = root
        super(MainWidget, self).__init__(MenuButton([caption], self.clicked, bullet))
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker([urwid.AttrMap(urwid.Text(['\n', caption]), 'heading'), urwid.AttrMap(divider, 'line')] + choices + [urwid.Divider()]))
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
        self.ml.draw_screen()

    def handle_typing(self, keys):
        to_return = []
        for key in keys:
            if key == 'enter':
                pass  # TODO apply filter
            elif len(key) > 1:
                to_return.append(key)
            elif key == 'backspace':
                self.regex_str = self.regex_str[:-1]
                self.change_footer('Searching for: {}'.format(self.regex_str))
            elif key.isalnum() or key.isspace():
                self.regex_str = '{}{}'.format(self.regex_str, key)
                self.change_footer('Searching for: {}'.format(self.regex_str))
            else:
                to_return.append(key)
        return to_return

    def filter_if_typing(self, keys, raw):
        if self.is_typing:
            return self.handle_typing(keys)
        else:
            return keys

    def handle_key(self, key):
        if not isinstance(key, tuple):
            if key in 'Q':
                exit_program(key)
            elif key in 'S':  # Save data
                try:
                    self.controller.store_sites()
                    self.change_footer("Data saved!")
                except Exception as e:
                    self.change_footer("{}".format(e))
            elif key in 'D':  # Download current column
                col = self.root.get_focus_column()
                if col == 0:
                    self.change_footer("You can't download sites")
                elif col == 1:  # Site
                    self.change_footer("Indexing Site...")
                    # self.controller.crawl_site(site_number)
                    # self.root.clear_content()
                    try:
                        self.controller.crawl_site(self.root.site_number)
                        self.root.fresh_open(self.sites_to_menu().menu)
                        self.change_footer("Indexed {} mangas".format(len(self.controller.manga_sites[self.root.site_number].mangas)))
                    except Exception as e:
                        self.change_footer("{}".format(e))
                elif col == 2:  # Manga
                    self.change_footer("Indexing Manga...")
                    urwid
                    try:
                        self.controller.crawl_manga(self.root.site_number, self.root.manga_number)
                        manga = self.controller.manga_sites[self.root.site_number].mangas[self.root.manga_number]
                        name = manga.title
                        no_of_chapters = len(manga.chapters)
                        self.root.fresh_open(self.sites_to_menu().menu)
                        self.change_footer("Indexed {} chapters for manga {}".format(no_of_chapters, name))
                    except Exception as e:
                        self.change_footer("{}".format(e))
                elif col == 3:  # Chapter
                    self.change_footer("Downloading images...")
                    try:
                        self.controller.crawl_chapter(self.root.site_number, self.root.manga_number, self.root.chapter_number)
                        chapter = self.controller.manga_sites[self.root.site_number].mangas[self.root.manga_number].chapters[self.root.chapter_number]
                        name = chapter.title
                        no_of_pages = len(chapter.pages)
                        self.root.fresh_open(self.sites_to_menu().menu)
                        self.change_footer("Downloaded {} images of {}".format(no_of_pages, name))
                    except Exception as e:
                        self.change_footer("{}".format(e))
                    pass
                pass  # Details?

            elif key in '/':  # Start typing filter
                if not self.is_typing:
                    self.is_typing = True
                    self.change_footer('Searching for: {}'.format(self.regex_str))

    def sites_to_menu(self):
        sites = []
        for site in self.controller.manga_sites:
            mangas = []
            for manga in site.mangas:
                chapters = []
                for chapter in manga.chapters:
                    pages = 0
                    if hasattr(chapter, 'pages') and chapter.pages:
                        pages = len(chapter.pages)
                    chapters.append(ColumnChapters(self.root, chapter.title, manga.chapters.index(chapter), chapter.downloaded, chapter.converted, pages))
                mangas.append(ColumnMangas(self.root, manga.title, site.mangas.index(manga), chapters))
            # add to columnsites
            sites.append(ColumnSites(self.root, site.site_name, self.controller.manga_sites.index(site), mangas))
        to_return = MainWidget(self.root, "Manga Sites ({})".format(len(self.controller.manga_sites)), sites)
        return to_return

    def __init__(self, controller):
        self.controller = controller
        self.frame = None
        self.footer = urwid.Text('DokiDokiMD  |  [D]ownload  [S]ave  [Q]uit')
        self.header = urwid.Text(['WD>', self.controller.save_location_sites])

        self.is_typing = False
        self.regex_str = ''
        # for site in self.controller.manga_sites:
        # self.manga_sites.add_choices(MangaSiteWidget(self.controller, '{}'.format(site.site_name), []))
        self.root = RootWidget(self.controller)

        self.manga_data = self.sites_to_menu()
        self.ml = None

    def start(self):
        self.root.open_box(self.manga_data.menu)
        self.frame = urwid.Frame(self.root, footer=self.footer, header=self.header)
        self.ml = urwid.MainLoop(self.frame, palette, input_filter=self.filter_if_typing, unhandled_input=self.handle_key)
        self.ml.run()


if __name__ == '__main__':
    from sys import platform

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
