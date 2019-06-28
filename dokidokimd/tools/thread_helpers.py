from PyQt5.QtCore import QThread, pyqtSignal


class SingleThread(QThread):
    message = pyqtSignal('PyQt_PyObject')
    finished = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, chapter):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.chapter = chapter


class GroupOfThreads(QThread):
    message = pyqtSignal('PyQt_PyObject')
    finished = pyqtSignal('PyQt_PyObject')

    def __init__(self, ddmd, single_thread_class, message_signal, chapters, finished_signal, threads_max):
        QThread.__init__(self)
        self.ddmd = ddmd
        self.single_thread_class = single_thread_class  # type: SingleThread
        self.chapters = chapters
        self.message_signal = message_signal
        self.finished_signal = finished_signal
        self.threads = list()
        self.threads_max = threads_max

    def set_name(self, thread_name):
        self.name = thread_name

    def run(self):
        if len(self.chapters) > self.threads_max:
            for i in range(0, len(self.chapters), self.threads_max):
                chunk = self.chapters[i:i + self.threads_max]
                for chapter in chunk:
                    t = self.single_thread_class(self.ddmd, chapter)
                    t.message.connect(self.message_signal)
                    t.finished.connect(self.finished_signal)
                    self.threads.append(t)
                    t.start()
                for t in self.threads:
                    t.wait()
                self.threads.clear()
        else:
            for chapter in self.chapters:
                t = self.single_thread_class(self.ddmd, chapter)
                t.message.connect(self.message_signal)
                t.finished.connect(self.finished_signal)
                self.threads.append(t)
                t.start()
            for t in self.threads:
                t.wait()
        self.message.emit(self.name)
        self.finished.emit(len(self.chapters))


class SingleChapterDownloadThread(SingleThread):
    def __init__(self, ddmd, chapter):
        SingleThread.__init__(self, ddmd, chapter)

    def run(self):
        try:
            self.ddmd.crawl_chapter(self.chapter)
        except Exception as e:
            self.message.emit('Could not download chapter {}, reason {}'.format(self.chapter.title, e))
        else:
            self.message.emit('Downloaded {}'.format(self.chapter.title))
        finally:
            self.finished.emit('')


class SingleChapterSaveThread(SingleThread):
    def __init__(self, ddmd, chapter):
        SingleThread.__init__(self, ddmd, chapter)

    def run(self):
        if self.chapter.in_memory:
            ret, path = self.ddmd.save_images_from_chapter(self.chapter)
            if ret:
                self.message.emit('Downloaded {}'.format(self.chapter.title))
            else:
                self.message.emit('Could not save downloaded chapter {}, in path {}'.format(self.chapter.title, path))
        else:
            try:
                self.message.emit('Downloading {}'.format(self.chapter.title))
                self.ddmd.crawl_chapter(self.chapter)
            except Exception as e:
                self.message.emit('Could not download chapter {}, reason {}'.format(self.chapter.title, e))
            else:
                ret, path = self.ddmd.save_images_from_chapter(self.chapter)
                if ret:
                    self.message.emit('Saved chapter {}'.format(self.chapter.title))
                else:
                    self.message.emit('Could not save downloaded chapter {}, in path {}'.format(self.chapter.title, path))
        self.finished.emit('')


class SingleChapterConvertThread(SingleThread):
    def __init__(self, ddmd, chapter):
        SingleThread.__init__(self, ddmd, chapter)

    def run(self):
        if self.chapter.in_memory:
            ret, path = self.ddmd.convert_chapter_2_pdf(self.chapter)
            if ret:
                self.message.emit('Converted {}'.format(self.chapter.title))
            else:
                self.message.emit('Could not convert chapter {} to PDF file {}'.format(self.chapter.title, path))
        else:
            if self.ddmd.chapter_images_present(self.chapter):
                ret, path = self.ddmd.convert_images_2_pdf(self.chapter)
                if ret:
                    self.message.emit('Converted {}'.format(self.chapter.title))
                else:
                    self.message.emit(
                        'Could not save convert chapter {}, in path {}'.format(self.chapter.title, path))
            else:
                try:
                    self.message.emit('Downloading {}'.format(self.chapter.title))
                    self.ddmd.crawl_chapter(self.chapter)
                except Exception as e:
                    self.message.emit('Could not download chapter {}, reason {}'.format(self.chapter.title, e))
                else:
                    ret, path = self.ddmd.convert_chapter_2_pdf(self.chapter)
                    if ret:
                        self.message.emit('Converted {}'.format(self.chapter.title))
                    else:
                        self.message.emit(
                            'Could not save convert chapter {}, in path {}'.format(self.chapter.title, path))
        self.finished.emit('')
