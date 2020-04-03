import sys
from os import urandom

from PyQt5.QtCore import QThread, pyqtSignal

from dokidokimd.tools.ddmd_logger import get_logger
from dokidokimd.tools.translator import translate as _

logger = get_logger(__name__)


class SingleThread(QThread):
    finished = pyqtSignal('PyQt_PyObject')
    message = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, ddmd, chapter, uuid, task_id):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.chapter = chapter
        self.uuid = uuid
        self.task_id = task_id


class GroupOfThreads(QThread):
    message = pyqtSignal('PyQt_PyObject')
    finished = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, single_thread_class, chapters, task_add_signal, finished_signal):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.single_thread_class = single_thread_class
        self.chapters = chapters
        self.finished_signal = finished_signal
        self.task_add_signal = task_add_signal
        self.threads = list()
        self.threads_max = self.ddmd.config.max_threads
        self.counter = 0

    def set_name(self, thread_name):
        self.name = thread_name

    def run(self):
        if len(self.chapters) > self.threads_max:
            for i in range(0, len(self.chapters), self.threads_max):
                chunk = self.chapters[i:i + self.threads_max]
                self.start_threads(chunk)
        else:
            self.start_threads(self.chapters)
        self.message.emit(self.name)
        self.finished.emit(len(self.chapters))

    def start_threads(self, chapters):
        for chapter in chapters:
            t = self.single_thread_class(self.ddmd, chapter, int.from_bytes(urandom(64), sys.byteorder), self.counter)
            self.counter += 1
            t.message.connect(self.task_add_signal)
            t.finished.connect(self.finished_signal)
            self.threads.append(t)
            t.start()
        for t in self.threads:
            t.wait()
        self.threads.clear()


class SingleChapterDownloadThread(SingleThread):

    def run(self):
        try:
            try:
                self.message.emit(self.task_id, self.uuid, _(F'Downloading chapter [{self.chapter.title}]...'))
                self.ddmd.crawl_chapter(self.chapter)
            except Exception as e:
                msg = _(F'Could not download chapter [{self.chapter.title}], reason {e}')
                self.message.emit(self.task_id, self.uuid, msg)
                logger.error(msg)
            else:
                self.message.emit(self.task_id, self.uuid, _(F'Downloaded chapter [{self.chapter.title}]'))
            finally:
                self.finished.emit(self.uuid)
        except Exception as e:
            logger.error(str(e))


class SingleChapterSaveThread(SingleThread):

    def run(self):
        try:
            if not self.chapter.in_memory:
                try:
                    self.message.emit(self.task_id, self.uuid, _(F'Downloading chapter [{self.chapter.title}]...'))
                    self.ddmd.crawl_chapter(self.chapter)
                except Exception as e:
                    msg = _(F'Could not download chapter [{self.chapter.title}], reason {e}')
                    self.message.emit(self.task_id, self.uuid, msg)
                    logger.error(msg)
                    return
            ret, path = self.chapter.save_images(self.ddmd.sites_location)
            if ret:
                self.message.emit(self.task_id, self.uuid, _(F'Saved chapter [{self.chapter.title}]'))
            else:
                self.message.emit(self.task_id, self.uuid, _(F'Could not save downloaded chapter [{self.chapter.title}], in path {path}'))
            self.finished.emit(self.uuid)
        except Exception as e:
            logger.error(str(e))


class SingleChapterConvertThread(SingleThread):

    def run(self):
        try:
            if not self.chapter.in_memory and not self.chapter.chapter_images_present(self.ddmd.sites_location):
                try:
                    self.message.emit(self.task_id, self.uuid, _(F'Downloading chapter [{self.chapter.title}]...'))
                    self.ddmd.crawl_chapter(self.chapter)
                except Exception as e:
                    self.message.emit(self.task_id, self.uuid, _(F'Could not download chapter [{self.chapter.title}], reason {e}'))
                    return
            ret, path = self.chapter.make_pdf(self.ddmd.sites_location)
            if ret:
                self.message.emit(self.task_id, self.uuid, _(F'Converted chapter [{self.chapter.title}]'))
            else:
                self.message.emit(self.task_id, self.uuid, _(F'Could not convert chapter [{self.chapter.title}] to PDF file {path}'))
            self.finished.emit(self.uuid)
        except Exception as e:
            logger.error(str(e))
