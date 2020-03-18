from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QComboBox, QTextEdit, QColorDialog, QCheckBox,\
    QTableWidget, QTableWidgetItem, QHeaderView, QShortcut, QProgressDialog, QMainWindow, QDialog, QFormLayout, QDialogButtonBox,\
    QLineEdit, QGroupBox, QVBoxLayout
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if prefs.get_pref("debug"): exit()
        else:
            super(Window, self).keyPressEvent(event)

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
    def __init__(self, screen, text, x, y, focusOnTab=True, shown=True):
        if screen in screens:
            self.screen = screen
            super(Button, self).__init__(screens[screen])
        else:
            self.screen = None
        self.setText(text)
        self.move(x, y)

        if shown: self.show()
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
    def __init__(self, screen, text, x, y, shown=True):
        if screen in screens:
            self.screen = screen
            super(Label, self).__init__(screens[screen])
        else:
            self.screen = None

        self.setText(text)
        self.move(x, y)
        self.setupFont()
        if shown: self.show()

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
        #Good idea in theory, but...not in actuality, since I use like 0 layouts so nothing is adjusted
        # self.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.show()

    def keyPressEvent(self, event) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.showPopup()
        else:
            super(Dropdown, self).keyPressEvent(event)

    def modifyText(self, text):
        if self.count() == 0: self.addItem(text)
        if text: self.setItemText(self.currentIndex(), text)

class Table(QTableWidget):
    def __init__(self, screen, header=None, data=None, x=None, y=None, w=None, h=None, locked=None, changed=None, shown=True, accepted=None, custom_change=False):
        if screen in screens:
            self.screen = screen
            super(Table, self).__init__(len(data) if data else 0, len(data[0]) if data else 0, screens[screen])
        else:
            self.screen = None
        self.header = header
        self.locked = locked
        self.setHorizontalHeaderLabels(self.header)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.accepted = accepted #should be dict in form {"HeaderName":{"whitelist":["value1", "value2"] &| "blacklist":["value1", "value2"]}
        self.data = data
        self.changed = changed
        self.cellClicked.connect(self.cellOpened)
        if not custom_change: self.itemChanged.connect(self.validate)
        self.oldText = ""
        self.oldCell = ()
        self.setGeometry(x, y, w, h)
        self.move(x, y)
        if shown: self.show()

    def cellOpened(self, row, column):
        self.oldText = self.item(row, column).text() if self.item(row, column) else ""
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
                    if self.locked and self.horizontalHeaderItem(col).text() in self.locked: item.setFlags(Qt.ItemIsEnabled)
                    self.setItem(row, col, item)
        self.setHorizontalHeaderLabels(self.header)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.repaint()
        app.changeStyle()

    def keyPressEvent(self, event):
        row, column = self.currentRow(), self.currentColumn()
        if row == self.rowCount() - 1 and column == self.columnCount() - 1 and event.key() == Qt.Key_Tab:
            self.insertRow(self.rowCount() - 1)
        else:
            super().keyPressEvent(event)

    def validate(self, item):
        if self.oldCell != (item.row(), item.column()): self.oldText = ""
        row = item.row()
        column = item.column()
        horizontal_header = self.horizontalHeaderItem(column)
        vertical_header = self.verticalHeaderItem(row)
        if horizontal_header is not None and isinstance(self.accepted, dict) and horizontal_header.text() in self.accepted:
            if 'whitelist' in self.accepted[horizontal_header.text()]:
                if not item.text() in self.accepted[horizontal_header.text()]['whitelist']:
                    item.setText(self.oldText)
            if 'blacklist' in self.accepted[horizontal_header.text()]:
                if item.text() in self.accepted[horizontal_header.text()]['blacklist']:
                    item.setText(self.oldText)
            self.oldText = item.text()

        #credit https://stackoverflow.com/questions/21280061/get-data-from-every-cell-from-a-qtableview
        model = self.model()
        self.data = []
        for row in range(model.rowCount()):
            self.data.append([])
            for column in range(model.columnCount()):
                index = model.index(row, column)
                self.data[row].append(str(model.data(index)))

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

#Layout stuff adapted from https://pythonspot.com/pyqt5-form-layout/; rest mine
class Multidialog(QDialog):
    def __init__(self, screen, title, form_set):

        if screen in screens:
            self.screen = screen
            super(Multidialog, self).__init__(screens[screen])
        else:
            self.screen = None

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.form_set = form_set
        self.elements = {}
        self.title = title
        self.setWindowTitle(self.title)
        self.main_layout = QVBoxLayout()
        self.group_box = QGroupBox()
        self.first_launch = True
        layout = QFormLayout()
        for f in self.form_set:
            if 'name' in f and 'label' in f and 'type' in f:
                self.elements[f['name']] = {'label':f['label'], 'type':f['type'], 'object':self.get_element(f['type'])}
                if 'options' in f:
                    self.elements[f['name']]['options'] = f['options']
                    if self.elements[f['type']] == 'dropdown': f['object'].addItems(f['options'])
            layout.addRow(f['label'], self.elements[f['name']]['object'])
        self.group_box.setLayout(layout)
        self.main_layout.addWidget(self.group_box)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

    def get_element(self, k):
        if k.lower() == "input": return QLineEdit()
        elif k.lower() == "dropdown": return QComboBox()

    def refresh(self):
        for w in self.group_box.children():
            if isinstance(w, QLineEdit): w.setText("")
            elif isinstance(w, QComboBox):
                if w.count() > 0: w.setCurrentIndex(0)




