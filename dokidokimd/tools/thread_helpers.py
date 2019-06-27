from PyQt5.QtCore import QThread, pyqtSignal


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

    def set_name(self, thread_name):
        self.name = thread_name

    def run(self):
        for chapter in self.chapters:
            t = SingleChapterDownloadThread(self.ddmd, chapter)
            t.signal.connect(self.callable_fun)
            self.threads.append(t)
            t.start()
        for t in self.threads:
            t.wait()
        self.signal.emit(self.name)


class SingleChapterConvertThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, chapter):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.chapter = chapter

    def run(self):
        if self.chapter.in_memory:
            self.ddmd.convert_chapter_2_pdf(self.chapter)
        else:
            if not self.ddmd.chapter_images_present(self.chapter):
                self.signal.emit("Downloading {}".format(self.chapter.title))
                self.ddmd.crawl_chapter(self.chapter)
            self.ddmd.convert_images_2_pdf(self.chapter)
            self.signal.emit("Converted {}".format(self.chapter.title))


class ConvertThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, callable_fun, chapters):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.chapters = chapters
        self.callable_fun = callable_fun
        self.threads = list()

    def set_name(self, thread_name):
        self.name = thread_name

    def run(self):
        for chapter in self.chapters:
            t = SingleChapterConvertThread(self.ddmd, chapter)
            t.signal.connect(self.callable_fun)
            self.threads.append(t)
            t.start()
        for t in self.threads:
            t.wait()
        self.signal.emit(self.name)
