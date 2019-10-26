from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit, QColorDialog, QCheckBox, QInputDialog
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QPalette, QFont

from sys import exit
import os
import json

from preferences import prefs

class Application(QApplication):
    def __init__(self, name, useStyle):
        super(Application, self).__init__([])
        self.setApplicationName(name)
        self.useStyle = useStyle
        self.setupStyles()
        if useStyle:
            self.changeStyle()

    def setupStyles(self):
        pass
        # self.setStyleSheet(f'''
        #     QComboBox {{
        #         max-width: 200px;
        #     }}
        # ''')

    def changeStyle(self):
        if self.useStyle:
            self.setStyleSheet(f'''
                QPushButton, QComboBox {{color: {prefs.get_pref('txt_color') if not None else '#000000'};}}
                QLabel {{color: {prefs.get_pref('lbl_color') if not None else '#ffffff'};}}
                QWidget#appWindow {{background: {prefs.get_pref('bg_color') if not None else '#000080'};}}
            ''')


class Window(QWidget):
    def __init__(self, name, x, y, w, h, shown=False):
        super(Window, self).__init__()
        self.setWindowTitle(name)
        self.setGeometry(x, y, w, h)
        self.setFixedSize(self.size())
        self.setUI(bg_color=prefs.get_pref('bg_color') if not None else "#000080", txt_color=prefs.get_pref('txt_color') if not None else "#ffffff")
        # self.setUnifiedTitleAndToolBarOnMac(True)
        if shown:
            self.show()


    def setUI(self, bg_color=None, txt_color=None):
        palette = self.palette()
        if bg_color:
            self.autoFillBackground()
            background_color = QColor()
            background_color.setNamedColor(bg_color)
            palette.setColor(QPalette.Background, background_color)
        if txt_color:
            text_color = QColor()
            text_color.setNamedColor(txt_color)
            palette.setColor(QPalette.Text, text_color)
            palette.setColor(QPalette.WindowText, text_color)
            palette.setColor(QPalette.ButtonText, text_color)
        self.setPalette(palette)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            exit()

class Button(QPushButton):
    def __init__(self, window, text, x, y, focusOnTab=True):
        super(Button, self).__init__(window)
        self.setText(text)
        self.move(x, y)
        self.show()
        if focusOnTab:
            self.setFocusPolicy(Qt.StrongFocus)
        else:
            self.setFocusPolicy(Qt.ClickFocus)

    def keyPressEvent(self, event) -> None:
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.click()

        if event.key() == Qt.Key_Escape:
            exit()

class Label(QLabel):
    def __init__(self, window, text, x, y):
        super(Label, self).__init__(window)
        self.setText(text)
        self.move(x, y)
        self.setupFont()
        self.show()

    def setupFont(self, size=24, font_family="Arial"):
        self.setFont(QFont(font_family, size, QFont.Bold))

class Input(QLineEdit):
    def __init__(self, window, x, y):
        super(Input, self).__init__(window)
        self.move(x, y)
        self.show()

class Dropdown(QComboBox):
    def __init__(self, window, x, y, options):
        super(Dropdown, self).__init__(window)
        self.move(x, y)
        self.setFocusPolicy(Qt.StrongFocus)
        self.addItems(options)
        self.lastSelected = " "
        self.history = [" "]
        self.setMaximumWidth(650)
        self.show()

    def keyPressEvent(self, event) -> None:
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.showPopup()
        if event.key() == Qt.Key_Escape:
            exit()


class Textarea(QTextEdit):
    def __init__(self, window, content, x, y, w, h):
        super(Textarea, self).__init__(window)
        self.setGeometry(x, y, w, h)
        self.setText(content)
        self.setTabChangesFocus(True)
        self.show()

class Checkbox(QCheckBox):
    def __init__(self, window, x, y):
        super(Checkbox, self).__init__(window)
        self.setChecked(True)
        self.setCheckable(True)
        self.move(x, y)
        self.show()

class ColorSelector(QColorDialog):
    def __init__(self, window, corresponds=None):
        super(ColorSelector, self).__init__(window)
        self.corresponds = corresponds

    def updateColor(self, title, color_pref):
        #pretty sure title ain't working, idk why
        color = QColorDialog.getColor(title=title)
        if color.isValid() and prefs.has_pref(color_pref):
            prefs.update_pref(color_pref, color.name())
            QApplication.instance().changeStyle()
