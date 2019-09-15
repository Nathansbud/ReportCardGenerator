from threading import Thread
from math import floor

from PyQt5.QtWidgets import QLineEdit, QInputDialog, QWidget
from cuter import Application, Window, Button, Label, Input, Dropdown, Textarea, ColorSelector, Checkbox #Pared down versions of ^, to reduce cluttered code
from google_sheets import get_sheet, write_sheet

'''
Todo:
    - Rework program load model so that all data is loaded 
    - Async/io on spreadsheet calls
    - Hook-ins for presets (i.e. hooks into student grades)
'''

report_sheet = "1ermre2z1PwXIXXEymu2aKHRJqtkCKyn2jxR_HpuIxGQ"
report_column = "D"
row_offset = 2

sheet = get_sheet(report_sheet)
all_tabs = [(tab['properties']['title'], tab['properties']['sheetId']) for tab in sheet.get('sheets')]

class_tabs = [tab for tab in all_tabs if not tab[0].startswith("Sentences")]
sentence_tabs = [tab for tab in all_tabs if tab[0].startswith("Sentences")]

class_students = []

app = Application("Report Card Generator")


main_window = Window("Report Card Generator", 0, 0, 1000, 750, True)

class_label = Label(main_window, "Class: ", main_window.width() / 2.5, 15)
class_dropdown = Dropdown(
    main_window,
    class_label.x() + class_label.width(),
    class_label.y() ,
    [tab[0] for tab in class_tabs]
)

student_label = Label(main_window, "Name: ", 50, 75)
student_dropdown = Dropdown(
    main_window,
    student_label.x() + student_label.width(),
    student_label.y(),
    []
)

preset_button = Button(main_window, "Generate Preset", student_dropdown.x() + student_dropdown.width(), student_dropdown.y())
preset_dropdown = Dropdown(
    main_window,
    preset_button.x() + preset_button.width(),
    preset_button.y(),
    []
)
preset_list = {}

sentences = [] #Should be populated with SentenceGroup elements

generate_button = Button(main_window, "Generate", main_window.width()/2 - 20, 410)
report_area = Textarea(main_window, "", 0, 450, main_window.width(), 250)
submit_button = Button(main_window, "Submit", main_window.width()/2 - 20, 710)

color_selector = ColorSelector(main_window, "BG")
color_button = Button(main_window, "Colors", main_window.width() - 150, student_label.y(), False)
color_button.clicked.connect(color_selector.openColorDialog)

refresh_button = Button(main_window, "Refresh", generate_button.x() + generate_button.width(), generate_button.y(), False)

class Student:
    pronouns = {
        "M": ["he", "his", "him", "his"],
        "F": ["she", "her", "her", "hers"],
        "T": ["they", "their", "them", "theirs"]
    }

    def __init__(self, first_name, last_name, gender, report, classroom, offset):
        self.first_name = first_name
        self.last_name = last_name
        self.report = report
        self.gender = gender
        self.classroom = classroom
        self.offset = offset


    def submit_report(self, report=None):
        global report_sheet
        global report_column
        if not report:
            report = self.report
        write_sheet(report_sheet, [[report]], "{}!{}".format(self.classroom, report_column + str(self.offset)))

    def get_pronouns(self):
        if self.gender:
            return Student.pronouns[self.gender]
        else:
            return Student.pronouns["T"]

class SentenceGroup:
    def __init__(self, label, x, y, options, index):

        self.index = index

        self.x = x
        self.y = y

        self.checkbox = Checkbox(main_window, x, y)
        self.label = Label(main_window, label, x + self.checkbox.width(), y)
        self.dropdown = Dropdown(main_window, self.label.x() + self.label.width(), y, options)

        self.add = Button(main_window, "+", self.dropdown.x() + self.dropdown.width(), y, False)
        self.remove = Button(main_window, "-", self.add.x() + self.add.width(), y, False)
        self.change = Button(main_window, "Edit", self.remove.x() + self.remove.width(), y, False)

        self.add.clicked.connect(self.addOption)
        self.remove.clicked.connect(self.removeOption)
        self.change.clicked.connect(self.editOption)

        self.manual_delete = False

    def shift(self, x, y):
        self.checkbox.move(x, y)
        self.label.move(x + self.checkbox.width(), y)
        self.dropdown.move(self.label.x() + self.label.width(), y)
        self.add.move(self.dropdown.x() + self.dropdown.width(), y)
        self.remove.move(self.add.x() + self.add.width(), y)
        self.change.move(self.remove.x() + self.remove.width(), y)

    def delete(self):
        self.dropdown.deleteLater()
        self.label.deleteLater()
        self.checkbox.deleteLater()
        self.add.deleteLater()
        self.remove.deleteLater()
        self.change.deleteLater()

    def addOption(self):
        text, ok = QInputDialog(main_window).getText(main_window, "Add Option", "Sentence", QLineEdit.Normal, "")
        if ok and len(text) > 0:
            self.dropdown.addItem(text)

        sentence_thread = Thread(target=self.write_sentences)
        sentence_thread.start()

    def removeOption(self):
        if self.dropdown.count() > 0:
            item_list = [self.dropdown.itemText(i) for i in range(self.dropdown.count())]
            item, ok = QInputDialog(main_window).getItem(main_window, "Remove Option", "Option:", item_list, 0, False)
            if ok and item:
                item_list.remove(item)
                self.dropdown.clear()
                self.dropdown.addItems(item_list)
                if self.dropdown.count() == 0:
                    self.checkbox.setChecked(False)
                sentence_thread = Thread(target=self.write_sentences)
                sentence_thread.start()
        else:
            global sentences
            sentences.remove(self)
            self.delete()

            for i in range(0, len(sentences)):
                if sentences[i].index > self.index:
                    sentences[i].index -= 1
                    sentences[i].shift(sentences[i].x, sentences[i].y - 25)
                    sentences[i].label.setText("S{}:".format(i + 1))
            self.manual_delete = True
            sentence_thread = Thread(target=self.write_sentences)
            sentence_thread.start()

    def editOption(self):
        if self.dropdown.count() > 0:
            item_list = [self.dropdown.itemText(i) for i in range(self.dropdown.count())]
            item, ok = QInputDialog(main_window).getItem(main_window, "Edit Option", "Option:", item_list, 0, False)
            if item and ok:
                replace, ok = QInputDialog(main_window).getText(main_window, "Replacement Option", "Replace '{}' With:".format(item), QLineEdit.Normal, item)
                if ok and len(replace) > 0:
                    item_list[item_list.index(item)] = replace
                    self.dropdown.clear()
                    self.dropdown.addItems(item_list)
                    sentence_thread = Thread(target=self.write_sentences)
                    sentence_thread.start()
        else:
            self.addOption()


    def write_sentences(self):
        global class_dropdown
        global report_sheet
        global sentence_tabs

        col = ""

        ind = self.index
        times = floor(ind/26 + 1)

        for i in range(0, times):
            col += str(chr(ind % 26 + 65))
            ind -= 26

        if self.manual_delete:
            tab_id = [tab[1] for tab in sentence_tabs if tab[0] == "Sentences " + class_dropdown.currentText()[0]]
            write_sheet(report_sheet, "", mode="COLUMNS", remove=[self.index, self.index+1], tab_id=tab_id[0])
        else:
            item_list = [self.dropdown.itemText(i) for i in range(self.dropdown.count())] + ["", "", "", "", "", "", "", "", "", ""]
            write_sheet(report_sheet, [item_list], "Sentences {}!{}2:{}".format(class_dropdown.currentText()[0], col, col + str(item_list.__len__() + 10)), "COLUMNS")

def fill_class_data():
    global class_students
    global class_dropdown
    global class_tabs
    global student_dropdown
    global report_area
    global row_offset

    student_dropdown.clear()
    class_students = []

    current_class = get_sheet(report_sheet, "{}!A2:D1000".format(class_dropdown.currentText())).get('values')
    ro = row_offset #Row offset
    for student in current_class:
        class_students.append(
            Student(
                student[0], #First Name
                student[1], #Last Name
                student[2], #Gender
                student[3], #Report
                class_dropdown.currentText(),
                ro
            )
        )
        ro+=1

    student_dropdown.addItems([student.first_name + " " + student.last_name for student in class_students])
    if class_dropdown.history[-1][0] != class_dropdown.currentText()[0]:
        update_sentences()
    class_dropdown.history.append(class_dropdown.currentText())
    update_report()

def update_tab_order():
    global sentences
    global class_dropdown
    global student_dropdown
    global report_area

    main_window.setTabOrder(class_dropdown, student_dropdown)

    if len(sentences) > 0:
        main_window.setTabOrder(student_dropdown, sentences[0].dropdown)
        count = 0
        if len(sentences) > 1:
            for sentence in sentences[:-1]:
                main_window.setTabOrder(sentences[count].dropdown, sentences[count+1].dropdown)
                count+=1
        main_window.setTabOrder(sentences[count].dropdown, generate_button)
    else:
        main_window.setTabOrder(student_dropdown, generate_button)
    main_window.setTabOrder(generate_button, report_area)
    main_window.setTabOrder(report_area, submit_button)

def update_sentences():
    global sentences
    global sentence_tabs
    global class_dropdown
    
    for tab in sentence_tabs:
        if tab[0][-1] == class_dropdown.currentText()[0]:
            for elem in sentences:
                elem.delete()
            sentences = []
            
            current_sentences = get_sheet(report_sheet, "{}!A1:Z1000".format("Sentences " + str(class_dropdown.currentText()[0])), "COLUMNS").get('values')
            count = 0
            ro = 0
            for entry in current_sentences:
                if len(entry) > 1:
                    sentences.append(
                        SentenceGroup("S{}:".format(count+1), 50, 125 + 25 * count, entry[1:], ro)
                    )
                    count += 1
                ro+=1
            populate_presets(current_sentences)
            break
    update_tab_order()

class Preset:
    def __init__(self, text, group, index):
        self.text = text
        self.group = group
        self.index = index

def populate_presets(sentence_set):
    global preset_dropdown
    global preset_list

    preset_dropdown.clear()
    presets_found = []
    preset_list = {}

    for elem in sentence_set:
        for cell in elem:
            cell_split = cell.split("*")
            if len(cell_split) == 2:
                preset_split = cell_split[1].split("|")
                if len(preset_split) == 2:
                    presets_found.append(Preset(cell_split[0], preset_split[0], preset_split[1]))

    for elem in presets_found:
        if not elem.group in preset_list:
            preset_list[elem.group] = []
        preset_list[elem.group].append(elem)

    for elem in preset_list:
        preset_list[elem] = sorted(preset_list[elem], key=lambda e: int(e.index))
        preset_dropdown.addItem(elem)

def update_report():
    global class_students
    global student_dropdown
    global report_area

    report_area.setText(class_students[student_dropdown.currentIndex()].report)



def send_report():
    global class_students
    global student_dropdown

    class_students[student_dropdown.currentIndex()].report = report_area.toPlainText()
    submit_thread = Thread(target=class_students[student_dropdown.currentIndex()].submit_report)
    submit_thread.start()

def generate_report():
    global sentences
    global report_area
    global student_dropdown
    global class_students

    report_area.setText("")
    for sentence in sentences:
        if sentence.checkbox.isChecked():
            report_area.setText(report_area.toPlainText() + replace_generics(sentence.dropdown.currentText())+" ")

def generate_report_from_preset():
    global report_area
    global student_dropdown
    global class_students
    global preset_list
    global preset_dropdown

    report_area.setText("")
    if preset_dropdown.count() > 0:
        for elem in preset_list[preset_dropdown.currentText()]:
            report_area.setText(report_area.toPlainText() + replace_generics(elem.text) + " ")


fill_class_data()

class_dropdown.currentIndexChanged.connect(fill_class_data)
student_dropdown.currentIndexChanged.connect(update_report)
submit_button.clicked.connect(send_report)
generate_button.clicked.connect(generate_report)
refresh_button.clicked.connect(update_sentences)
preset_button.clicked.connect(generate_report_from_preset)

def replace_generics(fmt):
    global student_dropdown
    global class_students
    global pronouns

    current_student = class_students[student_dropdown.currentIndex()]
    ps = current_student.get_pronouns()

    fmt = fmt.split("*")[0].strip().format(
        name=current_student.first_name,
        p1=ps[0],
        p2=ps[1],
        p3=ps[2],
        p4=ps[3]
    ).replace("@", current_student.first_name).replace("#", ps[0]).replace("$", ps[1]).replace("%", ps[2]).replace("^", ps[3])
    if current_student.gender == "T":
        fmt = fmt.replace("they is", "they are")

    capitalizationIndices = []
    for i in range(0, len(fmt)):
        if fmt[i] == "." or fmt[i] == "!" or fmt[i] == "?": capitalizationIndices.append(i)

    for index in capitalizationIndices:
        if index + 2 < len(fmt):
            fmt = fmt[0:index + 2] + fmt[index + 2].upper() + fmt[index + 3:]

    return fmt.strip()

if __name__ == "__main__":
    app.exec()
