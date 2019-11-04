from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit, QColorDialog, QCheckBox, QInputDialog, QStackedWidget
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
        if useStyle:
            self.changeStyle()

    def changeStyle(self):
        if self.useStyle:
            self.setStyleSheet(f'''
                QPushButton, QComboBox {{color: {prefs.get_pref('txt_color') if not None else '#000000'};}}
                QLabel {{color: {prefs.get_pref('lbl_color') if not None else '#ffffff'};}}
                QWidget#Reports, QWidget#Preferences {{background: {prefs.get_pref('bg_color') if not None else '#000080'};}}
                QTableWidget {{background:{prefs.get_pref('bg_color') if not None else '000080'};}}
            ''')

app = Application("Report Card Generator", useStyle=True)

class Window(QWidget):
    def __init__(self, name, x, y, w, h, shown=False):
        super(Window, self).__init__()
        self.setWindowTitle(name)
        self.setGeometry(x, y, w, h)
        self.setFixedSize(self.size())
        self.setObjectName(name)
        self.setUI(bg_color=prefs.get_pref('bg_color') if not None else "#000080", txt_color=prefs.get_pref('txt_color') if not None else "#ffffff")
        self.shown = shown
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

screens = {
    "Reports":Window("Reports", 0, 0, 1000, 750, True),
    "Preferences":Window("Preferences", 0, 0, 1000, 750, False),
    "Grades":Window("Grades", 0, 0, 1000, 750, False)
}

def switch_screen(to):
    if not to in screens:
        return
    else:
        if not screens[to].shown:
            for screen in screens:
                if not screen == to:
                    screens[screen].shown = False
                    screens[screen].hide()
                else:
                    screens[screen].shown = True
                    screens[screen].show()



# screen_handler = QStackedWidget()
# for scr in screens.values(): screen_handler.addWidget(scr)
# screen_handler.setCurrentIndex(0)

class Button(QPushButton):
    def __init__(self, screen, text, x, y, focusOnTab=True):
        if screen in screens:
            self.screen = screen
            super(Button, self).__init__(screens[screen])
        else:
            self.screen = None
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
    def __init__(self, screen, text, x, y, visible=True):
        if screen in screens:
            self.screen = screen
            super(Label, self).__init__(screens[screen])
        else:
            self.screen = None

        self.setText(text)
        self.move(x, y)
        self.setupFont()
        if visible: self.show()

    def setupFont(self, size=24, font_family="Arial"):
        self.setFont(QFont(font_family, size, QFont.Bold))

class Input(QLineEdit):
    def __init__(self, screen, x, y):
        if screen in screens:
            self.screen = screen
            super(Input, self).__init__(screens[screen])
        else:
            self.screen = None
        self.move(x, y)
        self.show()

class Dropdown(QComboBox):
    def __init__(self, screen, x, y, options, focusOnTab=True):
        if screen in screens:
            self.screen = screen
            super(Dropdown, self).__init__(screens[screen])
        else:
            self.screen = None
        self.move(x, y)
        if focusOnTab:
            self.setFocusPolicy(Qt.StrongFocus)
        else:
            self.setFocusPolicy(Qt.ClickFocus)
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
    def __init__(self, screen, content, x, y, w, h):
        if screen in screens:
            self.screen = screen
            super(Textarea, self).__init__(screens[screen])
        else:
            self.screen = None
        self.setGeometry(x, y, w, h)
        self.setText(content)
        self.setTabChangesFocus(True)
        self.show()

class Checkbox(QCheckBox):
    def __init__(self, screen, x, y, ):
        if screen in screens:
            self.screen = screen
            super(Checkbox, self).__init__(screens[screen])
        else:
            self.screen = None
        self.setChecked(True)
        self.setCheckable(True)
        self.move(x, y)
        self.show()

class ColorSelector(QColorDialog):
    def __init__(self, screen, corresponds=None):
        if screen in screens:
            self.screen = screen
            super(ColorSelector, self).__init__(screens[screen])
        else:
            self.screen = None
        self.corresponds = corresponds

    def updateColor(self, title, color_pref):
        color = QColorDialog.getColor(title=title)
        if color.isValid() and prefs.has_pref(color_pref):
            prefs.update_pref(color_pref, color.name())
            QApplication.instance().changeStyle()

