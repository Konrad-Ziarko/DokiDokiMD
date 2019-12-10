import atexit
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction, QMenu, QFileDialog

from consts import QCOLOR_DARK, QCOLOR_HIGHLIGHT, QCOLOR_WHITE
from controller import DDMDController
from pyqt.widgets import MangaSiteWidget
from tools.config import ConfigManager
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


class GUI(QMainWindow):
    def __init__(self, qt_app, title):
        super(GUI, self).__init__()
        self.qt_app = qt_app
        self.original_palette = self.qt_app.palette()
        self.config = ConfigManager()
        self.config.read_config()
        self.controller = DDMDController(self.config)
        self.title = title
        self.setWindowTitle(self.title)
        self.main_widget = MangaSiteWidget(self, self.controller)
        self.setCentralWidget(self.main_widget)
        self.styleSheet()
        self.init_menu_bar()
        self.change_sot(self.config.sot)
        self.set_dark_style(self.config.dark_mode)
        self.keep_status_msg = 0
        self.show()

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(_('File'))
        options_menu = menu_bar.addMenu(_('Options'))
        manga_menu = QMenu(_('Manga DB'), self)
        file_menu.addMenu(manga_menu)

        save_act = QAction(_('Save '), self)
        save_act.triggered.connect(
            lambda: (
                self.controller.store_sites(),
                self.show_msg_on_status_bar(_(F'DB saved to {self.config.db_path}'))
            )
        )
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
        dark_mode.triggered.connect(lambda: self.set_dark_style(dark_mode.isChecked()))
        options_menu.addAction(dark_mode)
        dark_mode.setChecked(self.config.dark_mode)

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
            self.main_widget = MangaSiteWidget(self, self.controller)
            self.setCentralWidget(self.main_widget)
            self.show_msg_on_status_bar(_(F'Loaded DB from {self.config.db_path}'))

    def set_dark_style(self, is_checked):
        self.config.dark_mode = is_checked
        if is_checked:
            p = self.qt_app.palette()
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
            self.qt_app.setPalette(p)
        else:
            self.qt_app.setPalette(self.original_palette)

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

    def show_msg_on_status_bar(self, string: str = ''):
        self.statusBar().showMessage(string)

    def clear_status_bar(self):
        self.statusBar().clearMessage()

    def show_msg_window(self, title, msg):
        QMessageBox.question(self, title, msg, QMessageBox.Ok)


def start_gui(title):
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('fusion')
    qt_app.setWindowIcon(QIcon('../icons/favicon.png'))
    gui = GUI(qt_app, title)
    gui.show_msg_on_status_bar("Some websites, like KissManga, index more than 10min!")
    atexit.register(gui.before_exit)
    sys.exit(qt_app.exec_())
