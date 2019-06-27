from PyQt5.QtCore import QThread, pyqtSignal


class SingleThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, chapter):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.chapter = chapter


class GroupOfThreads(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, single_thread_class, callable_fun, chapters):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.single_thread_class = single_thread_class  # type: SingleThread
        self.chapters = chapters
        self.callable_fun = callable_fun
        self.threads = list()

    def set_name(self, thread_name):
        self.name = thread_name

    def run(self):
        for chapter in self.chapters:
            t = self.single_thread_class(self.ddmd, chapter)
            t.signal.connect(self.callable_fun)
            self.threads.append(t)
            t.start()
        for t in self.threads:
            t.wait()
        self.signal.emit(self.name)


class SingleChapterDownloadThread(SingleThread):
    def __init__(self, ddmd, chapter):
        SingleThread.__init__(self, ddmd, chapter)

    def run(self):
        try:
            self.ddmd.crawl_chapter(self.chapter)
        except Exception as e:
            self.signal.emit('Could not download chapter {}, reason {}'.format(self.chapter.title, e))


class SingleChapterSaveThread(SingleThread):
    def __init__(self, ddmd, chapter):
        SingleThread.__init__(self, ddmd, chapter)

    def run(self):
        if self.chapter.in_memory:
            ret, path = self.ddmd.save_images_from_chapter(self.chapter)
            if ret:
                self.signal.emit('Downloaded {}'.format(self.chapter.title))
            else:
                self.signal.emit('Could not save downloaded chapter {}, in path {}'.format(self.chapter.title, path))
        else:
            try:
                self.signal.emit("Downloading {}".format(self.chapter.title))
                self.ddmd.crawl_chapter(self.chapter)
            except Exception as e:
                self.signal.emit('Could not download chapter {}, reason {}'.format(self.chapter.title, e))
            else:
                ret, path = self.ddmd.save_images_from_chapter(self.chapter)
                if ret:
                    self.signal.emit('Saved chapter {}'.format(self.chapter.title))
                else:
                    self.signal.emit('Could not save downloaded chapter {}, in path {}'.format(self.chapter.title, path))


class SingleChapterConvertThread(SingleThread):
    def __init__(self, ddmd, chapter):
        SingleThread.__init__(self, ddmd, chapter)

    def run(self):
        if self.chapter.in_memory:
            ret, path = self.ddmd.convert_chapter_2_pdf(self.chapter)
            if ret:
                self.signal.emit('Converted {}'.format(self.chapter.title))
            else:
                self.signal.emit('Could not convert chapter {}'.format(self.chapter.title))
        else:
            if self.ddmd.chapter_images_present(self.chapter):
                ret, path = self.ddmd.convert_images_2_pdf(self.chapter)
                if ret:
                    self.signal.emit("Converted {}".format(self.chapter.title))
                else:
                    self.signal.emit(
                        'Could not save convert chapter {}, in path {}'.format(self.chapter.title, path))
            else:
                try:
                    self.signal.emit("Downloading {}".format(self.chapter.title))
                    self.ddmd.crawl_chapter(self.chapter)
                except Exception as e:
                    self.signal.emit('Could not download chapter {}, reason {}'.format(self.chapter.title, e))
                else:
                    ret, path = self.ddmd.convert_chapter_2_pdf(self.chapter)
                    if ret:
                        self.signal.emit("Converted {}".format(self.chapter.title))
                    else:
                        self.signal.emit(
                            'Could not save convert chapter {}, in path {}'.format(self.chapter.title, path))
