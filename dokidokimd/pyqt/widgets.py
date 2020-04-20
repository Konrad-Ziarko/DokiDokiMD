import functools
import os
from sys import platform
from typing import Dict

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QPaintEvent, QPainter, QCursor, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QListWidget, QAction, \
    QListWidgetItem, QLineEdit, QProgressBar, QMenu

from dokidokimd.controller import DDMDController
from dokidokimd.pyqt.consts import QCOLOR_DOWNLOADED, QCOLOR_CONVERTERR, QTIMER_REMOVE_TASK_TIMEOUT
from dokidokimd.tools.ddmd_logger import get_logger
from dokidokimd.tools.misc import get_resource_path
from dokidokimd.tools.thread_helpers import SingleChapterDownloadThread, SingleChapterSaveThread, \
    SingleChapterConvertThread, GroupOfThreads
from dokidokimd.tools.translator import translate as _

logger = get_logger(__name__)


def nop():
    pass


def ensure_manga_selected(func):
    try:
        @functools.wraps(func)
        def func_wrapper(*a, **kw):
            if a[0].mangas_list.currentRow() != -1:
                return func(*a, **kw)
            else:
                return nop()

        return func_wrapper
    except Exception as e:
        logger.error(str(e))


def ensure_chapter_selected(func):
    try:
        @functools.wraps(func)
        def func_wrapper(*a, **kw):
            if a[0].chapters_list.currentRow() != -1:
                return func(*a, **kw)
            else:
                return nop()

        return func_wrapper
    except Exception as e:
        logger.error(str(e))


class ListWidget(QListWidget):
    def __init__(self, default_string=_('No Items')):
        QListWidget.__init__(self)
        self.default_string = default_string

    def paintEvent(self, e: QPaintEvent) -> None:
        QListWidget.paintEvent(self, e)
        if self.model() and self.model().rowCount(self.rootIndex()) > 0:
            return
        p = QPainter(self.viewport())
        p.drawText(self.rect(), Qt.AlignCenter, self.default_string)


class FilterMangasTextBox(QLineEdit):
    def __init__(self, apply_filter):
        QLineEdit.__init__(self)
        self.setToolTip(_('Filter'))
        self.setPlaceholderText(_('Search manga...'))
        self.textChanged.connect(apply_filter)


class TasksProgressBar(QProgressBar):
    def __init__(self):
        QProgressBar.__init__(self)
        self.setValue(0)
        self.setMinimum(0)
        self.setMaximum(0)


class SitesSelector(QComboBox):
    def __init__(self, site_selected_action, sites):
        QComboBox.__init__(self)
        self.site_selected_action = site_selected_action
        self.activated.connect(self.site_selected)
        for idx, site in enumerate(sites):
            self.addItem(F'{idx}:{site.site_name}({len(site.mangas)})', site)
        self.setMaximumWidth(self.sizeHint().width())

    def site_selected(self, site_index):
        site = self.itemData(site_index, QtCore.Qt.UserRole)
        self.site_selected_action(site_index, site)


class MangaSiteWidget(QWidget):
    def connect_actions(self, show_msg_on_status_bar, lock_gui, unlock_gui):
        self.show_msg_on_status_bar = show_msg_on_status_bar
        self.lock_gui = lock_gui
        self.unlock_gui = unlock_gui

    def __init__(self, controller):
        QWidget.__init__(self)
        self.ddmd = controller  # type: DDMDController
        self.threads = dict()  # type: Dict

        self.show_msg_on_status_bar = None
        self.lock_gui = None
        self.unlock_gui = None

        root_layout = QVBoxLayout(self)
        manga_site_progress_layout = QHBoxLayout()
        filter_mangas_layout = QHBoxLayout()
        manga_chapter_layout = QHBoxLayout()
        task_information_layout = QHBoxLayout()

        root_layout.addLayout(manga_site_progress_layout)
        root_layout.addLayout(filter_mangas_layout)
        root_layout.addLayout(manga_chapter_layout)
        root_layout.addLayout(task_information_layout)

        left_part_of_top = QVBoxLayout()
        right_part_of_top = QVBoxLayout()
        manga_site_progress_layout.addLayout(left_part_of_top)
        manga_site_progress_layout.addLayout(right_part_of_top)
        search_part = QHBoxLayout()
        left_part_of_top.addLayout(search_part)
        self.setLayout(root_layout)

        self.filter_mangas_textbox = FilterMangasTextBox(self.apply_filter)
        filter_mangas_layout.addWidget(self.filter_mangas_textbox)

        # region progress bar
        self.progress_bar = TasksProgressBar()
        right_part_of_top.addWidget(self.progress_bar)
        # endregion

        # region button for search manga site
        btn_crawl_site = QPushButton()
        btn_crawl_site.setMaximumSize(btn_crawl_site.sizeHint())
        btn_crawl_site.clicked.connect(self.update_mangas)
        btn_crawl_site.setIcon(QIcon(get_resource_path('icons/baseline_search_black_18dpx2.png')))
        # endregion

        # region manga sites selector
        if not 0 < self.ddmd.last_site < len(self.ddmd.get_sites()):
            self.ddmd.set_new_last_site(0)
        self.combo_box_sites = SitesSelector(self.site_selected, self.ddmd.get_sites())
        search_part.addWidget(self.combo_box_sites)
        search_part.addWidget(btn_crawl_site)
        search_part.setAlignment(QtCore.Qt.AlignLeft)
        # endregion

        # region tasks list widget
        self.tasks_list = ListWidget(_('No tasks'))
        self.tasks_list_context_menu = QMenu()
        self.tasks_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tasks_list.customContextMenuRequested.connect(self.open_tasks_list_context_menu)
        task_information_layout.addWidget(self.tasks_list)
        self.tasks_list.setMaximumHeight(100)
        clear_tasks_log = QAction(_('Clear tasks log'), self)
        clear_tasks_log.triggered.connect(lambda: self.tasks_list.clear())
        self.tasks_list_context_menu.addAction(clear_tasks_log)
        # endregion

        # region list widget for mangas
        self.mangas_list = ListWidget(_('No mangas'))
        self.manga_context_menu = QMenu()
        self.mangas_list.doubleClicked.connect(self.manga_download_clicked)
        self.mangas_list.clicked.connect(self.manga_selected)
        self.mangas_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mangas_list.customContextMenuRequested.connect(self.open_manga_context_menu)
        manga_chapter_layout.addWidget(self.mangas_list)
        # endregion

        # region list widget for manga chapters
        self.chapters_list = ListWidget(_('No chapters'))
        self.chapter_context_menu = QMenu()
        self.chapters_list.doubleClicked.connect(self.chapter_double_clicked)
        self.chapters_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.chapters_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.chapters_list.customContextMenuRequested.connect(self.open_chapter_context_menu)
        manga_chapter_layout.addWidget(self.chapters_list)
        # endregion

        # region Manga contextmenu
        clear_action = QAction(_('Clear item'), self)
        clear_action.triggered.connect(self.manga_clear_clicked)
        self.manga_context_menu.addAction(clear_action)
        self.manga_context_menu.addSeparator()

        download_action = QAction(_('Index chapters'), self)
        download_action.triggered.connect(self.manga_download_clicked)
        self.manga_context_menu.addAction(download_action)
        self.manga_context_menu.addSeparator()

        open_explorer_action = QAction(_('Show in File Explorer'), self)
        open_explorer_action.triggered.connect(
            lambda: self.open_file_explorer('M')
        )
        self.manga_context_menu.addAction(open_explorer_action)

        open_terminal_action = QAction(_('Show in Terminal'), self)
        open_terminal_action.triggered.connect(
            lambda: self.open_terminal('M')
        )
        self.manga_context_menu.addAction(open_terminal_action)
        self.manga_context_menu.addSeparator()

        remove_from_disk = QAction(_('Remove from disk'), self)
        remove_from_disk.triggered.connect(
            lambda: self.remove_from_disk('M')
        )
        self.manga_context_menu.addAction(remove_from_disk)
        # endregion

        # region Chapter contextmenu
        clear_action = QAction(_('Clear item'), self)
        clear_action.triggered.connect(self.chapter_clear_clicked)
        self.chapter_context_menu.addAction(clear_action)
        self.chapter_context_menu.addSeparator()

        download_action = QAction(_('Download'), self)
        download_action.triggered.connect(self.start_chapters_download)
        self.chapter_context_menu.addAction(download_action)

        save_action = QAction(_('Save images'), self)
        save_action.triggered.connect(self.start_chapters_save)
        self.chapter_context_menu.addAction(save_action)

        convert_action = QAction(_('Convert to PDF'), self)
        convert_action.triggered.connect(self.start_chapters_convert)
        self.chapter_context_menu.addAction(convert_action)
        self.chapter_context_menu.addSeparator()

        mark_download_action = QAction(_('Mark as downloaded'), self)
        mark_download_action.triggered.connect(self.mark_as_downloaded)
        self.chapter_context_menu.addAction(mark_download_action)

        mark_converted_action = QAction(_('Mark as converted'), self)
        mark_converted_action.triggered.connect(self.mark_as_converted)
        self.chapter_context_menu.addAction(mark_converted_action)
        self.chapter_context_menu.addSeparator()

        open_explorer_action = QAction(_('Show in File Explorer'), self)
        open_explorer_action.triggered.connect(
            lambda: self.open_file_explorer('C')
        )
        self.chapter_context_menu.addAction(open_explorer_action)

        open_terminal_action = QAction(_('Show in Terminal'), self)
        open_terminal_action.triggered.connect(
            lambda: self.open_terminal('C')
        )
        self.chapter_context_menu.addAction(open_terminal_action)
        self.chapter_context_menu.addSeparator()

        remove_from_disk = QAction(_('Remove from disk'), self)
        remove_from_disk.triggered.connect(
            lambda: self.remove_from_disk('C')
        )
        self.chapter_context_menu.addAction(remove_from_disk)
        # endregion
        self.combo_box_sites.setCurrentIndex(self.ddmd.last_site)
        self.combo_box_sites.site_selected(self.ddmd.last_site)

    def open_manga_context_menu(self):
        self.manga_selected(self.mangas_list.currentRow()),
        self.manga_context_menu.exec_(QCursor.pos())

    def open_chapter_context_menu(self):
        self.chapter_context_menu.exec_(QCursor.pos())

    def open_tasks_list_context_menu(self):
        self.tasks_list_context_menu.exec_(QCursor.pos())

    def reload_chapters_list(self):
        indexes = [idx.row() for idx in self.chapters_list.selectedIndexes()]
        self.load_stored_chapters(self.ddmd.get_current_manga())
        for i in indexes:
            self.chapters_list.item(i).setSelected(True)

    def reload_mangas_list(self):
        index = self.mangas_list.currentRow()
        self.load_stored_mangas(site=self.ddmd.get_current_site())
        self.mangas_list.item(index).setSelected(True)

    # region Thread slots
    def group_of_threads_finished(self, thread_name):
        self.threads.pop(thread_name)
        self.show_msg_on_status_bar(_('Job finished'))
        self.reload_chapters_list()

    def task_add_to_list(self, task_id: int, uuid: int, msg: str):
        """
        Add message entry to 'task log' and store it with thread uuid for later identification
        uuid jest 64 digit long so tasks are also numerated with task_id
        This separation is necessary because each group of tasks does not share task counter
            and their taks_id could be ambiguous
        """
        item = QListWidgetItem(F'Task [{task_id}]: {msg}')
        item.setData(QtCore.Qt.UserRole, uuid)
        self.tasks_list.addItem(item)
        self.tasks_list.scrollToBottom()

    def remove_task_from_list(self, uuid: int):
        """
        Remove entries from 'task log' that were inserted by thread with matching uuid
        """
        for tasks_entry in self.tasks_list.findItems('*', Qt.MatchWildcard):
            # iterate over all items from list
            entry_uuid = tasks_entry.data(QtCore.Qt.UserRole)
            if entry_uuid == uuid:
                self.tasks_list.takeItem(self.tasks_list.row(tasks_entry))

    # endregion

    # region chapters_list actions
    @ensure_chapter_selected
    def chapter_clear_clicked(self, *args):
        selected_chapters = self.chapters_list.selectedItems()
        for selected_chapter in selected_chapters:
            chapter = selected_chapter.data(QtCore.Qt.UserRole)
            chapter.clear_state()
        self.reload_chapters_list()

    @ensure_chapter_selected
    def start_chapters_download(self, *args):
        self.start_working_threads(SingleChapterDownloadThread, _('Downloading {} chapters...'))

    @ensure_chapter_selected
    def start_chapters_save(self, *args):
        self.start_working_threads(SingleChapterSaveThread, _('Saving {} chapters...'))

    @ensure_chapter_selected
    def start_chapters_convert(self, *args):
        self.start_working_threads(SingleChapterConvertThread, _('Converting {} chapters...'))

    def start_working_threads(self, thread_job_type, message):
        """
        This method is invoked by context menu actions
        It starts threads and they  context menu entry was selected
        """
        chapters = [selected_chapter.data(QtCore.Qt.UserRole) for selected_chapter in
                    self.chapters_list.selectedItems()]
        self.add_to_progress_max(len(chapters))
        self.show_msg_on_status_bar(message.format(
            self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole).title))
        t = GroupOfThreads(self.ddmd, thread_job_type, chapters, self.task_add_to_list, self.single_task_finished)
        self.threads[str(t)] = t
        t.message.connect(self.group_of_threads_finished)
        t.finished.connect(self.remove_from_progress_max)
        t.start()

    @ensure_chapter_selected
    def chapter_double_clicked(self, *args):
        chapter_index = self.chapters_list.currentRow()
        chapter = self.chapters_list.item(chapter_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_chapter(chapter)
        self.start_chapters_download()

    @ensure_chapter_selected
    def mark_as_downloaded(self, *args):
        if self.mangas_list.currentRow() != -1:
            selected_chapters = self.chapters_list.selectedItems()
            chapters = [selected_chapter.data(QtCore.Qt.UserRole) for selected_chapter in selected_chapters]
            for chapter in chapters:
                chapter.set_downloaded(True)
            self.reload_chapters_list()

    @ensure_chapter_selected
    def mark_as_converted(self, *args):
        if self.mangas_list.currentRow() != -1:
            selected_chapters = self.chapters_list.selectedItems()
            chapters = [selected_chapter.data(QtCore.Qt.UserRole) for selected_chapter in selected_chapters]
            for chapter in chapters:
                chapter.converted = True
            self.reload_chapters_list()

    # endregion

    # region manga_list actions
    @ensure_manga_selected
    def manga_clear_clicked(self, *args):
        manga = self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole)
        manga.clear_state()
        self.reload_mangas_list()
        self.load_stored_chapters()

    def manga_download_clicked(self):
        self.download_manga(self.mangas_list.currentRow())

    @ensure_manga_selected
    def manga_selected(self, manga_index):
        if isinstance(manga_index, QModelIndex):
            manga_index = manga_index.row()
        manga = self.mangas_list.item(manga_index).data(QtCore.Qt.UserRole)
        self.ddmd.set_cwd_manga(manga)
        self.load_stored_chapters()

    @ensure_manga_selected
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
            self.lock_gui()
            manga = self.ddmd.crawl_manga()
        except Exception as e:
            logger.warning(_(F'Could not download chapters for {self.ddmd.get_current_manga().title}, reason: {e}'))
            self.show_msg_on_status_bar(_(F'Could not download chapters for {self.ddmd.get_current_manga().title}'))
        else:
            self.load_stored_chapters(manga)
        finally:
            self.unlock_gui()

    # endregion

    # region site_combobox actions
    def site_selected(self, site_index, site):
        self.ddmd.set_new_last_site(site_index)
        self.ddmd.set_cwd_site(site)
        self.load_stored_mangas(site=site)
        self.chapters_list.clear()

    def load_stored_mangas(self, site=None):
        filter_text = self.filter_mangas_textbox.text()
        if not site:
            site = self.ddmd.get_current_site()
        self.mangas_list.clear()
        for manga in site.mangas:
            if filter_text == '' or filter_text.lower() in manga.title.lower():
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
            self.lock_gui()
            site = self.ddmd.crawl_site()
        except Exception as e:
            logger.warning(_(F'Could not refresh site, reason: {e}'))
            self.show_msg_on_status_bar(_('Could not refresh site, for more info look into log file.'))
        else:
            self.load_stored_mangas(site=site)
        finally:
            self.unlock_gui()

    # endregion

    # region progress bar actions
    def single_task_finished(self, uuid: int):
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        QtCore.QTimer.singleShot(QTIMER_REMOVE_TASK_TIMEOUT, lambda: self.remove_task_from_list(uuid))

    def add_to_progress_max(self, value: int):
        self.progress_bar.setMaximum(self.progress_bar.maximum() + value)

    def remove_from_progress_max(self, value: int):
        self.progress_bar.setMaximum(max(0, self.progress_bar.maximum() - value))

    # endregion

    @ensure_manga_selected
    def open_file_explorer(self, level: str):
        try:
            base_path = self.ddmd.sites_location
            if level == 'M':
                list_object = self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole)
            elif level == 'C':
                list_object = self.chapters_list.item(self.chapters_list.currentRow()).data(QtCore.Qt.UserRole)
            else:
                return
            path = list_object.get_download_path(base_path)
            if not os.path.exists(path):
                path = list_object.get_pdf_path(base_path)
            if platform == 'linux' or platform == 'linux2':
                os.system(F'gio open "{path}"')
            elif platform == 'win32':
                os.system(F'explorer "{path}"')
        except Exception as e:
            logger.warning(_(F'There was a problem while opening manga: [{e}]'))

    @ensure_manga_selected
    def open_terminal(self, level: str):
        try:
            base_path = self.ddmd.sites_location
            if level == 'M':
                list_object = self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole)
            elif level == 'C':
                list_object = self.chapters_list.item(self.chapters_list.currentRow()).data(QtCore.Qt.UserRole)
            else:
                return
            path = list_object.get_download_path(base_path)
            if not os.path.exists(path):
                path = list_object.get_pdf_path(base_path)
            if platform == 'linux' or platform == 'linux2':
                os.system(F'gnome-terminal --working-directory="{path}"')
            elif platform == 'win32':
                os.system(F'start cmd /K "cd /d {path}"')
        except Exception as e:
            logger.warning(_(F'There was a problem while opening manga: [{e}]'))

    @ensure_manga_selected
    def remove_from_disk(self, level: str):
        base_path = self.ddmd.sites_location
        if level == 'M':
            list_object = [self.mangas_list.item(self.mangas_list.currentRow()).data(QtCore.Qt.UserRole)]
            self.manga_clear_clicked()
        elif level == 'C':
            list_object = [chapter.data(QtCore.Qt.UserRole) for chapter in self.chapters_list.selectedItems()]
            self.chapter_clear_clicked()
        else:
            return
        for obj in list_object:
            obj.remove_from_disk(base_path)

    def apply_filter(self):
        self.load_stored_mangas()
