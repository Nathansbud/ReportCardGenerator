from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QComboBox, QTextEdit, QColorDialog, QCheckBox,\
    QTableWidget, QTableWidgetItem, QHeaderView, QShortcut, QProgressDialog, QMainWindow, QDialog, QFormLayout, QDialogButtonBox,\
    QLineEdit, QGroupBox, QVBoxLayout, QTableView, QStackedWidget, QToolButton
from PyQt5.QtCore import Qt, QEvent, QRect
from PyQt5.QtGui import QColor, QPalette, QFont, QBrush, QKeySequence, QTextCursor, QPainter, QPen


from sys import exit
from preferences import prefs
from util import *

#possible that this is just hoRRENDOUS form
def xw(obj): return obj.x() + obj.width()
def yh(obj): return obj.y() + obj.height()
QWidget.xw = xw
QWidget.yh = yh
#oh well, sue me

class Application(QApplication):
    def __init__(self, name, useStyle=True):
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
                Window {{background: {prefs.get_pref('bg_color') if not None else '#000080'};}}
                QTableWidget {{background:{prefs.get_pref('bg_color') if not None else '000080'};}}
            ''')

app = Application("Report Card Generator", useStyle=True)

class Window(QMainWindow):
    def __init__(self, width, height):
        super(Window, self).__init__()
        self.setFixedSize(width, height)
        self.setWindowTitle("Report Card Generator")

        self.screen_manager = QStackedWidget(self)
        self.setCentralWidget(self.screen_manager)
        self.screens = {}

        self.addScreen("Reports", Screen("Report Builder"))
        self.addScreen("Grades", Screen("Grade Editor"))
        self.addScreen("Setup", Screen("Report Sheet Setup"))
        self.addScreen("Builder", Screen("Report Sheet Builder"))

        self.show()
        self.switchScreen("Setup")
        self.setUI(bg_color=prefs.get_pref('bg_color') if not None else "#000080", txt_color=prefs.get_pref('txt_color') if not None else "#ffffff")

    def addScreen(self, name, screen):
        if not name in self.screens:
            self.screens[name] = screen
            self.screen_manager.addWidget(screen)

    def getScreen(self, name):
        if name in self.screens: return self.screens[name]

    def switchScreen(self, name):
        if name in self.screens:
            self.screen_manager.setCurrentWidget(self.screens[name])
            self.setWindowTitle(self.screens[name].objectName())

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

class Screen(QWidget):
    def __init__(self, name, x=None, y=None, w=None, h=None, shown=False):
        super(Screen, self).__init__()
        self.setObjectName(name)
        self.shown = shown
        if shown:
            self.show()

window = Window(1000, 775)

class Button(QPushButton):
    def __init__(self, screen, text, x, y, focusOnTab=True, shown=True):
        if screen in window.screens:
            self.screen = screen
            super(Button, self).__init__(window.screens[screen])
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
        if screen in window.screens:
            self.screen = screen
            super(Label, self).__init__(window.screens[screen])
        else:
            self.screen = None

        self.setText(text)
        self.move(x, y)
        self.setupFont()
        if shown: self.show()

    def setupFont(self, size=12 if is_windows() else 24, font_family="Arial"):
        self.setFont(QFont(font_family, size, QFont.Bold))

class Dropdown(QComboBox):
    def __init__(self, screen, x, y, options, focusOnTab=True, editable=False):
        if screen in window.screens:
            self.screen = screen
            super(Dropdown, self).__init__(window.screens[screen])
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
        if self.count() == 0: self.addItem(text)
        if text: self.setItemText(self.currentIndex(), text)

class Table(QTableWidget):
    def __init__(self, screen, header=None, data=None, x=None, y=None, w=None, h=None, locked=None, changed=None, shown=True, accepted=None, custom_change=False):
        if screen in window.screens:
            self.screen = screen
            super(Table, self).__init__(len(data) if data else 0, len(data[0]) if data else 0, window.screens[screen])
        else:
            self.screen = None
        self.header = header
        self.locked = locked
        self.setHorizontalHeaderLabels(self.header)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.accepted = accepted #should be dict in form {"HeaderName":{"whitelist":["value1", "value2"] &| "blacklist":["value1", "value2"]}
        self.data = data
        self.changed = changed
        if not custom_change: self.itemChanged.connect(self.validate)
        self.itemSelectionChanged.connect(self.backupCell)
        self.oldText = ""
        self.oldCell = ()
        self.setGeometry(x, y, w, h)
        self.move(x, y)
        if shown: self.show()
        self.enterPressed = False

    def backupCell(self, row=-1, col=-1): #selected and deselected never used, but should be backupCell(selected, deselected)
        if self.currentItem():
            self.oldText = self.currentItem().text()
            self.oldCell = (self.currentItem().row(), self.currentItem().column())
            # print("Backup Cell:", self.oldText, self.oldCell)

    def updateTable(self, data=None):
        self.clearContents()
        self.data = data
        self.setRowCount(len(data) if data is not None else 0)
        self.setColumnCount(len(data[0]) if data is not None and len(data) > 0 else 0)
        self.setHorizontalHeaderLabels(self.header)
        if self.data:
            for row in range(0, len(data)):
                for col in range(0, len(data[row])):
                    item = QTableWidgetItem(data[row][col])
                    item.setForeground(QBrush(QColor(255, 0, 0))) #there is no way to set table info via QSS
                    if self.locked and self.horizontalHeaderItem(col) and self.horizontalHeaderItem(col).text() in self.locked: item.setFlags(Qt.ItemIsEnabled)
                    self.setItem(row, col, item)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.repaint()
        app.changeStyle()

    def keyPressEvent(self, event):
        row, column = self.currentRow(), self.currentColumn()
        editing = self.state() == QTableView.EditingState

        if not editing and event.key() == Qt.Key_Backspace: self.currentItem().setText("")
        elif row == self.rowCount() - 1 and column == self.columnCount() - 1 and event.key() == Qt.Key_Tab:
            self.insertRow(self.rowCount())
            self.setCurrentCell(self.rowCount() - 1, 0)
        elif editing and row < self.rowCount() - 1 and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            self.enterPressed = True
        elif editing and column < self.columnCount() - 1 and event.key() == Qt.Key_Right:
            self.setCurrentCell(row, column + 1)
            # print("Right Column Shift")
        elif editing and column > 0 and event.key() == Qt.Key_Left:
            self.setCurrentCell(row, column - 1)
            # print("Left Column Shift")
        else:
            super().keyPressEvent(event)
            # print("Normal Key Event")

    def validate(self, item):
        if self.oldCell != (item.row(), item.column()): self.oldText = ""
        row = item.row()
        column = item.column()
        #print("Validate", self.oldText, row, column)
        horizontal_header = self.horizontalHeaderItem(column)
        vertical_header = self.verticalHeaderItem(row)
        if horizontal_header is not None and isinstance(self.accepted, dict) and horizontal_header.text() in self.accepted:
            if 'whitelist' in self.accepted[horizontal_header.text()]:
                if not item.text() in self.accepted[horizontal_header.text()]['whitelist'] and item.text() != "":
                    item.setText(self.oldText)
            if 'blacklist' in self.accepted[horizontal_header.text()]:
                if item.text() in self.accepted[horizontal_header.text()]['blacklist']:
                    item.setText(self.oldText)
        #If setCurrentCell is called in keyPressEvent, the validation step occurs AFTER backup step, meaning data is overwritten incorrectly
        if self.enterPressed:
            self.setCurrentCell(row + 1, column)
            self.enterPressed = False
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
        if screen in window.screens:
            self.screen = screen
            super(Textarea, self).__init__(window.screens[screen])
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
        if screen in window.screens:
            self.screen = screen
            super(Checkbox, self).__init__(window.screens[screen])
        else:
            self.screen = None
        self.setChecked(True)
        self.setCheckable(True)
        self.move(x, y)
        self.show()

class ColorButton(QPushButton):
    def __init__(self, screen=None, x=None, y=None, color=None, pref=None):
        if screen in window.screens:
            self.screen = screen
            super(ColorButton, self).__init__(window.screens[screen])
        else:
            self.screen = None
            super(ColorButton, self).__init__()

        if x and y: self.move(x, y)
        self.pref = pref
        self.color = color
        if color:
            self.updateColor(color)
        self.clicked.connect(self.changeColor)

    def updateColor(self, v):
        self.color = v
        self.setText(self.color.upper())
        self.setStyleSheet(f"ColorButton {{background:{self.color}; color: {foreground_from_background(self.color)};}}")

    def saveColor(self):
        if self.pref and prefs.has_pref(self.pref):
            prefs.update_pref(self.pref, self.color)
        app.changeStyle()

    def changeColor(self):
        returned_color = QColorDialog.getColor(title="Test Button")
        if returned_color.isValid():
            self.updateColor(returned_color.name())

#Mine, but layout stuff adapted from https://pythonspot.com/pyqt5-form-layout/
class Multidialog(QDialog):
    def __init__(self, screen, title, form_set, buttons=None, button_pressed=lambda:None):
        if screen in window.screens:
            self.screen = screen
            super(Multidialog, self).__init__(window.screens[screen])
        else:
            self.screen = None

        self.form_set = form_set
        self.elements = {}
        self.title = title
        self.setWindowTitle(self.title)
        self.main_layout = QVBoxLayout()
        self.group_box = QGroupBox()
        self.first_launch = True
        layout = QFormLayout()
        for f in self.form_set:
            if not 'name' in f: continue
            else:
                self.elements[f['name']] = {k:f[k] for k in f}
                e, l = self.get_element(etype=f['type'],
                                        settings=f['settings'] if 'settings' in f else None,
                                        data=f['data'] if 'data' in f else None,
                                        label=f['label'] if 'label' in f else None)
                self.elements[f['name']]['object'], self.elements[f['name']]['label'] = e, l
                self.elements[f['name']]['callback'] = False
                if 'settings' in f: self.elements[f['name']]['settings'] = f['settings']

            layout.addRow(self.elements[f['name']]['label'], self.elements[f['name']]['object'])
        self.initialize_settings()
        if not buttons:
            self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.button_box.accepted.connect(self.accept)
            self.button_box.rejected.connect(self.reject)
        else:
            self.button_box = QDialogButtonBox(QDialogButtonBox.Reset | QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            #this needs some work
            
        self.group_box.setLayout(layout)
        self.main_layout.addWidget(self.group_box)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)
        self.setFixedSize(self.main_layout.sizeHint())

    def get_element(self, etype, settings, data, label):
        widget = None
        label = QLabel(label)
        if etype.lower() == "input":
            le = QLineEdit()
            if data and isinstance(data, str): le.setText(data)
            if settings and 'mode' in settings:
                if settings["mode"] == "password": le.setEchoMode(QLineEdit.Password)
            widget = le
        elif etype.lower() == "dropdown":
            cb = QComboBox()
            cb.setFocusPolicy(Qt.StrongFocus)
            # bugged on enter activate; to-do
            # # QShortcut(QKeySequence(Qt.Key_Return), cb)
            # cb.enterPressed.activated.connect(lambda: cb.showPopup)
            if data:
                if isinstance(data, list): cb.addItems(data)
                elif isinstance(data, str): cb.addItem(data)
            widget = cb
        elif etype.lower() == "color":
            cb = ColorButton()
            if settings and 'pref' in settings:
                cb.pref = settings['pref']
                cb.color = prefs.get_pref(cb.pref)
            elif 'color' in settings:
                cb.color = settings['color']
            cb.updateColor(cb.color)
            widget = cb
        return widget, label

    def initialize_settings(self):
        for el in self.elements:
            e = self.elements[el]
            if 'settings' in e:
                settings = e['settings']
                if 'conditional_show' in settings:
                    if 'element' in settings['conditional_show']:
                        if settings['conditional_show']['element'] in self.elements:
                            ref_e = settings['conditional_show']['element']
                            if 'callback' in self.elements[ref_e] and not self.elements[ref_e]['callback']:
                                if 'object' in self.elements[ref_e] and isinstance(self.elements[ref_e]['object'], QComboBox):
                                    self.elements[ref_e]['object'].currentIndexChanged.connect(self.initialize_settings)
                                    self.elements[ref_e]['callback'] = True
                            if 'object' in self.elements[ref_e]:
                                if 'not_state' in settings['conditional_show']:
                                    sv = not (self.elements[ref_e]['object'].currentText() in settings['conditional_show']['not_state'])
                                    e['object'].setVisible(sv)
                                    e['label'].setVisible(sv)
                                elif 'state' in settings['conditional_show']:
                                    sv = (self.elements[ref_e]['object'].currentText() in settings['conditional_show']['state'])
                                    e['object'].setVisible(sv)
                                    e['label'].setVisible(sv)

    def refresh(self):
        for w in self.group_box.children():
            if isinstance(w, QLineEdit): w.setText("")
            elif isinstance(w, QComboBox):
                if w.count() > 0: w.setCurrentIndex(0)

class ArrowButton(QToolButton):
    arrow_map = {"UP":Qt.UpArrow, "DOWN":Qt.DownArrow, "LEFT":Qt.LeftArrow, "RIGHT":Qt.RightArrow}
    def __init__(self, screen, x, y, width=0, height=0, arrow=None):
        if screen in window.screens:
            self.screen = screen
            super(ArrowButton, self).__init__(window.screens[screen])
        else:
            self.screen = None

        if arrow and arrow in ArrowButton.arrow_map: self.setArrowType(ArrowButton.arrow_map[arrow])

        if width > 0 and height > 0: self.setGeometry(x, y, width, height)
        else: self.move(x, y)

        self.show()