import atexit
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow, QHBoxLayout, \
    QComboBox, QListWidget, QMessageBox, QAction, QMenu, QAbstractButton, QListWidgetItem

from controller import DDMDController
from tools.kz_logger import get_logger
from tools.translator import translate as _

logger = get_logger('.'.join(__name__.split('.')[1:]))


class ImageButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(ImageButton, self).__init__(parent)
        self.bitmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.bitmap)

    def sizeHint(self):
        return self.bitmap.size()


class MangaSiteWidget(QWidget):
    def __init__(self, parent, controller):
        super(QWidget, self).__init__(parent)
        self.ddmd = controller

        hbox = QHBoxLayout(self)
        vbox_left = QVBoxLayout(self)
        hbox.addLayout(vbox_left)
        vbox_right = QVBoxLayout(self)
        search_hbox = QHBoxLayout()
        combo_box_sites = QComboBox()
        self.mangas_list = QListWidget()
        self.chapters_list = QListWidget()
        hbox.addLayout(vbox_right)

        combo_box_sites.currentIndexChanged.connect(
            lambda: self.site_selected(combo_box_sites.currentIndex())
        )
        combo_box_sites.addItems(
            ['{}:{}'.format(key[0], key[1]) for key in self.ddmd.get_sites()]
        )
        combo_box_sites.setMaximumWidth(combo_box_sites.sizeHint().width())
        vbox_left.addLayout(search_hbox)
        search_hbox.addWidget(combo_box_sites)
        # get mangas for site from drop down
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
        #self.load_stored_mangas(combo_box_sites.currentIndex())
        vbox_left.addWidget(self.mangas_list)

        ##
        # self.chapters_list.doubleClicked.connect(
        #     lambda: pass
        # )
        hbox.addWidget(self.chapters_list)
        self.setLayout(hbox)

    def manga_double_clicked(self, manga_index):
        self.ddmd.set_cwd_manga(manga_index)
        self.update_chapters()

    def manga_selected(self, manga_index):
        self.ddmd.set_cwd_manga(manga_index)
        self.load_stored_chapters()

    def site_selected(self, site_index):
        self.ddmd.set_cwd_site(site_index)
        self.load_stored_mangas()

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
            item = QListWidgetItem(manga.title)
            if manga.downloaded:
                item.setForeground(QColor(23, 150, 200, 250))
            item.setToolTip(manga.title)
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
        finally:
            self.parent().setEnabled(True)


class GUI(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.controller = DDMDController()
        self.title = title
        self.setWindowTitle(self.title)
        self.main_widget = MangaSiteWidget(self, self.controller)
        self.setCentralWidget(self.main_widget)
        self.styleSheet()
        self.init_menu_bar()
        self.show()

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(_('File'))
        options_menu = menu_bar.addMenu(_('Options'))
        imp_menu = QMenu('Import', self)
        #imp_menu.triggered.connect(lambda: print('asd'))
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

    def before_exit(self):
        self.controller.store_sites()

    def change_sot(self, is_checked):
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
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    gui = GUI(title)
    atexit.register(gui.before_exit)
    sys.exit(app.exec_())
