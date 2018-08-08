import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QFrame, QToolButton, QLabel, QHBoxLayout, QSizePolicy


class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint);
        css = "\
        QWidget{\
            Background: red;\
            color:white;\
            font:12px bold;\
            font-weight:bold;\
            border-radius: 1px;\
            height: 11px;\
        }\
        QDialog{\
            Background-image:url('img/titlebar bg.png');\
            font-size:12px;\
            color: black;\
\
        }\
        QToolButton{\
            Background: blue;\
            font-size:11px;\
        }\
        QToolButton:hover{\
            Background: red;\
            font-size:11px;\
        }\
        "
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QtGui.QPalette.Highlight)
        self.setStyleSheet(css)
        self.minimize=QToolButton(self)
        self.minimize.setIcon(QtGui.QIcon('img/min.png'))
        self.maximize=QToolButton(self)
        self.maximize.setIcon(QtGui.QIcon('img/max.png'))
        close=QToolButton(self)
        close.setIcon(QtGui.QIcon('img/close.png'))
        self.minimize.setMinimumHeight(10)
        close.setMinimumHeight(10)
        self.maximize.setMinimumHeight(10)
        label=QLabel(self)
        label.setText("DokiDokiMangaDownloader")
        self.setWindowTitle("DokiDokiMangaDownloader")
        hbox=QHBoxLayout(self)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.maximize)
        hbox.addWidget(close)
        hbox.insertStretch(1,500)
        hbox.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.maxNormal=False
        #close.connect(self.close, QtCore.SIGNAL("clicked()"))
        #self.minimize.connect(self.showSmall, QtCore.SIGNAL("clicked()"))
        #self.maximize.connect(self.showMaxRestore, QtCore.SIGNAL("clicked()"))

    def showSmall(self):
        widget.showMinimized();

    def showMaxRestore(self):
        if(self.maxNormal):
            widget.showNormal();
            self.maxNormal= False;
            self.maximize.setIcon(QtGui.QIcon('img/max.png'));
            print ('1')
        else:
            widget.showMaximized();
            self.maxNormal=  True;
            print ('2')
            self.maximize.setIcon(QtGui.QIcon('img/max2.png'));

    def close(self):
        widget.close()

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            widget.moving = True; widget.offset = event.pos()

    def mouseMoveEvent(self,event):
        if widget.moving: widget.move(event.globalPos()-widget.offset)


class MyWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setStyleSheet("background: qlineargradient( x1: 0, y1: 0, x2: 1, y2 : 0, stop: 0 black, stop: 1 blue);")

        self.title_bar = TitleBar(self)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setWindowTitle("DokiDokiMangaDownloader")
        self.resize(550, 400)
        self.tabs = {"General": QtWidgets.QWidget(), "Manga Sites": QtWidgets.QWidget(), "Proxy": QtWidgets.QWidget(),
                     "Authentication": QtWidgets.QWidget(), "Updates": QtWidgets.QWidget(),
                     "Images": QtWidgets.QWidget(), "Download": QtWidgets.QWidget(), "1": QtWidgets.QWidget(),
                     "2": QtWidgets.QWidget(), "3": QtWidgets.QWidget()}

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.title_bar)

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
