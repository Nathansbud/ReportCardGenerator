from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QStackedWidget, QPushButton, QLineEdit, QComboBox, QTextEdit, QListWidget, QColorDialog, QCheckBox
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QPalette, QFont, QFocusEvent

from sys import exit
import os
import json

with open(os.path.join(os.path.dirname(__file__), "prefs" + os.sep + "config.json")) as jf:
    prefs = json.load(jf)

class Application(QApplication):
    def __init__(self, name):
        super(Application, self).__init__([])
        self.setApplicationName(name)

class Window(QWidget):
    def __init__(self, name, x, y, w, h, shown=False):
        super(Window, self).__init__()
        self.setWindowTitle(name)
        self.setGeometry(x, y, w, h)
        self.setFixedSize(self.size())
        self.setUI(bg_color=prefs['bg_color'])
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
        self.setPalette(palette)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            exit()

class Button(QPushButton):
    def __init__(self, window, text, x, y):
        super(Button, self).__init__(window)
        self.setText(text)
        self.move(x, y)
        self.show()
        self.setFocusPolicy(Qt.StrongFocus)

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
        self.setColor(prefs['text_color'])

    def setColor(self, color):
        palette = self.palette()
        text_color = QColor()
        text_color.setNamedColor(color)
        palette.setColor(QPalette.WindowText, text_color)
        self.setPalette(palette)

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
        self.move(x, y)
        self.show()

class ColorSelector(QColorDialog):
    def __init__(self, window, corresponds):
        super(ColorSelector, self).__init__(window)
        self.corresponds = corresponds

    def openColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            if self.corresponds == "BG":
                self.parentWidget().setUI(bg_color=color.name())
            elif self.corresponds == "TXT":
                self.parentWidget().setUI(text_color=color.name())
