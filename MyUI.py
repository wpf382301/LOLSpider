import threading
from abc import ABCMeta, abstractmethod

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QBasicTimer, QSize, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QCloseEvent, QFocusEvent, QColor
from PyQt5.QtWidgets import QProgressBar, QMessageBox, QDialog, QVBoxLayout, QTabWidget, QTabBar, QLabel, QWidget, \
    QMainWindow, QDesktopWidget, QGridLayout, QHBoxLayout, QRadioButton, QScrollArea, QLineEdit


def skin_detail_tab(cursor_, name):
    from MyDB import find_hero_skin
    result = find_hero_skin(name, cursor_)
    tab = MyTabWidget()
    for i in range(0, len(result)):
        skin_label = MyLabel(full_able=True, full_img_dir=result[i][2], full_skin_name=result[i][1])
        img = QPixmap(result[i][2], format="0").scaled(980, 500)
        skin_label.setPixmap(img)
        tab.addTab(skin_label, result[i][1])

    # tab.setTabShape(QTabWidget.TabShape(0))
    # tab.setDocumentMode(True)
    return tab


def skill_detail_tab(cursor_, name):
    from MyDB import find_hero_skill
    result = find_hero_skill(name, cursor_)

    tab = QTabWidget()
    tab.setIconSize(QSize(64, 64))
    for i in range(1, 6):
        skill_item = QVBoxLayout()
        skill_name = QLabel()
        text_t = '<font size="5"><b>' + result[i] + '</b></font> '
        if i == 1:
            text_t = text_t + ' <font color="grey">快捷键：Q</font>'
        elif i == 2:
            text_t = text_t + ' <font color="grey">快捷键：W</font>'
        elif i == 3:
            text_t = text_t + ' <font color="grey">快捷键：E</font>'
        elif i == 4:
            text_t = text_t + ' <font color="grey">快捷键：R</font>'
        else:
            text_t = text_t + ' <font color="grey">被动技能</font>'
        skill_name.setText(text_t)
        skill_item.addWidget(skill_name)
        skill_desc = QLabel()
        skill_desc.setAlignment(QtCore.Qt.AlignLeft)
        skill_desc.setWordWrap(True)
        skill_desc.setText(result[i + 10])
        skill_item.addWidget(skill_desc)

        data_ = result[i + 15]
        if data_:
            data = data_.split(",")
            for _ in data:
                skill_data = QLabel()
                skill_data.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignLeft)
                skill_data.setText(_)
                skill_item.addWidget(skill_data)

        w = QWidget()
        w.setLayout(skill_item)
        icon = QIcon(result[i + 5])
        tab.addTab(w, icon, "")

    return tab


def make_tab(flag, cursor_):
    top_layout = QVBoxLayout()
    top_layout.setAlignment(QtCore.Qt.AlignTop)
    content_widget = QWidget()
    content_layout = QGridLayout()
    content_layout.setSpacing(10)
    content_widget.setLayout(content_layout)
    type_search_layout = QHBoxLayout()
    type_search_layout.setAlignment(QtCore.Qt.AlignTop)
    type_search_widget = QWidget()
    type_search_widget.setLayout(type_search_layout)
    type_layout = QHBoxLayout()
    type_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    type_widget = QWidget()
    type_widget.setLayout(type_layout)
    if flag == 1:
        radio_0 = MyRadioButton(cursor_, "所有", "hero", "", top_layout)
        radio_1 = MyRadioButton(cursor_, "战士", "hero", "战士", top_layout)
        radio_2 = MyRadioButton(cursor_, "法师", "hero", "法师", top_layout)
        radio_3 = MyRadioButton(cursor_, "刺客", "hero", "刺客", top_layout)
        radio_4 = MyRadioButton(cursor_, "坦克", "hero", "坦克", top_layout)
        radio_5 = MyRadioButton(cursor_, "射手", "hero", "射手", top_layout)
        radio_6 = MyRadioButton(cursor_, "辅助", "hero", "辅助", top_layout)
        search_box = MyLineEdit(cursor=cursor_, table="hero", value="*",  key="name", top_layout=top_layout)
        search_box.setPlaceholderText("搜索")
        type_layout.addWidget(radio_0)
        type_layout.addWidget(radio_1)
        type_layout.addWidget(radio_2)
        type_layout.addWidget(radio_3)
        type_layout.addWidget(radio_4)
        type_layout.addWidget(radio_5)
        type_layout.addWidget(radio_6)
    else:
        radio_0 = MyRadioButton(cursor_, "所有", "equipment", "", top_layout)
        radio_1 = MyRadioButton(cursor_, "防御类", "equipment", "", top_layout)
        radio_2 = MyRadioButton(cursor_, "攻击类", "equipment", "", top_layout)
        radio_3 = MyRadioButton(cursor_, "法术类", "equipment", "", top_layout)
        radio_4 = MyRadioButton(cursor_, "移动速度", "equipment", "", top_layout)
        radio_5 = MyRadioButton(cursor_, "消耗品", "equipment", "", top_layout)
        search_box = MyLineEdit(cursor=cursor_, table="equipment", value="*", key="name", top_layout=top_layout)
        search_box.setPlaceholderText("搜索")
        type_layout.addWidget(radio_0)
        type_layout.addWidget(radio_1)
        type_layout.addWidget(radio_2)
        type_layout.addWidget(radio_3)
        type_layout.addWidget(radio_4)
        type_layout.addWidget(radio_5)

    type_search_layout.addWidget(type_widget, alignment=QtCore.Qt.AlignLeft)
    type_search_layout.addWidget(search_box, alignment=QtCore.Qt.AlignRight)
    top_layout.addWidget(type_search_widget)
    top_layout.addWidget(content_widget)
    w = QWidget()
    w.setLayout(top_layout)
    radio_0.setChecked(True)
    radio_0.focusInEvent(QFocusEvent(QtCore.QEvent.FocusIn))

    scroll = QScrollArea()
    scroll.setWidget(w)
    scroll.setAutoFillBackground(True)
    scroll.setWidgetResizable(True)
    scroll.resize(w.width() + 20, int(w.width() / 4 * 3))

    return scroll


def make_content_widget(cursor, table, key_word, fuzzy=False, key: str=None, value: str=None):
    if fuzzy and key:
        from MyDB import fuzzy_search
        result = fuzzy_search(cursor, value, table, key, key_word)
    else:
        from MyDB import find_type
        result = find_type(table, key_word, cursor)
    content_widget = QWidget()
    content_layout = QGridLayout()
    content_widget.setLayout(content_layout)
    if result:
        for i in range(0, len(result)):
            item_widget = QWidget()
            item_layout = QVBoxLayout()
            item_widget.setLayout(item_layout)
            if table == "hero":
                imglabel = MyLabel(cursor_=cursor, hero_name=result[i][0], hero_profile=result[i][-1])
                img = QPixmap(result[i][-1], format="0").scaled(60, 60)
                imglabel.setPixmap(img)
                textlabel = QLabel(result[i][0])
                tip = "名称:{}<br/>位置:{}<br/>物理攻击:{}<br/>魔法攻击:{}<br/>防御能力:{}<br/>上手难度:{}".format(
                    result[i][0],
                    result[i][1],
                    result[i][2],
                    result[i][3],
                    result[i][4],
                    result[i][5]
                )
                imglabel.setToolTip(tip)
            else:
                imglabel = MyLabel(equipment=result[i], cursor_=cursor)
                img = QPixmap(result[i][-1], format="0").scaled(60, 60)
                imglabel.setPixmap(img)
                textlabel = QLabel(result[i][1])
            item_layout.addWidget(imglabel, alignment=QtCore.Qt.AlignCenter)
            item_layout.addWidget(textlabel, alignment=QtCore.Qt.AlignCenter)
            content_layout.addWidget(item_widget, int(i / 10), int(i % 10))
        if len(result) <= 10:
            content_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

    return content_widget


class MyLabel(QLabel):
    def __init__(self, parent: QWidget = None, cursor_=None, hero_name=None, hero_profile=None, equipment: list = None,
                 full_able=False, full_img_dir=None, full_skin_name=None):
        super(MyLabel, self).__init__(parent)
        self.parent = parent
        self.cursor = cursor_
        self.hero_name = hero_name
        self.hero_profile = hero_profile
        self.equipment = equipment
        if self.equipment:
            self.setMouseTracking(True)
        self.equipment_detail_widget = None
        self.full_able = full_able
        if self.full_able:
            self.setToolTip("双击显示大图")
        self.full_img_dir = full_img_dir
        self.full_skin_name = full_skin_name

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        """
        button = ev.button()\n
        button = 1 when LEFT CLICK\n
        button = 2 when RIGHT CLICK\n
        :param ev:
        :return:
        """
        if self.hero_name and ev.button() == 1:
            d = MyHeroDetailDialog(cursor_=self.cursor, hero_name=self.hero_name, hero_profile=self.hero_profile)
            d.exec_()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent):
        if self.equipment:
            if not self.equipment_detail_widget:
                self.equipment_detail_widget = QWidget(self)
                self.equipment_detail_widget.setWindowFlags(QtCore.Qt.ToolTip)
                # 背景颜色
                palette = QtGui.QPalette()
                palette.setColor(self.equipment_detail_widget.backgroundRole(), QColor(0, 0, 0))
                self.equipment_detail_widget.setPalette(palette)
                self.equipment_detail_widget.setWindowOpacity(0.8)  # 透明度
                item = QGridLayout()
                self.equipment_detail_widget.setLayout(item)
                imglabel = QLabel()
                img = QPixmap(self.equipment[-1], format="0").scaled(60, 60)
                imglabel.setPixmap(img)
                textlabel = QLabel(
                    '<h3><b><font color="#54FF00">{}</font></b></h3><font color="#CA9033">售价或合成费用：{}</font>'.format(
                        self.equipment[1],
                        self.equipment[2]
                    )
                )
                textlabel.setAlignment(QtCore.Qt.AlignLeft)
                desc = ""
                for i in range(3, len(self.equipment) - 3):
                    if self.equipment[i]:
                        t_ = self.equipment[i].split(",")
                        for _ in t_:
                            desc = desc + "<br/>" + _
                desc = '<font color="#B0DDFF">' + desc + '</font>'
                desc_label = QLabel(desc)
                desc_label.setWordWrap(True)

                tree_widget = None
                if self.cursor:
                    r = [[str(self.equipment[0])]]
                    from MyDB import find_
                    find_(self.cursor, r[0][0], 1, r)
                    deep = len(r)
                    t = False
                    for i in r[len(r) - 1]:
                        if i:
                            t = True
                    if not t:
                        deep = deep - 1
                        del r[deep]
                    if r and len(r) > 1:
                        tree_widget = QWidget()
                        tree_layout = QVBoxLayout()
                        tree_widget.setLayout(tree_layout)
                        for i in r:
                            t_layout = QHBoxLayout()
                            t_layout.setAlignment(QtCore.Qt.AlignHCenter)
                            for j in i:
                                s = j.split(",")
                                for k in s:
                                    equipment_img = QPixmap("equipments\\{}.png".format(k), format="0").scaled(20, 20)
                                    equipment_label = QLabel()
                                    equipment_label.setPixmap(equipment_img)
                                    t_layout.addWidget(equipment_label)
                            tree_layout.addLayout(t_layout)

                item.addWidget(imglabel, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
                item.addWidget(textlabel, 0, 1, 1, 2, QtCore.Qt.AlignLeft)
                item.addWidget(desc_label, 1, 0, 1, 3, QtCore.Qt.AlignLeft)
                if tree_widget:
                    item.addWidget(tree_widget, 2, 0, 1, 3, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            x = ev.globalX() + 20
            y = ev.globalY() + 20
            point_in_window = ev.windowPos().toPoint()
            if point_in_window.x() + self.equipment_detail_widget.width() > self.window().width():
                x = ev.globalX() - self.equipment_detail_widget.width() - 10
            if point_in_window.y() + self.equipment_detail_widget.height() > self.window().height():
                y = ev.globalY() - self.equipment_detail_widget.height() - 10
            self.equipment_detail_widget.move(x, y)
            self.equipment_detail_widget.show()

    def leaveEvent(self, a0: QtCore.QEvent):
        if self.equipment_detail_widget and isinstance(self.equipment_detail_widget, QWidget):
            self.equipment_detail_widget.close()

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent):
        if self.full_able:
            t_d = QDialog()
            t_d.setWindowTitle(self.full_skin_name)
            t_d.setWindowIcon(QIcon(self.full_img_dir))
            t_l = QHBoxLayout()
            t_q = QLabel()
            t_q.setPixmap(
                QPixmap(self.full_img_dir, format="0").scaled(QDesktopWidget().availableGeometry().width() - 50,
                                                              QDesktopWidget().availableGeometry().height() - 50))
            t_l.addWidget(t_q)
            t_d.setLayout(t_l)
            t_d.exec_()


class MyHeroDetailDialog(QDialog):
    def __init__(self, cursor_=None, hero_name=None, hero_profile=None):
        super(MyHeroDetailDialog, self).__init__()
        self.cursor = cursor_
        self.hero_name = hero_name
        self.hero_profile = hero_profile
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        if self.hero_name:
            self.setWindowTitle(self.hero_name)
            if self.cursor:
                layout.addWidget(skin_detail_tab(self.cursor, self.hero_name))
                layout.addWidget(skill_detail_tab(self.cursor, self.hero_name))
        if self.hero_profile:
            self.setWindowIcon(QIcon(self.hero_profile))


class MyTabBar(QTabBar):
    def __init__(self):
        super(MyTabBar, self).__init__()

    def wheelEvent(self, event: QtGui.QWheelEvent):
        angle = event.angleDelta().y()
        tab_count = self.count() - 1
        current_index = self.currentIndex()
        if angle >= 120:
            if current_index > 0:
                self.setCurrentIndex(current_index - 1)
        elif angle <= -120:
            if current_index < tab_count:
                self.setCurrentIndex(current_index + 1)


class MyTabWidget(QTabWidget):
    def __init__(self):
        super(MyTabWidget, self).__init__()
        self.setTabBar(MyTabBar())

    def wheelEvent(self, a0: QtGui.QWheelEvent):
        angle = a0.angleDelta().y()
        tab_count = self.count() - 1
        current_index = self.currentIndex()
        if angle >= 120:
            if current_index > 0:
                self.setCurrentIndex(current_index - 1)
        elif angle <= -120:
            if current_index < tab_count:
                self.setCurrentIndex(current_index + 1)


class MyRadioButton(QRadioButton):
    def __init__(self, cursor_, s, table, tag, top_layout: QVBoxLayout):
        super(MyRadioButton, self).__init__(s)
        self.table = table
        self.tag = tag
        self.top_layout = top_layout
        self.cursor = cursor_

    def focusInEvent(self, e: QtGui.QFocusEvent):
        if not self.top_layout and not self.cursor:
            return
        content_widget_old = self.top_layout.itemAt(1).widget()
        content_widget_new = make_content_widget(self.cursor, self.table, self.tag)
        content_widget_old.close()
        self.top_layout.replaceWidget(content_widget_old, content_widget_new)


class ProgressBar(QtWidgets.QWidget):
    def __init__(self, root_widget=None):
        QtWidgets.QWidget.__init__(self)

        self.setGeometry(300, 300, 250, 120)
        self.pbar = QProgressBar(self)
        self.pbar.setMaximum(100)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.timer = QBasicTimer()
        self.step = 0
        self.root_widget = root_widget

    def timerEvent(self, event):
        if self.step < 0:
            self.timer.stop()
            if self.step == -1:
                self.onError()
            if self.step == -2:
                self.onCancle()
        if self.step >= 100:
            self.timer.stop()
            self.pbar.setValue(100)
            self.onSuccess()
        self.pbar.setValue(self.step)

    def onStart(self):
        self.timer.start(100, self)

    def onCancle(self):
        if isinstance(self.root_widget, MyProgressDialog):
            self.root_widget.cancle()

    def onError(self):
        if self.root_widget:
            QMessageBox.warning(self.root_widget, "提示", "更新失败!")
            if isinstance(self.root_widget, MyProgressDialog) and isinstance(self.root_widget.root, MyMainWindow):
                self.root_widget.root.refresh_tab()
            self.root_widget.close()

    def onSuccess(self):
        if self.root_widget:
            QMessageBox.information(self.root_widget, "提示", "更新成功!")
            if isinstance(self.root_widget, MyProgressDialog) and isinstance(self.root_widget.root, MyMainWindow):
                self.root_widget.root.refresh_tab()
            self.root_widget.close()


class MyProgressDialog(QDialog):
    def __init__(self, root):
        super(MyProgressDialog, self).__init__()
        self.root = root
        self.setWindowTitle("更新")
        self.setWindowIcon(QIcon("logo.png"))
        self.progressbar = ProgressBar(root_widget=self)
        self.thread = None
        self.target = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.progressbar)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setFixedSize(self.progressbar.width(), self.progressbar.height())

    def execute(self, target, type_update):
        self.progressbar.onStart()
        self.target = target
        self.thread = threading.Thread(target=target.main_external, args=(self.progressbar, type_update))
        self.thread.start()
        self.show()

    def cancle(self):
        if isinstance(self.root, MyMainWindow):
            self.root.refresh_tab()

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.close()
        if self.thread and self.thread.is_alive() and self.target:
            self.target.stop()


class MyLineEdit(QLineEdit):
    def __init__(self, parent=None, cursor=None, value=None, table=None, key=None, top_layout=None):
        super(MyLineEdit, self).__init__(parent)
        self.setFixedWidth(200)
        self.cursor = cursor
        self.value = value
        self.table = table
        self.key = key
        self.top_layout = top_layout
        self.textChanged[str].connect(self.onTextChanged)

    def onTextChanged(self, a0: str):
        if self.cursor and self.table and self.value and self.key and self.top_layout:
            content_widget_old = self.top_layout.itemAt(1).widget()
            content_widget_old.close()
            content_widget_new = make_content_widget(self.cursor, self.table, a0, True, self.key, self.value)
            self.top_layout.replaceWidget(content_widget_old, content_widget_new)


class MyMainWindow(QMainWindow):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(MyMainWindow, self).__init__()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(QPoint(cp.x(), cp.y() - 19))
        self.move(qr.topLeft())

    def closeEvent(self, a0: QCloseEvent):
        reply = QMessageBox.question(self, "LOL", "退出程序?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            a0.accept()
        else:
            a0.ignore()

    @abstractmethod
    def refresh_tab(self):
        pass
