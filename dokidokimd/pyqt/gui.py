import atexit
import random
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction, QMenu, QFileDialog

from dokidokimd.controller import DDMDController
from dokidokimd.pyqt.consts import QCOLOR_DARK, QCOLOR_HIGHLIGHT, QCOLOR_WHITE
from dokidokimd.pyqt.widgets import MangaSiteWidget
from dokidokimd.tools.ddmd_logger import get_logger
from dokidokimd.tools.misc import get_resource_path
from dokidokimd.tools.translator import translate as _

logger = get_logger(__name__)


class DDMDApplication(QApplication):
    def __init__(self, title, config, args):
        QApplication.__init__(self, args)
        self.setStyle('fusion')
        self.setWindowIcon(QIcon(get_resource_path('icons/favicon.png')))
        self._default_palette = self.palette()

        gui = GUI(self, title, config)
        gui.connect_action(self.set_dark_palette, self.set_default_palette)
        atexit.register(gui.before_exit)
        gui.redraw_palette(config.dark_mode)

    def set_dark_palette(self):
        p = self.palette()
        p.setColor(QPalette.Window, QCOLOR_DARK)
        p.setColor(QPalette.Button, QCOLOR_DARK)
        p.setColor(QPalette.Highlight, QCOLOR_HIGHLIGHT)
        p.setColor(QPalette.ButtonText, QCOLOR_WHITE)
        p.setColor(QPalette.PlaceholderText, QCOLOR_WHITE)
        p.setColor(QPalette.Background, QCOLOR_DARK)
        p.setColor(QPalette.Base, QCOLOR_DARK)
        p.setColor(QPalette.Text, QCOLOR_WHITE)
        p.setColor(QPalette.PlaceholderText, QCOLOR_WHITE)
        p.setColor(QPalette.Foreground, QCOLOR_WHITE)
        self.setPalette(p)

    def set_default_palette(self):
        self.setPalette(self._default_palette)


GUI_HINTS = [
    'You can right click to bring context menu.',
    'Some websites, like KissManga, index more than 10min!',
    'Search pattern is not regular expression!',
    'Search pattern is case insensitive.',
    'You can manually change number of thread in config file.',
]


class GUI(QMainWindow):
    def __init__(self, qt_app, title, config):
        QMainWindow.__init__(self)
        self.set_dark_palette = None
        self.set_default_palette = None

        self.qt_app = qt_app
        self.title = title
        self.config = config
        self.controller = DDMDController(self.config)
        self.setWindowTitle(self.title)
        self.main_widget = MangaSiteWidget(self.controller)
        self.main_widget.connect_actions(self.show_msg_on_status_bar, self.lock_gui, self.unlock_gui)
        self.setCentralWidget(self.main_widget)
        self.init_menu_bar()
        self.change_sot(self.config.sot)
        self.show()
        self.show_msg_on_status_bar(random.choice(GUI_HINTS))

    def connect_action(self, set_dark_palette, set_default_palette):
        self.set_dark_palette = set_dark_palette
        self.set_default_palette = set_default_palette

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(_('File'))
        options_menu = menu_bar.addMenu(_('Options'))
        manga_menu = QMenu(_('Manga DB'), self)
        file_menu.addMenu(manga_menu)

        save_act = QAction(_('Save '), self)
        save_act.triggered.connect(self.save_sites)
        manga_menu.addAction(save_act)

        imp_act = QAction(_('Import'), self)
        imp_act.triggered.connect(self.import_db)
        manga_menu.addAction(imp_act)

        relocate_act = QAction(_('Relocate'), self)
        relocate_act.triggered.connect(self.relocate_db)
        manga_menu.addAction(relocate_act)

        aot_menu = QAction(_('Stay on top'), self)
        aot_menu.setCheckable(True)
        aot_menu.triggered.connect(lambda: self.change_sot(aot_menu.isChecked()))
        options_menu.addAction(aot_menu)
        aot_menu.setChecked(self.config.sot)

        dark_mode = QAction(_('Dark mode'), self)
        dark_mode.setCheckable(True)
        dark_mode.triggered.connect(lambda: self.redraw_palette(dark_mode.isChecked()))
        options_menu.addAction(dark_mode)
        dark_mode.setChecked(self.config.dark_mode)

    def save_sites(self):
        self.controller.store_sites(),
        self.show_msg_on_status_bar(_(F'DB saved to {self.config.db_path}'))

    def relocate_db(self):
        path = str(QFileDialog.getExistingDirectory(self, _('Select Directory')))
        if path:
            self.config.db_path = path
            self.controller.store_sites()

    def import_db(self):
        path = str(QFileDialog.getExistingDirectory(self, _('Select Directory')))
        if path:
            self.config.db_path = path
            self.controller.load_db()
            self.main_widget = MangaSiteWidget(self.controller)
            self.main_widget.connect_actions(self.show_msg_on_status_bar, self.lock_gui, self.unlock_gui)
            self.setCentralWidget(self.main_widget)
            self.show_msg_on_status_bar(_(F'Loaded DB from {self.config.db_path}'))

    def redraw_palette(self, is_dark_mode):
        self.config.dark_mode = is_dark_mode
        if self.config.dark_mode:
            self.set_dark_palette()
        else:
            self.set_default_palette()

    def before_exit(self):
        self.controller.store_sites()
        self.config.write_config()

    def change_sot(self, is_checked):
        self.config.sot = is_checked
        flags = QtCore.Qt.WindowFlags()
        hint = QtCore.Qt.WindowStaysOnTopHint
        if is_checked:
            self.setWindowFlags(flags | hint)
        else:
            self.setWindowFlags(flags & ~hint)
        self.show()

    def lock_gui(self):
        self.setDisabled(True)

    def unlock_gui(self):
        self.setEnabled(True)

    def show_msg_on_status_bar(self, string: str = ''):
        self.statusBar().showMessage(string)

    def show_msg_window(self, title, msg):
        QMessageBox.question(self, title, msg, QMessageBox.Ok)


def start_gui(title, config):
    return_code = -1
    try:
        return_code = DDMDApplication(title, config, sys.argv).exec_()
    except Exception as e:
        logger.critical(_(F'Application failed due to an error: {e}'))
    finally:
        sys.exit(return_code)
