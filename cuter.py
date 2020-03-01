from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QComboBox, QTextEdit, QColorDialog, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QShortcut
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QPalette, QFont, QBrush, QKeySequence, QTextCursor


from sys import exit
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

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Escape:
    #         exit()

screens = {
    "Reports":Window("Reports", 0, 0, 1000, 750, False),
    "Preferences":Window("Preferences", 0, 0, 1000, 750, False),
    "Grades":Window("Grades", 0, 0, 1000, 750, False),
    "Setup":Window("Sheet Setup", 0, 0, 1000, 750, True),
    "Builder":Window("Sheet Builder", 0, 0, 1000, 750, False),
    "Test":Window("Testing", 0, 0, 1000, 750, False)
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
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.click()
        else:
            super(Button, self).keyPressEvent(event)

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

class Dropdown(QComboBox):
    def __init__(self, screen, x, y, options, focusOnTab=True, editable=False):
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


        self.options = options
        self.addItems(options)
        self.lastSelected = " "
        self.history = [" "]
        self.setMaximumWidth(650)
        self.setEditable(editable)
        if self.isEditable():
            self.setInsertPolicy(QComboBox.InsertAtCurrent)
            self.editTextChanged.connect(self.modifyText)
        self.show()

    def keyPressEvent(self, event) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.showPopup()
        else:
            super(Dropdown, self).keyPressEvent(event)

    def modifyText(self, text):
        #idk how 2 do this
        # if self.isEditable():
        #     if len(self.options) == 0:
        #         self.options.append(text)
        #         self.setCurrentIndex(self.count()-1)
        #     else:
        #         index = self.currentIndex()
        #         self.options[self.currentIndex()] = text
        #         self.clear()
        #         self.addItems(self.options)
        #         self.setCurrentIndex(index)
        pass

class Table(QTableWidget):
    def __init__(self, screen, header=None, data=None, x=None, y=None, w=None, h=None, locked=None, changed=None):
        if screen in screens:
            self.screen = screen
            super(Table, self).__init__(len(data) if data else 0, len(data[0]) if data else 0, screens[screen])
        else:
            self.screen = None
        self.header = header
        self.locked = locked
        self.setHorizontalHeaderLabels(self.header)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.data = data
        self.changed = changed
        self.cellClicked.connect(self.cellOpened)
        self.oldText = None
        self.oldCell = ()
        self.setGeometry(x, y, w, h)
        self.move(x, y)
        self.show()

    def cellOpened(self, row, column):
        self.oldText = self.item(row, column).text()
        self.oldCell = (row, column)
        print(column, row, self.oldText)

    def updateTable(self, data=None):
        self.setRowCount(0)
        self.data = data
        self.setRowCount(len(data) if data is not None else 0)
        self.setColumnCount(len(data[0]) if data is not None and len(data) > 0 else 0)
        self.setHorizontalHeaderLabels(self.header)
        if self.data:
            for row in range(0, len(data)):
                for col in range(0, len(data[row])):
                    item = QTableWidgetItem(data[row][col])
                    item.setForeground(QBrush(QColor(255, 0, 0))) #there is no way to set table info via QSS

                    if self.horizontalHeaderItem(col).text() in self.locked: item.setFlags(Qt.ItemIsEnabled)
                    self.setItem(row, col, item)
        self.setHorizontalHeaderLabels(self.header)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.repaint()
        app.changeStyle()

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

        self.italic = QShortcut(QKeySequence("Ctrl+I"), self)
        self.italicActive = False

        self.bold = QShortcut(QKeySequence("Ctrl+B"), self)
        self.boldActive = False

        self.underline = QShortcut(QKeySequence("Ctrl+U"), self)
        self.underlineActive = False

        self.strikethrough = QShortcut(QKeySequence("Ctrl+L"), self)
        self.strikethroughActive = False

        self.italic.activated.connect(self.makeItalic)
        self.bold.activated.connect(self.makeBold)
        self.underline.activated.connect(self.makeUnderline)
        self.strikethrough.activated.connect(self.makeStrikethrough)
        self.show()

    def makeItalic(self):
        if self.isActiveWindow():
            start, end = self.textCursor().anchor(), self.textCursor().position()
            if (start - end) == 0:
                if not self.italicActive:
                    # self.insertHtml("<i>ITALICS")
                    print("Should in-place toggle italics")
                    self.italicActive = True
                else:
                    # self.setHtml(self.toHtml()[0:-13]+"</i>")
                    # self.moveCursor(QTextCursor.End)
                    print("Should in-place toggle off italics")
                    self.italicActive = False
            else:
                print("Should handle italics on region")
    def makeStrikethrough(self): print("Strikethrough: Unimplemented")
    def makeBold(self): print("Bold: Unimplemented")
    def makeUnderline(self): print("Underline: Unimplemented")

class Checkbox(QCheckBox):
    def __init__(self, screen, x, y):
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


