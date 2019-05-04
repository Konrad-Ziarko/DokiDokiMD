import os
import re
import sys

import urwid

from controller import DDMDController
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


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
        self.length = _('「Pages {}」').format(self.pages) if not self.downloaded else _('『Pages {}』').format(self.pages)
        self.caption = caption
        self.bullet = white_bullet if self.downloaded else bullet
        super(ColumnChapters, self).__init__(MenuButton(self.caption, self.clicked, self.bullet))
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [urwid.AttrMap(urwid.Text(['  ', self.caption]), 'heading'),
                 urwid.AttrMap(divider, 'line')]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        state = _('{}\nDownloaded - {}\nPDF - {}\n').format(self.length, self.downloaded, self.converted)

        response = urwid.AttrMap(urwid.Text([state, '\n', self.caption]), 'heading')
        done_button = MenuButton(_('Back'), self.go_back, self.bullet)
        download_button = MenuButton(_('Download Images'), self.download, self.bullet)
        save_button = MenuButton(_('Save Images'), self.save_images, self.bullet)
        convert_button = MenuButton(_('Make PDF'), self.make_pdf, self.bullet)
        remove_button = MenuButton(_('Remove Images'), self.remove_images, self.bullet)
        response_box = urwid.Filler(urwid.Pile([response,
                                                urwid.AttrMap(divider, 'line'),
                                                done_button,
                                                download_button,
                                                save_button,
                                                convert_button,
                                                remove_button]))
        self.root.chapter_number = self.row
        self.root.open_box(response_box)

    def go_back(self, button):
        self.root.set_focus(self.root.focus_position - 1)

    def download(self, button):
        self.root.window.download_content()

    def save_images(self, button):
        self.root.window.save_chapter_images()

    def make_pdf(self, button):
        self.root.window.convert_chapter_2_pdf()

    def remove_images(self, button):
        self.root.window.remove_images()


class ColumnMangas(urwid.WidgetWrap):
    def __init__(self, root, caption, row, choices=None):
        self.focus_skip = 2

        if choices is None:
            choices = list()
        self.choices = choices
        self.root = root
        self.row = row
        self.caption = _('{} 「{}」').format(caption, len(choices))
        super(ColumnMangas, self).__init__(MenuButton(self.caption, self.clicked, bullet))

        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker([urwid.AttrMap(urwid.Text(['\n ', self.caption]), 'heading'),
                                         urwid.AttrMap(divider, 'line')] +
                                        choices))  # choices start as 3rd widget => self.focus_skip = 2  # because 0, 1, 2
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.manga_number = self.row
        self.root.open_box(self.menu)


class ColumnSites(urwid.WidgetWrap):
    def __init__(self, root, caption, row, choices=None):
        self.focus_skip = 2

        if choices is None:
            choices = list()
        self.choices = choices
        self.root = root
        self.row = row
        self.caption = '{} 「{}」'.format(caption, len(choices))
        super(ColumnSites, self).__init__(MenuButton(self.caption, self.clicked, bullet))
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker([urwid.AttrMap(urwid.Text(['\n ', self.caption]), 'heading'),
                                         urwid.AttrMap(divider, 'line')] +
                                        choices))  # choices start as 3rd widget => self.focus_skip = 2  # because 0, 1, 2
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.site_number = self.row
        self.root.open_box(self.menu)


class MainWidget(urwid.WidgetWrap):
    def __init__(self, root, caption, choices=None):
        self.focus_skip = 2

        if choices is None:
            choices = list()
        self.choices = choices
        self.root = root
        super(MainWidget, self).__init__(MenuButton([caption], self.clicked, bullet))
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [urwid.AttrMap(urwid.Text(['\n ', caption]), 'heading'),
                 urwid.AttrMap(divider, 'line')] +
                choices))  # choices start as 3rd widget => self.focus_skip = 2  # because 0, 1, 2
        self.menu = urwid.AttrMap(listbox, 'options')

    def clicked(self, button):
        self.root.open_box(self.menu)


class RootWidget(urwid.Columns):
    def __init__(self, controller, window):
        self.window = window
        self.controller = controller
        self.site_number = -1
        self.manga_number = -1
        self.chapter_number = -1
        super(RootWidget, self).__init__([], dividechars=1)

    def open_box(self, box):
        if self.contents:
            del self.contents[self.focus_position + 1:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map), self.options('given', 25)))
        self.focus_position = len(self.contents) - 1

    def fresh_open(self, box):
        del self.contents[:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map), self.options('given', 25)))
        self.focus_position = 0


class Window:

    def change_footer(self, text):
        self.frame.footer = urwid.Text(text)
        self.ml.draw_screen()

    def change_header(self, text):
        self.frame.header = urwid.Text(text)
        self.ml.draw_screen()

    def handle_typing(self, keys):
        to_return = []
        if self.is_typing_jump:
            for key in keys:
                if key == 'enter' or key == 'g' or key == 'G':
                    self.is_typing = self.is_typing_jump = False
                    self.set_focus(int(self.jump_to))
                    self.jump_to = ''
                elif key.isdigit():
                    self.jump_to += key
                    self.change_footer(_('Jump to row: {}').format(self.jump_to))
                else:
                    to_return.append(key)
        else:
            for key in keys:
                if key == 'enter':
                    self.main_widget = self.sites_to_menu(self.regex_str)
                    self.root.fresh_open(self.main_widget.menu)
                    self.is_typing = False
                    self.change_footer(_('Applied filter /{}/').format(self.regex_str))
                    self.regex_str = ''
                elif key == 'backspace':
                    self.regex_str = self.regex_str[:-1]
                    self.change_footer(_('Searching for: {}').format(self.regex_str))
                elif key.isalnum() or key.isspace() or len(key) == 1:
                    self.regex_str = '{}{}'.format(self.regex_str, key)
                    self.change_footer(_('Searching for: {}').format(self.regex_str))
                elif len(key) > 1:
                    to_return.append(key)
                else:
                    to_return.append(key)
        return to_return

    def filter_if_typing(self, keys, raw):
        if self.is_typing:
            return self.handle_typing(keys)
        else:
            return keys

    def set_focus(self, focus_position):
        current_column = self.root.get_focus_column()
        success = False
        try:
            if current_column == 0:
                focus_skip = self.main_widget.focus_skip
                self.main_widget.menu.original_widget.set_focus(focus_skip + focus_position)
                success = True
            elif current_column == 1:  # Site
                x = self.main_widget.menu.base_widget.get_focus()[1]
                widget = self.main_widget.menu.base_widget.body[x].menu.base_widget

                focus_skip = self.main_widget.focus_skip
                for position in range(widget.body.__len__()):
                    if position >= focus_skip:
                        if '({})'.format(focus_position) in widget.body[position].caption:
                            widget.set_focus(position)
                            success = True
                            break
            elif current_column == 2:  # Manga
                x = self.main_widget.menu.base_widget.get_focus()[1]
                y = self.main_widget.menu.base_widget.body[x].menu.base_widget.get_focus()[1]
                widget = self.main_widget.menu.base_widget.body[x].menu.base_widget.body[y].menu.base_widget

                focus_skip = self.main_widget.focus_skip
                for position in range(widget.body.__len__()):
                    if position >= focus_skip:
                        if '({})'.format(focus_position) in widget.body[position].caption:
                            widget.set_focus(position)
                            success = True
                            break
            else:
                self.change_footer(_('Cannot jump here'))
                return
            if success:
                self.change_footer(_('Jumped to row: {}').format(focus_position))
            else:
                raise IndexError()
        except IndexError:
            self.change_footer(_("Wrong index value!"))

    def download_content(self):
        current_column = self.root.get_focus_column()
        module_logger.info(_('Downloading for column {}').format(current_column))
        if current_column == 0:
            self.change_footer(_("You can't download sites"))
        elif current_column == 1:  # Site
            self.change_footer(_('Indexing Site...'))
            # self.controller.crawl_site(site_number)
            # self.root.clear_content()
            try:
                module_logger.info(_('Downloading mangas for site {}').format(self.controller.manga_sites[self.root.site_number].site_name))
                self.controller.crawl_site(self.root.site_number)
                self.main_widget = self.sites_to_menu()
                self.root.fresh_open(self.main_widget.menu)
                self.change_footer(_('Indexed {} mangas').format(len(self.controller.manga_sites[self.root.site_number].mangas)))
            except Exception as e:
                self.change_footer(_('Error downloading mangas for site {}').format(self.controller.manga_sites[self.root.site_number].site_name))
                module_logger.error(_('Error downloading mangas for site {}. Exception message: {}').format(self.controller.manga_sites[self.root.site_number].site_name, e))
        elif current_column == 2:  # Manga
            self.change_footer(_('Indexing Manga...'))
            manga = self.controller.crawl_manga(self.root.site_number, self.root.manga_number)
            try:
                module_logger.info(_('Downloading chapters for manga {}').format(manga.title))
                no_of_chapters = len(manga.chapters)
                self.main_widget = self.sites_to_menu()
                self.root.fresh_open(self.main_widget.menu)
                self.change_footer(_('Indexed {} chapters for manga {}').format(no_of_chapters, manga.title))
            except Exception as e:
                self.change_footer(_('Error downloading chapters for manga {}').format(manga.title))
                module_logger.error(_('Error downloading chapters for manga {}. Exception message: {}').format(manga.title, e))
        elif current_column == 3:  # Chapter
            self.change_footer(_('Downloading images...'))
            chapter = self.controller.crawl_chapter(self.root.site_number, self.root.manga_number, self.root.chapter_number)
            try:
                module_logger.info(_('Downloading images for chapter {}').format(chapter.title))
                no_of_pages = len(chapter.pages)
                self.main_widget = self.sites_to_menu()
                self.root.fresh_open(self.main_widget.menu)
                self.change_footer(_('Downloaded {} images of {}').format(no_of_pages, chapter.title))
            except Exception as e:
                self.change_footer(_('Error downloading images for chapter {}').format(chapter.title))
                module_logger.error(_('Error downloading images for chapter {}. Exception message: {}').format(chapter.title, e))
        # Details?

    def save_chapter_images(self):
        current_column = self.root.get_focus_column()
        if current_column == 3:
            self.change_footer(_('Saving pages to {}').format(self.controller.save_location_sites))
            chapter = self.controller.manga_sites[self.root.site_number].mangas[self.root.manga_number].chapters[self.root.chapter_number]
            try:
                module_logger.info(_('Saving images for chapter {}').format(chapter.title))
                boolean, path = self.controller.save_images_from_chapter(chapter)
                if boolean:
                    # self.root.fresh_open(self.sites_to_menu().menu)
                    self.change_footer(_('Pages of {} saved to {}').format(chapter.title, path))
                else:
                    self.change_footer(_('Pages of {} could not be saved to {}').format(chapter.title, path))
            except Exception as e:
                self.change_footer(_('Error saving images for chapter {}').format(chapter.title))
                module_logger.error(_('Error saving images for chapter {}. Exception message: {}').format(chapter.title, e))
        else:
            self.change_footer(_('You have to be in a specific manga chapter'))

    def convert_chapter_2_pdf(self):
        current_column = self.root.get_focus_column()
        if current_column == 3:
            chapter = self.controller.manga_sites[self.root.site_number].mangas[self.root.manga_number].chapters[self.root.chapter_number]
            if not chapter.downloaded:
                self.change_footer(_('You have to download the chapter first (Shift + D)'))
            else:
                self.change_footer(_('Saving PDF to {}').format(self.controller.save_location_sites))
                try:
                    boolean, path = self.controller.convert_chapter_2_pdf(chapter)
                    if boolean:
                        # self.root.fresh_open(self.sites_to_menu().menu)
                        self.change_footer(_('PDF of {} saved to {}').format(chapter.title, path))
                    else:
                        self.change_footer(_('PDF of {} could not be saved to {}').format(chapter.title, path))
                except Exception as e:
                    self.change_footer(_('Error convering to pdf for chapter {}').format(chapter.title))
                    module_logger.error(_('Error convering to pdf for chapter {}. Exception message: {}').format(chapter.title, e))
        else:
            self.change_footer(_('You have to be in a specific manga chapter'))

    def remove_images(self):
        current_column = self.root.get_focus_column()
        if current_column == 3:
            chapter = self.controller.manga_sites[self.root.site_number].mangas[self.root.manga_number].chapters[self.root.chapter_number]
            if not chapter.downloaded:
                self.change_footer(_('You have to download the chapter first (Shift + D)'))
            else:
                self.change_footer(_('Removing images for {}').format(chapter.title))
                try:
                    boolean, path = self.controller.remove_images(chapter)
                    if boolean:
                        # self.root.fresh_open(self.sites_to_menu().menu)
                        self.change_footer(_('Removed images for {} from {}').format(chapter.title, path))
                    else:
                        self.change_footer(_('Images of {} could not be removed from {}').format(chapter.title, path))
                except Exception as e:
                    self.change_footer(_('Error removing images for chapter {}').format(chapter.title))
                    module_logger.error(_('Error emoving images for chapter {}. Exception message: {}').format(chapter.title, e))
        else:
            self.change_footer(_('You have to be in a specific manga chapter'))

    def handle_key(self, key):
        if not isinstance(key, tuple):
            if key in 'Q':
                exit_program(key)
            elif key in 'H':
                self.change_footer(self.help_text)
            elif key in 'S':  # Save data
                try:
                    self.controller.store_sites()
                    self.change_footer(_('Data saved!'))
                    module_logger.info(_('Data saved!'))
                except Exception as e:
                    self.change_footer(_('Error while saving DB'))
                    module_logger.error(_('Error while saving DB. Exception message: {}').format(e))
            elif key in 'C':  # Convert to PDF
                self.convert_chapter_2_pdf()
            elif key in 'W':  # Save images
                self.save_chapter_images()
            elif key in 'D':  # Download current column
                self.download_content()
            elif key in 'R':  # Download current column
                self.remove_images()
            elif key.isdigit():
                if not self.is_typing:
                    self.is_typing = True
                    self.is_typing_jump = True
                    self.jump_to = key
                    self.change_footer(_('Jump to row: {}').format(self.jump_to))
            elif key in '/':  # Start typing filter
                if not self.is_typing:
                    self.is_typing = True
                    self.change_footer(_('Searching for: {}').format(self.regex_str))

    def sites_to_menu(self, match_filter: str = None):
        pattern = re.compile(match_filter) if match_filter is not None else None
        sites = []
        for site in self.controller.manga_sites:
            mangas = []
            for manga in site.mangas:
                if match_filter is None or pattern.match(manga.title.lower()):
                    chapters = []
                    for chapter in manga.chapters:
                        pages = 0
                        if hasattr(chapter, 'pages') and chapter.pages:
                            pages = len(chapter.pages)
                        idx3 = manga.chapters.index(chapter)
                        chapters.append(ColumnChapters(self.root, '({})'.format(idx3) + chapter.title, manga.chapters.index(chapter), chapter.downloaded, chapter.converted, pages))
                    idx2 = site.mangas.index(manga)
                    mangas.append(ColumnMangas(self.root, '({})'.format(idx2) + manga.title, site.mangas.index(manga), chapters))
            # add to columnsites
            idx1 = self.controller.manga_sites.index(site)
            sites.append(ColumnSites(self.root, '({})'.format(idx1) + site.site_name, self.controller.manga_sites.index(site), mangas))
        to_return = MainWidget(self.root, _('Manga Sites ({})').format(len(self.controller.manga_sites)), sites)
        return to_return

    def __init__(self, controller: DDMDController):
        self.help_text = _('[S]aveDB  [D]ownload  [W]riteImages  [C]onvert2PDF  [R]emoveImages  [H]elp  [Q]uit')
        self.controller = controller  # type: DDMDController
        self.frame = None  # type: urwid.Frame
        self.footer = urwid.Text(self.help_text)  # type: urwid.Text
        self.header = urwid.Text(['WD>', self.controller.save_location_sites])  # type: urwid.Text

        self.is_typing = False  # type: bool
        self.is_typing_jump = False  # type: bool
        self.regex_str = ''  # type: str
        self.jump_to = ''  # type: str
        self.root = RootWidget(self.controller, self)

        self.main_widget = self.sites_to_menu()
        self.ml = None  # type: urwid.MainLoop

    def start(self):
        self.root.open_box(self.main_widget.menu)
        self.frame = urwid.Frame(self.root, footer=self.footer, header=self.header)
        self.ml = urwid.MainLoop(self.frame, palette, input_filter=self.filter_if_typing, unhandled_input=self.handle_key)
        self.ml.run()


def main():
    from sys import platform

    cmd = ''
    python = 'python'
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
        # import subprocess
        # proc = subprocess.Popen(args=["gnome-terminal", "--command={} {}".format(python, __file__)])


if __name__ == '__main__':
    main()
