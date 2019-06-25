import atexit
import configparser
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QColor, QPaintEvent, QPainter, QCursor, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow, QHBoxLayout, \
    QComboBox, QListWidget, QMessageBox, QAction, QMenu, QListWidgetItem, QLineEdit

from controller import DDMDController
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger(__name__)

QCOLOR_DOWNLOADED = QColor(23, 150, 200, 250)
QCOLOR_CONVERTERR = QColor(11, 120, 10, 250)
QCOLOR_HIGHLIGHT = QColor(142, 45, 197, 255)
QCOLOR_WHITE = QColor(255, 255, 255, 220)
QCOLOR_DARK = QColor(33, 33, 33, 220)

CONFIG_FILE = 'ddmd.ini'


class ConfigManager(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.sot = None
        self.dark_mode = None
        try:
            self.config.read(CONFIG_FILE)
            if self.config.has_section('Window'):
                pass
            else:
                self.config.add_section('Window')
        except Exception as e:
            logger.error(_('Could not open config file due to: {}').format(e))

    def read_config(self):
        try:
            self.sot = self.config.getboolean('Window', 'stay_on_top')
        except:
            self.config.set('Window', 'stay_on_top', 'false')
            self.sot = False
        try:
            self.dark_mode = self.config.getboolean('Window', 'dark_mode')
        except:
            self.config.set('Window', 'dark_mode', 'true')
            self.dark_mode = False

    def set_sot(self, boolean):
        self.config.set('Window', 'stay_on_top', str(boolean))

    def set_dark_mode(self, boolean):
        self.config.set('Window', 'dark_mode', str(boolean))

    def write_config(self):
        with open(CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)


class SingleChapterDownloadThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, chapter):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.chapter = chapter

    def run(self):
        self.ddmd.crawl_chapter(self.chapter)
        self.ddmd.save_images_from_chapter(self.chapter)
        self.signal.emit("Downloaded {}".format(self.chapter.title))


class DownloadThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, callable_fun, chapters):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.chapters = chapters
        self.callable_fun = callable_fun
        self.threads = list()

    def set_name(self, string):
        self.name = string

    def run(self):
        for chapter in self.chapters:
            t = SingleChapterDownloadThread(self.ddmd, chapter)
            t.signal.connect(self.callable_fun)
            self.threads.append(t)
            t.start()

        while any(t.isRunning() for t in self.threads):
            pass
        self.signal.emit(self.name)


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
        super(MangaSiteWidget, self).__init__(parent)
        self.ddmd = controller
        self.filter_text = ''
        self.download_threads = dict()

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
        self.chapters_list.doubleClicked.connect(
            lambda: self.chapter_double_clicked(self.chapters_list.currentRow())
        )
        self.chapters_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        hbox.addWidget(self.chapters_list)
        self.chapters_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.chapters_list.customContextMenuRequested.connect(self.chapter_list_item_right_clicked)
        self.setLayout(hbox)

    def repaint_chapters(self):
        indexes = [idx.row() for idx in self.chapters_list.selectedIndexes()]
        self.load_stored_chapters(self.ddmd.get_current_manga())
        for i in indexes:
            self.chapters_list.item(i).setSelected(True)

    def single_download_finished(self, string):
        self.parent().show_msg_on_status_bar(string)
        self.repaint_chapters()

    def download_finished(self, name):
        self.download_threads.pop(name)
        self.parent().show_msg_on_status_bar(_("Download finished"))
        self.repaint_chapters()

    def chapter_list_item_right_clicked(self, QPos):
        list_menu = QtWidgets.QMenu()
        clear_action = QAction(_('Clear item'), self)
        clear_action.triggered.connect(self.chapter_clear_clicked)
        menu_item_clear = list_menu.addAction(clear_action)

        list_menu.addSeparator()

        download_action = QAction(_('Download'), self)
        download_action.triggered.connect(self.chapter_download_clicked)
        menu_item_download = list_menu.addAction(download_action)

        convert_action = QAction(_('Save as PDF'), self)
        convert_action.triggered.connect(self.chapter_convert_clicked)
        menu_item_make_pdf = list_menu.addAction(convert_action)

        list_menu.addSeparator()
        # TODO mark_as_downloaded mark_as_converted remove_from_disk
        list_menu.exec_(QCursor.pos())

    def chapter_clear_clicked(self):
        selected_chapters = self.chapters_list.selectedItems()
        for selected_chapter in selected_chapters:
            chapter = selected_chapter.data(QtCore.Qt.UserRole)
            chapter.downloaded = chapter.converted = False
            chapter.pages = []
        self.repaint_chapters()

    def chapter_convert_clicked(self):
        # TODO
        raise NotImplementedError

    def chapter_download_clicked(self):
        selected_chapters = self.chapters_list.selectedItems()
        ch = [selected_chapter.data(QtCore.Qt.UserRole) for selected_chapter in selected_chapters]
        self.parent().show_msg_on_status_bar(_("Downloading chapters..."))
        t = DownloadThread(self.ddmd, self.single_download_finished, ch)
        self.download_threads[str(t)] = t
        self.download_threads[str(t)].set_name(str(t))
        self.download_threads[str(t)].signal.connect(self.download_finished)
        self.download_threads[str(t)].start()

    def chapter_double_clicked(self, chapter_index):
        chapter = self.chapters_list.item(chapter_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_chapter(chapter)
        # FIXME double click should open chapter info ?

    def manga_double_clicked(self, manga_index):
        manga = self.mangas_list.item(manga_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_manga(manga)
        self.update_chapters()
        self.mangas_list.item(manga_index).setForeground(QCOLOR_DOWNLOADED)

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
                item.setForeground(QCOLOR_DOWNLOADED)
            if chapter.converted:
                item.setForeground(QCOLOR_CONVERTERR)
            item.setToolTip(chapter.title)
            item.setData(QtCore.Qt.UserRole, chapter)
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
                    item.setForeground(QCOLOR_DOWNLOADED)
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
        super(GUI, self).__init__()
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
        self.keep_status_msg = 0
        self.show()

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        # TODO
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
        # TODO END

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

    def clear_status_bar(self):
        self.statusBar().clearMessage()

    def show_msg_window(self, title, msg):
        QMessageBox.question(self, title, msg, QMessageBox.Ok)


def start_gui(title):
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('fusion')
    gui = GUI(qt_app, title)
    atexit.register(gui.before_exit)
    sys.exit(qt_app.exec_())
