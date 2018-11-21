import sqlite3
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QTabWidget, QAction, QMessageBox, QSplashScreen, QDesktopWidget

from LOLByTencent import LOLSpider
from MyDB import check_db
from MyUI import MyMainWindow, MyProgressDialog, make_tab


class MyGUI(MyMainWindow):
    def __init__(self, cursor_: sqlite3.Cursor):
        self.app = QApplication(sys.argv)
        super(MyGUI, self).__init__()
        self.tab = QTabWidget()
        self.cursor = cursor_
        self.setWindowTitle("LOL")
        self.setWindowIcon(QIcon("logo.png"))
        self.make_menu()
        self.setCentralWidget(self.tab)
        self.main()

    def update_(self, type_update):
        if type_update == 1:
            reply = QMessageBox.warning(self, "提示", "本操作需要火狐(Firefox)浏览器支持,请确保已安装火狐浏览器!",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        d = MyProgressDialog(self)
        spider = LOLSpider()
        d.execute(spider, type_update)

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
        update_action = QAction('&更新(慢)', self)
        update_action.setShortcut('Ctrl+U')
        update_action.setToolTip('更新数据(慢)')
        update_action.triggered.connect(lambda: self.update_(0))

        update_action_ = QAction('&更新(快)', self)
        update_action_.setShortcut('Ctrl+F')
        update_action_.setToolTip('更新数据(快)')
        update_action_.triggered.connect(lambda: self.update_(1))

        exit_action = QAction('&退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setToolTip('退出程序')
        exit_action.triggered.connect(self.close)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(update_action)
        file_menu.addAction(update_action_)
        file_menu.addAction(exit_action)

    def main(self):
        splash = QSplashScreen(QPixmap("loading.png"))
        splash.showMessage('启动中...', QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        splash.show()
        QtWidgets.qApp.processEvents()
        check_db(self.cursor)

        self.refresh_tab()

        self.show()
        splash.finish(self)
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    conn = sqlite3.connect("lol.db")
    cursor = conn.cursor()
    MyGUI(cursor)
    cursor.close()
    conn.close()
