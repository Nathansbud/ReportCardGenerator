from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QPalette, QFont, QFocusEvent

from sys import exit

class Application(QApplication):
    def __init__(self, name):
        super(Application, self).__init__([])
        self.setApplicationName(name)

class Window(QWidget):
    def __init__(self, name, x, y, w, h):
        super(Window, self).__init__()
        self.setWindowTitle(name)
        self.setGeometry(x, y, w, h)
        self.setFixedSize(self.size())
        self.setUI(bg_color="#450000")

        self.show()

    def setUI(self, bg_color=None, text_color=None):
        palette = self.palette()
        if bg_color:
            self.autoFillBackground()
            background_color = QColor()
            background_color.setNamedColor(bg_color)
            palette.setColor(QPalette.Background, background_color)
        if text_color:
            text_color = QColor()
            text_color.setNamedColor(text_color)
            palette.setColor(QPalette.Text, text_color)

        self.setPalette(palette)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            exit()
        # if event.key() == Qt.Key_Tab:
        #     print(self.focusWidget())

class Button(QPushButton):
    def __init__(self, window, text, x, y):
        super(Button, self).__init__(window)
        self.setText(text)
        self.move(x, y)
        self.show()

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
        self.show()

    def keyPressEvent(self, event) -> None:
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.showPopup()

class Textarea(QTextEdit):
    def __init__(self, window, content, x, y, w, h):
        super(Textarea, self).__init__(window)
        self.setGeometry(x, y, w, h)
        self.setText(content)
        self.show()
