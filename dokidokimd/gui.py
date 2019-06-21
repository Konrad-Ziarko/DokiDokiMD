import atexit
import configparser
import sys

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QColor, QPaintEvent, QPainter, QCursor, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow, QHBoxLayout, \
    QComboBox, QListWidget, QMessageBox, QAction, QMenu, QListWidgetItem, QLineEdit, QLabel

from controller import DDMDController
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)


class ConfigManager(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.sot = None
        self.dark_mode = None
        try:
            self.config.read('conf.ini')
            if self.config.has_section('Window'):
                pass
            else:
                self.config.add_section('Window')
        except Exception as e:
            logger.error(_('Could not open config file due to: {}').format(e))

    def read_config(self):
        try:
            self.sot = self.config.getboolean('Window', 'Stay on top')
        except:
            self.config.set('Window', 'Stay on top', 'false')
            self.sot = False
        try:
            self.dark_mode = self.config.getboolean('Window', 'Dark mode')
        except:
            self.config.set('Window', 'Dark mode', 'true')
            self.dark_mode = False

    def set_sot(self, boolean):
        self.config.set('Window', 'Stay on top', str(boolean))

    def set_dark_mode(self, boolean):
        self.config.set('Window', 'Dark mode', str(boolean))

    def write_config(self):
        with open('conf.ini', 'w') as configfile:
            self.config.write(configfile)


class ListWidget(QListWidget):
    def __init__(self, default_string=_('No Items')):
        super(ListWidget, self).__init__()
        self.default_string = default_string

    def paintEvent(self, e: QPaintEvent) -> None:
        QListWidget.paintEvent(self, e)
        if self.model() and self.model().rowCount(self.rootIndex()) > 0:
            return
        p = QPainter(self.viewport())
        p.drawText(self.rect(), Qt.AlignCenter, self.default_string)


class MangaSiteWidget(QWidget):
    def __init__(self, parent, controller):
        super(QWidget, self).__init__(parent)
        self.ddmd = controller
        self.filter_text = ''

        hbox = QHBoxLayout(self)
        vbox_left = QVBoxLayout(self)
        hbox.addLayout(vbox_left)
        vbox_right = QVBoxLayout(self)
        search_hbox = QHBoxLayout()
        self.combo_box_sites = QComboBox()
        self.mangas_list = ListWidget(_('No mangas'))
        self.chapters_list = ListWidget(_('No chapters'))
        self.filter_mangas = QLineEdit()
        hbox.addLayout(vbox_right)

        self.combo_box_sites.currentIndexChanged.connect(
            lambda: self.site_selected(self.combo_box_sites.currentIndex())
        )
        for idx, site in enumerate(self.ddmd.get_sites()):
            self.combo_box_sites.addItem('{}:{}({})'.format(idx, site.site_name, len(site.mangas)), site)
        self.combo_box_sites.setMaximumWidth(self.combo_box_sites.sizeHint().width())
        vbox_left.addLayout(search_hbox)
        search_hbox.addWidget(self.combo_box_sites)

        # get mangas for site from combobox
        btn_crawl_site = QPushButton(parent=self)
        btn_crawl_site.setMaximumSize(btn_crawl_site.sizeHint())
        btn_crawl_site.clicked.connect(
            lambda: self.update_mangas()
        )
        btn_crawl_site.setIcon(QIcon('../icons/baseline_search_black_18dpx2.png'))
        search_hbox.addWidget(btn_crawl_site)
        search_hbox.setAlignment(QtCore.Qt.AlignLeft)

        # list widget for mangas
        self.mangas_list.doubleClicked.connect(
            lambda: self.manga_double_clicked(self.mangas_list.currentRow())
        )
        self.mangas_list.clicked.connect(
            lambda: self.manga_selected(self.mangas_list.currentRow())
        )
        vbox_left.addWidget(self.mangas_list)

        self.filter_mangas.setToolTip(_('Filter'))
        self.filter_mangas.setPlaceholderText(_('Search manga...'))
        self.filter_mangas.textChanged.connect(lambda: self.apply_filter(self.filter_mangas.text()))
        vbox_left.addWidget(self.filter_mangas)

        ##
        # self.chapters_list.doubleClicked.connect(
        #     lambda: self.chapters_list.selectedItems()
        # )
        self.chapters_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        hbox.addWidget(self.chapters_list)
        self.chapters_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.chapters_list.customContextMenuRequested.connect(self.list_item_right_clicked)
        self.setLayout(hbox)

    def list_item_right_clicked(self, QPos):
        list_menu = QtWidgets.QMenu()
        menu_item_remove = list_menu.addAction(_('Remove Item'))
        list_menu.addSeparator()
        # menu_item_remove.triggered.connect(self._configure)
        menu_item_download = list_menu.addAction(_('Download'))
        menu_item_make_pdf = list_menu.addAction(_('Make PDF'))

        list_menu.exec_(QCursor.pos())

    def manga_double_clicked(self, manga_index):
        manga = self.mangas_list.item(manga_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_manga(manga)
        self.update_chapters()
        self.mangas_list.item(manga_index).setForeground(QColor(23, 150, 200, 250))

    def manga_selected(self, manga_index):
        manga = self.mangas_list.item(manga_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_manga(manga)
        self.load_stored_chapters()

    def site_selected(self, site_index):
        site = self.combo_box_sites.itemData(site_index, QtCore.Qt.UserRole)
        self.ddmd.set_cwd_site(site)
        self.load_stored_mangas()
        self.chapters_list.clear()

    def load_stored_chapters(self, manga=None):
        if not manga:
            manga = self.ddmd.get_current_manga()
        self.chapters_list.clear()
        for chapter in manga.chapters:
            item = QListWidgetItem(chapter.title)
            if chapter.downloaded:
                item.setForeground(QColor(23, 150, 200, 250))
            if chapter.converted:
                item.setForeground(QColor(11, 120, 10, 250))
            item.setToolTip(chapter.title)
            self.chapters_list.addItem(item)
        self.chapters_list.setMinimumWidth(self.chapters_list.sizeHint().width())

    def load_stored_mangas(self, site=None):
        if not site:
            site = self.ddmd.get_current_site()
        self.mangas_list.clear()
        for manga in site.mangas:
            if self.filter_text.lower() in manga.title.lower():
                item = QListWidgetItem(manga.title)
                if manga.downloaded:
                    item.setForeground(QColor(23, 150, 200, 250))
                item.setToolTip(manga.title)
                item.setData(QtCore.Qt.UserRole, manga)
                self.mangas_list.addItem(item)
        self.mangas_list.setMinimumWidth(self.mangas_list.sizeHint().width())
        self.mangas_list.setMaximumWidth(self.mangas_list.sizeHintForColumn(0))

    def update_chapters(self):
        try:
            self.parent().setDisabled(True)
            manga = self.ddmd.crawl_manga()
            self.load_stored_chapters(manga)
        except Exception as e:
            logger.warning(_('Could not refresh chapters, reason: {}').format(e))
        finally:
            self.parent().setEnabled(True)

    def update_mangas(self):
        try:
            self.parent().setDisabled(True)
            site = self.ddmd.crawl_site()
            self.load_stored_mangas(site)
        except Exception as e:
            logger.warning(_('Could not refresh site, reason: {}').format(e))
            self.parent().show_msg_on_status_bar(_('Could not refresh site, for more info look into log file.'))
        finally:
            self.parent().setEnabled(True)

    def apply_filter(self, text):
        self.filter_text = text
        self.load_stored_mangas()


class GUI(QMainWindow):
    def __init__(self, qt_app, title):
        super(QMainWindow, self).__init__()
        self.qt_app = qt_app
        self.original_palette = self.qt_app.palette()
        self.controller = DDMDController()
        self.config = ConfigManager()
        self.config.read_config()
        self.title = title
        self.setWindowTitle(self.title)
        self.main_widget = MangaSiteWidget(self, self.controller)
        self.setCentralWidget(self.main_widget)
        self.styleSheet()
        self.init_menu_bar()
        self.change_sot(self.config.sot)
        self.set_dark_style(self.config.dark_mode)
        self.show()

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(_('File'))
        options_menu = menu_bar.addMenu(_('Options'))
        imp_menu = QMenu('Import', self)
        # imp_menu.triggered.connect(lambda: print('asd'))
        imp_act = QAction('Import sub', self)
        imp_act.triggered.connect(lambda: print('test'))
        imp_menu.addAction(imp_act)
        new_act = QAction('New', self)
        new_act.triggered.connect(lambda: print('test'))
        file_menu.addAction(new_act)
        file_menu.addMenu(imp_menu)

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

    def set_dark_style(self, is_checked):
        self.config.set_dark_mode(is_checked)
        if is_checked:
            p = self.qt_app.palette()
            p.setColor(QPalette.Window, QColor(53, 53, 53))
            p.setColor(QPalette.Button, QColor(63, 63, 63))
            p.setColor(QPalette.Highlight, QColor(142, 45, 197))
            p.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            p.setColor(QPalette.PlaceholderText, QColor(255, 255, 255))
            p.setColor(QPalette.Background, QColor(33, 33, 33))
            p.setColor(QPalette.Base, QColor(33, 33, 33))
            p.setColor(QPalette.Text, QColor(255, 255, 255))
            p.setColor(QPalette.PlaceholderText, QColor(255, 255, 255))
            self.qt_app.setPalette(p)
        else:
            self.qt_app.setPalette(self.original_palette)

    def before_exit(self):
        self.controller.store_sites()
        self.config.write_config()

    def change_sot(self, is_checked):
        self.config.set_sot(is_checked)
        flags = QtCore.Qt.WindowFlags()
        hint = QtCore.Qt.WindowStaysOnTopHint
        if is_checked:
            self.setWindowFlags(flags | hint)
        else:
            self.setWindowFlags(flags & ~hint)
        self.show()

    def show_msg_on_status_bar(self, string: str = ''):
        self.statusBar().showMessage(string)

    def show_msg_window(self, title, msg):
        QMessageBox.question(self, title, msg, QMessageBox.Ok)


def start_gui(title):
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('fusion')
    gui = GUI(qt_app, title)
    atexit.register(gui.before_exit)
    sys.exit(qt_app.exec_())
