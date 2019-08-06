from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit
from PyQt5.QtCore import Qt, QEvent
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
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            exit()


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
        self.show()

class Input(QLineEdit):
    def __init__(self, window, x, y):
        super(Input, self).__init__(window)
        self.move(x, y)
        self.show()

class Dropdown(QComboBox):
    def __init__(self, window, x, y, options):
        super(Dropdown, self).__init__(window)
        self.move(x, y)
        self.addItems(options)
        self.show()

class Textarea(QTextEdit):
    def __init__(self, window, content, x, y, w, h):
        super(Textarea, self).__init__(window)
        self.setGeometry(x, y, w, h)
        self.setText(content)
        self.show()
