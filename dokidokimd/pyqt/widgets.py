import subprocess
from typing import Dict

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QCursor, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QListWidget, QAction, \
    QListWidgetItem, QLineEdit

from consts import QCOLOR_DOWNLOADED, QCOLOR_CONVERTERR
from controller import DDMDController
from tools.kz_logger import get_logger
from tools.thread_helpers import DownloadThread, ConvertThread
from tools.translator import translate as _

logger = get_logger(__name__)


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
        self.ddmd = controller                          # type: DDMDController
        self.filter_text = ''                           # type: str
        self.download_threads = dict()                  # type: Dict
        self.convert_threads = dict()                   # type: Dict

        hbox = QHBoxLayout(self)
        vbox_left = QVBoxLayout(self)
        hbox.addLayout(vbox_left)
        vbox_right = QVBoxLayout(self)
        search_hbox = QHBoxLayout()
        hbox.addLayout(vbox_right)

        self.combo_box_sites = QComboBox()
        btn_crawl_site = QPushButton(parent=self)
        self.mangas_list = ListWidget(_('No mangas'))
        self.filter_mangas_textbox = QLineEdit()
        self.chapters_list = ListWidget(_('No chapters'))
        self.manga_context_menu = QtWidgets.QMenu()
        self.chapter_context_menu = QtWidgets.QMenu()

        # region combobox for manga sites
        self.combo_box_sites.currentIndexChanged.connect(
            lambda: self.site_selected(self.combo_box_sites.currentIndex())
        )
        for idx, site in enumerate(self.ddmd.get_sites()):
            self.combo_box_sites.addItem('{}:{}({})'.format(idx, site.site_name, len(site.mangas)), site)
        self.combo_box_sites.setMaximumWidth(self.combo_box_sites.sizeHint().width())
        vbox_left.addLayout(search_hbox)
        search_hbox.addWidget(self.combo_box_sites)
        # endregion

        # region button for search manga site
        btn_crawl_site.setMaximumSize(btn_crawl_site.sizeHint())
        btn_crawl_site.clicked.connect(
            lambda: self.update_mangas()
        )
        btn_crawl_site.setIcon(QIcon('../icons/baseline_search_black_18dpx2.png'))
        search_hbox.addWidget(btn_crawl_site)
        search_hbox.setAlignment(QtCore.Qt.AlignLeft)
        # endregion

        # region list widget for mangas
        self.mangas_list.doubleClicked.connect(
            lambda: self.manga_double_clicked(self.mangas_list.currentRow())
        )
        self.mangas_list.clicked.connect(
            lambda: self.manga_selected(self.mangas_list.currentRow())
        )
        self.mangas_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mangas_list.customContextMenuRequested.connect(lambda: self.manga_context_menu.exec_(QCursor.pos()))
        vbox_left.addWidget(self.mangas_list)
        # endregion

        # region textbox for manga filter
        self.filter_mangas_textbox.setToolTip(_('Filter'))
        self.filter_mangas_textbox.setPlaceholderText(_('Search manga...'))
        self.filter_mangas_textbox.textChanged.connect(lambda: self.apply_filter(self.filter_mangas_textbox.text()))
        vbox_left.addWidget(self.filter_mangas_textbox)
        # endregion

        # region list widget for manga chapters
        self.chapters_list.doubleClicked.connect(
            lambda: self.chapter_double_clicked(self.chapters_list.currentRow())
        )
        self.chapters_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        hbox.addWidget(self.chapters_list)
        self.chapters_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.chapters_list.customContextMenuRequested.connect(lambda: self.chapter_context_menu.exec_(QCursor.pos()))
        # endregion

        # region Manga contextmenu
        clear_action = QAction(_('Clear item'), self)
        clear_action.triggered.connect(self.manga_clear_clicked)
        self.manga_context_menu.addAction(clear_action)
        self.manga_context_menu.addSeparator()
        download_action = QAction(_('Download'), self)
        download_action.triggered.connect(self.manga_download_clicked)
        self.manga_context_menu.addAction(download_action)
        self.manga_context_menu.addSeparator()
        open_explorer_action = QAction(_('Show in File Explorer'), self)
        open_explorer_action.triggered.connect(self.manga_open_file_explorer)
        self.manga_context_menu.addAction(open_explorer_action)
        open_terminal_action = QAction(_('Show in Terminal'), self)
        open_terminal_action.triggered.connect(self.manga_open_terminal)
        self.manga_context_menu.addAction(open_terminal_action)
        # endregion

        # region Chapter contextmenu
        clear_action = QAction(_('Clear item'), self)
        clear_action.triggered.connect(self.chapter_clear_clicked)
        self.chapter_context_menu.addAction(clear_action)
        self.chapter_context_menu.addSeparator()
        download_action = QAction(_('Download'), self)
        download_action.triggered.connect(self.chapter_download_clicked)
        self.chapter_context_menu.addAction(download_action)
        convert_action = QAction(_('Save as PDF'), self)
        convert_action.triggered.connect(self.chapter_convert_clicked)
        self.chapter_context_menu.addAction(convert_action)
        self.chapter_context_menu.addSeparator()
        # TODO add menus (mark_as_downloaded, mark_as_converted, remove_from_disk)
        # TODO add menu open explorer disk location/open terminal
        # endregion

        self.setLayout(hbox)

    def repaint_chapters(self):
        indexes = [idx.row() for idx in self.chapters_list.selectedIndexes()]
        self.load_stored_chapters(self.ddmd.get_current_manga())
        for i in indexes:
            self.chapters_list.item(i).setSelected(True)

    # region Thread slots
    def single_download_finished(self, string):
        self.parent().show_msg_on_status_bar(string)
        self.repaint_chapters()

    def single_convert_finished(self, string):
        self.parent().show_msg_on_status_bar(string)
        self.repaint_chapters()

    def download_finished(self, thread_name):
        self.download_threads.pop(thread_name)
        self.parent().show_msg_on_status_bar(_("Download finished"))
        self.repaint_chapters()

    def convert_finished(self, thread_name):
        self.convert_threads.pop(thread_name)
        self.parent().show_msg_on_status_bar(_("Convert finished"))
        self.repaint_chapters()
    # endregion

    # region chapters_list actions
    def chapter_clear_clicked(self):
        selected_chapters = self.chapters_list.selectedItems()
        for selected_chapter in selected_chapters:
            chapter = selected_chapter.data(QtCore.Qt.UserRole)
            chapter.clear_state()
        self.repaint_chapters()

    def chapter_download_clicked(self):
        selected_chapters = self.chapters_list.selectedItems()
        chapters = [selected_chapter.data(QtCore.Qt.UserRole) for selected_chapter in selected_chapters]
        self.parent().show_msg_on_status_bar(_('Downloading {} chapters...').format(
            self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole).title))
        t = DownloadThread(self.ddmd, self.single_download_finished, chapters)
        self.download_threads[str(t)] = t
        self.download_threads[str(t)].set_name(str(t))
        self.download_threads[str(t)].signal.connect(self.download_finished)
        self.download_threads[str(t)].start()

    def chapter_convert_clicked(self):
        selected_chapters = self.chapters_list.selectedItems()
        ch = [selected_chapter.data(QtCore.Qt.UserRole) for selected_chapter in selected_chapters]
        self.parent().show_msg_on_status_bar(_('Converting {} chapters...').format(
            self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole).title))
        t = ConvertThread(self.ddmd, self.single_convert_finished, ch)
        self.convert_threads[str(t)] = t
        self.convert_threads[str(t)].set_name(str(t))
        self.convert_threads[str(t)].signal.connect(self.convert_finished)
        self.convert_threads[str(t)].start()

    def chapter_double_clicked(self, chapter_index):
        chapter = self.chapters_list.item(chapter_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_chapter(chapter)
        self.chapter_download_clicked()
    # endregion

    # region manga_list actions
    def manga_clear_clicked(self):
        manga = self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole)
        manga.clear_state()
        self.repaint_chapters()

    def manga_download_clicked(self):
        self.download_manga(self.mangas_list.currentRow())

    def manga_double_clicked(self, manga_index):
        self.download_manga(manga_index)

    def manga_selected(self, manga_index):
        manga = self.mangas_list.item(manga_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_manga(manga)
        self.load_stored_chapters()

    def download_manga(self, manga_index):
        manga = self.mangas_list.item(manga_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_manga(manga)
        self.update_chapters()
        self.mangas_list.item(manga_index).setForeground(QCOLOR_DOWNLOADED)

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

    def update_chapters(self):
        try:
            self.parent().setDisabled(True)
            manga = self.ddmd.crawl_manga()
            self.load_stored_chapters(manga)
        except Exception as e:
            logger.warning(_('Could not refresh chapters, reason: {}').format(e))
        finally:
            self.parent().setEnabled(True)
    # endregion

    # region site_combobox actions
    def site_selected(self, site_index):
        site = self.combo_box_sites.itemData(site_index, QtCore.Qt.UserRole)
        self.ddmd.set_cwd_site(site)
        self.load_stored_mangas()
        self.chapters_list.clear()

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
    # endregion

    def manga_open_file_explorer(self):
        manga = self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole)
        path = manga.get_download_path(self.ddmd.sites_location)
        subprocess.call('explorer "{}"'.format(path))

    def manga_open_terminal(self):
        pass

    def apply_filter(self, text):
        self.filter_text = text
        self.load_stored_mangas()
