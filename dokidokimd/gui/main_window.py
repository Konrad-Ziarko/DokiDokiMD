import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QFrame, QToolButton, QLabel, QHBoxLayout, QSizePolicy


class MyWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setStyleSheet("background: qlineargradient( x1: 0, y1: 0, x2: 1, y2 : 0, stop: 0 black, stop: 1 blue);")

        self.setWindowTitle("DokiDokiMangaDownloader")
        self.resize(550, 400)
        self.tabs = {"General": QtWidgets.QWidget(), "Manga Sites": QtWidgets.QWidget(), "Proxy": QtWidgets.QWidget(),
                     "Authentication": QtWidgets.QWidget(), "Updates": QtWidgets.QWidget(),
                     "Images": QtWidgets.QWidget(), "Download": QtWidgets.QWidget(), "1": QtWidgets.QWidget(),
                     "2": QtWidgets.QWidget(), "3": QtWidgets.QWidget()}

        layout = QtWidgets.QVBoxLayout()

        self.tabs_widget = QtWidgets.QTabWidget(self)
        self.tabs_widget.setStyleSheet("QTabBar::tab { background: gray; color: white; padding: 5px; } "
                                       "QTabBar::tab:selected { background: red; } "
                                       "QTabWidget::pane { border: 5px; } "
                                       "QWidget { background: lightgray; } ")

        self.tabs_widget.addTab(self.tabs["General"], "General")
        self.tabs_widget.addTab(self.tabs["Manga Sites"], "Manga Sites")
        self.tabs_widget.addTab(self.tabs["Proxy"], "Proxy")
        self.tabs_widget.addTab(self.tabs["Authentication"], "Authentication")
        self.tabs_widget.addTab(self.tabs["Updates"], "Updates")
        self.tabs_widget.addTab(self.tabs["Images"], "Images")
        self.tabs_widget.addTab(self.tabs["Download"], "Download")
        self.tabs_widget.addTab(self.tabs["1"], "1")
        self.tabs_widget.addTab(self.tabs["2"], "2")
        self.tabs_widget.addTab(self.tabs["3"], "3")
        # self.
        layout.addWidget(self.tabs_widget)

        self.setLayout(layout)


app = QtWidgets.QApplication(sys.argv)
widget = MyWidget()
widget.show()
sys.exit(app.exec_())
