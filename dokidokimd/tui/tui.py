import sys
from os import getcwd
import os
import urwid

WORKING_DIR = getcwd()


def exit_program(key):
    raise urwid.ExitMainLoop()


focus_map = {
            'heading': 'focus heading',
            'options': 'focus options',
            'line': 'focus line'}


class MenuButton(urwid.Button):
    def __init__(self, caption, callback):
        super(MenuButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrMap(urwid.SelectableIcon([u'  \N{BULLET} ', caption], 2), None, 'selected')


class HorizontalBoxes(urwid.Columns):
    def __init__(self):
        super(HorizontalBoxes, self).__init__([], dividechars=1)

    def open_box(self, box):
        if self.contents:
            del self.contents[self.focus_position + 1:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map), self.options('given', 24)))
        self.focus_position = len(self.contents) - 1

    def close_box(self):
        if self.contents:
            del self.contents[self.focus_position:]
            self.focus_position = len(self.contents) - 1

    def fresh_content(self, box):
        del self.contents[:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map), self.options('given', 24)))
        self.focus_position = len(self.contents) - 1


class SubMenu(urwid.WidgetWrap):
    line = urwid.Divider(u'\N{LOWER ONE QUARTER BLOCK}')

    def __init__(self, caption, choices):
        self.caption = caption
        self.choices = choices
        super(SubMenu, self).__init__(MenuButton([caption, u"\N{HORIZONTAL ELLIPSIS}"], self.open_menu))
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    urwid.AttrMap(urwid.Text([u"\n  ", self.caption]), 'heading'),
                    urwid.AttrMap(self.line, 'line'),
                    urwid.Divider()] + self.choices + [urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def add_choices(self, items):
        if isinstance(items, (list,)):
            for item in items:
                self.__add_choice(item)
        else:
            self.__add_choice(items)

    def __add_choice(self, item):
        self.choices.append(item)
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    urwid.AttrMap(urwid.Text([u"\n  ", self.caption]), 'heading'),
                    urwid.AttrMap(self.line, 'line'),
                    urwid.Divider()] + self.choices + [urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def open_menu(self, button):
        Window.horizontal_boxes.open_box(self.menu)


class Choice(urwid.WidgetWrap):
    def __init__(self, caption):
        super(Choice, self).__init__(MenuButton(caption, self.item_chosen))
        self.caption = caption

    def item_chosen(self, button, ):
        response = urwid.Text([u'  You chose ', self.caption, u'\n'])
        done = MenuButton(u'Ok', exit_program)
        response_box = urwid.Filler(urwid.Pile([response, done]))
        Window.horizontal_boxes.open_box(urwid.AttrMap(response_box, 'options'))


class Window:
    horizontal_boxes = None

    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            #exit_program(key)
            menu_top = SubMenu(u'Manga Sites', [
                SubMenu(u'KissManga', [
                    SubMenu(u'Accessories', [
                        Choice(u'Text Editor'),
                        Choice(u'Terminal'),
                    ]),
                ]),
                SubMenu(u'MangaPanda', [
                    SubMenu(u'Preferences', [
                        Choice(u'Appearance'),
                    ]),
                    Choice(u'Lock Screen'),
                ]),
            ])
            Window.horizontal_boxes.fresh_content(menu_top.menu)

    def __init__(self):
        self.frame = None

        self.manga_sites = {'KissManga': SubMenu(u'KissManga', []),
                            'MangaPanda': SubMenu(u'MangaPanda', []),
                            'GoodManga': SubMenu(u'GoodManga', []),
                            }
        # here mangas should be loaded
        self.menu_top = SubMenu(u'Manga Sites', [])
        for k, v in self.manga_sites.items():
            self.menu_top.add_choices(v)

        self.palette = [
            (None, 'light gray', 'black'),
            ('heading', 'black', 'light gray'),
            ('line', 'black', 'light gray'),
            ('options', 'dark gray', 'black'),
            ('focus heading', 'white', 'dark red'),
            ('focus line', 'black', 'dark red'),
            ('focus options', 'black', 'light gray'),
            ('selected', 'white', 'dark blue')]

        self.manga_sites['KissManga'].add_choices([Choice(u'Lock Screen'), Choice(u'Appearance')])

    def start(self):
        Window.horizontal_boxes = HorizontalBoxes()
        Window.horizontal_boxes.open_box(self.menu_top.menu)
        frame = urwid.Filler(Window.horizontal_boxes, 'middle', 10)
        urwid.MainLoop(frame, self.palette, unhandled_input=self.exit_on_q).run()


if __name__ == '__main__':
    from sys import platform, executable, stdin
    cmd = ''
    python = 'python'  # 'python3'
    if platform == 'linux' or platform == 'linux2':
        cmd = 'gnome-terminal -e "{python} {path}"'
    elif platform == 'darwin':
        raise Exception('OSX not supported')
    elif platform == 'win32':
        cmd = 'start cmd /K {python} {path}'

    if sys.__stdin__.isatty():  # stdin.isatty():
        w = Window()
        w.start()
    else:
        # program started without command line interface
        # start itself in appropriate terminal
        os.system(cmd.format(python=python, path=__file__))


