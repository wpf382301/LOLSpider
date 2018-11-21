import sqlite3
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QIcon, QCloseEvent
from PyQt5.QtWidgets import QApplication, QTabWidget, QAction, QSplashScreen, QDesktopWidget

from LOLByTencent import LOLSpider
from MyDB import check_db
from MyUI import MyMainWindow, MyProgressDialog, make_tab


class MyGUI(MyMainWindow):
    def __init__(self):
        self.app = QApplication(sys.argv)
        super(MyGUI, self).__init__()
        self.conn = sqlite3.connect("lol.db")
        self.cursor = self.conn.cursor()
        self.tab = QTabWidget()
        self.setWindowTitle("LOL")
        self.setWindowIcon(QIcon("logo.png"))
        self.make_menu()
        self.setCentralWidget(self.tab)
        self.main()

    def update_(self):
        d = MyProgressDialog(self)
        d.execute(LOLSpider())

    def refresh_tab(self):
        self.tab.clear()
        scroll_hero = make_tab(1, self.cursor)
        scroll_equipment = make_tab(2, self.cursor)
        self.tab.addTab(scroll_hero, "hero")
        self.tab.addTab(scroll_equipment, "equipment")
        width = scroll_hero.width() if scroll_hero.width() > scroll_equipment.width() else scroll_equipment.width()
        screen_height = QDesktopWidget().availableGeometry().height()
        height = screen_height if screen_height < width / 4 * 3 else width / 4 * 3
        self.tab.resize(width + 10, height - 38)
        self.resize(self.tab.width(), self.tab.height())
        self.center()

    def make_menu(self):
        update_action = QAction('&更新', self)
        update_action.setShortcut('Ctrl+U')
        update_action.setToolTip('更新数据')
        update_action.triggered.connect(lambda: self.update_())

        exit_action = QAction('&退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setToolTip('退出程序')
        exit_action.triggered.connect(self.close)

        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(update_action)
        file_menu.addAction(exit_action)

    def load_data(self):
        check_db(self.cursor)
        self.refresh_tab()

    def closeEvent(self, a0: QCloseEvent):
        super().closeEvent(a0)
        self.cursor.close()
        self.conn.close()

    def main(self):
        splash = QSplashScreen(QPixmap("loading.png"))
        splash.showMessage('启动中...', QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        splash.show()
        QtWidgets.qApp.processEvents()

        self.load_data()
        self.show()
        splash.finish(self)

        sys.exit(self.app.exec_())


if __name__ == '__main__':
    MyGUI()
