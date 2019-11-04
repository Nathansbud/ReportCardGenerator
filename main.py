from threading import Thread
from math import floor

import re

import googleapiclient.errors

from PyQt5.QtWidgets import QLineEdit, QInputDialog, QDialog, QTableWidget, QTableWidgetItem, QSizePolicy, QWidget, QHeaderView
from cuter import Application, Window, Button, Label, Dropdown, Textarea, ColorSelector, Checkbox#, #Screen
from cuter import app, screens, switch_screen  # Pared down versions of ^, to reduce cluttered code
from google_sheets import get_sheet, write_sheet
from preferences import prefs
from grades import grade_schemes, GradeSet, load_grades

'''
Todo:
    - Async spreadsheet loading?
    - GUI so that user doesn't have to deal with weird text macros
'''

report_sheet = prefs.get_pref("report_sheet")

def setup_sheet(report=None):
    global report_sheet

    passed = False
    ask_for = "Input report sheet ID:"
    while not passed:
        if report is None:
            report, ok = QInputDialog(screens["Reports"]).getText(screens["Reports"], "Report Sheet", ask_for, QLineEdit.Normal, "")

        check_is = ["d", "https:", "spreadsheets", "http:", "docs.google.com", '']
        check_starts = ["edit#"]

        report = [part for part in report.split('/') if not part in check_is and not part.startswith(*check_starts)]
        if len(report) != 1:
            print("Something went wrong with your link!")
            print(report)
            report = None
        else:
            try:
                sheet_data = get_sheet(report[0])
                report_sheet = report[0]
                prefs.update_pref("report_sheet", report[0])
                return sheet_data
            except googleapiclient.errors.HttpError:
                ask_for = "Something went wrong getting your reports! Input report sheet ID:"
                report = None
        report = None

report_column = "D"
row_offset = 2

sheet = []
all_tabs = []
class_tabs = []
sentence_tabs = []
class_students = []
preset_list = {}
sentences = []  # Should be populated with SentenceGroup elements
grade_scheme_tabs = []
grade_rules = []

first_run = True

def setup():
    global sheet
    global all_tabs
    global class_tabs
    global sentence_tabs
    global grade_scheme_tabs
    global class_students
    global preset_list
    global grade_rules
    global sentences
    global first_run

    sheet = setup_sheet(report_sheet if len(report_sheet) > 0 else None)
    all_tabs = [(tab['properties']['title'], tab['properties']['sheetId']) for tab in sheet.get('sheets')]
    grade_scheme_tabs = [tab for tab in all_tabs if tab[0].startswith("Grade Scheme") or tab[0].startswith("Grade Rule")]
    class_tabs = [tab for tab in all_tabs if len(tab[0].split("-"))==2]
    sentence_tabs = [tab for tab in all_tabs if tab[0].startswith("Sentences")]
    class_students = []
    preset_list = {}
    grade_rules = []
    if not first_run:
        load_grades()
        fill_class_data()
        update_sentences()
    first_run = False

setup()

class_label = Label("Reports", "Class: ", screens['Reports'].width() / 2.5, 15)
class_dropdown = Dropdown("Reports", class_label.x() + class_label.width(), class_label.y(), [tab[0] for tab in class_tabs])

student_label = Label("Reports", "Name: ", 50, 75)
student_dropdown = Dropdown("Reports", student_label.x() + student_label.width(), student_label.y(), [])

preset_button = Button("Reports", "Generate Preset", student_dropdown.x() + student_dropdown.width(), student_dropdown.y(), False)
preset_dropdown = Dropdown("Reports", preset_button.x() + preset_button.width(), preset_button.y(), [], False)
grade_button = Button("Reports", "Generate From Grades", preset_dropdown.x()+preset_dropdown.width(), preset_dropdown.y(), False)
reload_grade_schemes_button = Button("Reports", "Reload Grade Rules", grade_button.x()+grade_button.width(), preset_dropdown.y(), False)

generate_button = Button("Reports", "Generate", screens['Reports'].width()/2 - 20, 410)
report_area = Textarea("Reports", "", 0, 450, screens['Reports'].width(), 250)
submit_button = Button("Reports", "Submit", screens['Reports'].width()/2 - 20, 700)


color_selector = ColorSelector("Reports")

open_preferences_from_reports_button = Button("Reports", "Open Preferences", screens['Reports'].width(), 0, False)
open_preferences_from_reports_button.move(screens['Reports'].width() - open_preferences_from_reports_button.width(), 0)

open_reports_from_preferences_button = Button("Preferences", "Open Reports", screens['Preferences'].width() - 50, 0, False)
open_reports_from_preferences_button.move(screens['Preferences'].width() - open_reports_from_preferences_button.width(), 0)

open_grades_from_reports_button = Button("Reports", "Open Grades", reload_grade_schemes_button.x() + reload_grade_schemes_button.width(), preset_dropdown.y(), False)
open_reports_from_grades_button = Button("Grades", "Open Reports", screens['Grades'].width() - 50, 0, False)
open_reports_from_grades_button.move(screens['Grades'].width() - open_reports_from_preferences_button.width(), 0)


open_preferences_from_reports_button.clicked.connect(lambda: switch_screen("Preferences"))
open_reports_from_preferences_button.clicked.connect(lambda: switch_screen("Reports"))
open_grades_from_reports_button.clicked.connect(lambda: switch_screen("Grades"))
open_reports_from_grades_button.clicked.connect(lambda: switch_screen("Reports"))


reload_button = Button("Reports", "Reload", open_preferences_from_reports_button.x(), open_preferences_from_reports_button.y() + open_preferences_from_reports_button.height(), False)

background_color_button = Button("Preferences", "BG Color", screens['Preferences'].width() - 150, open_reports_from_preferences_button.y() + open_reports_from_preferences_button.height(), False)
text_color_button = Button("Preferences", "Text Color", screens['Preferences'].width() - 150, background_color_button.y() + background_color_button.height(), False)
label_color_button = Button("Preferences", "Label Color", screens['Preferences'].width() - 150, text_color_button.y() + text_color_button.height(), False)

background_color_button.clicked.connect(lambda: color_selector.updateColor("Background Color", "bg_color"))
text_color_button.clicked.connect(lambda: color_selector.updateColor("Text Color", "txt_color"))
label_color_button.clicked.connect(lambda: color_selector.updateColor("Label Color", "lbl_color"))

refresh_button = Button("Reports", "Refresh Sentences", 0, 0, False)
add_sentence_button = Button("Reports", "Add Sentence", 0, refresh_button.y() + refresh_button.height(), False)

class Student:
    pronouns = {
        "M": ["he", "his", "him", "his"],
        "F": ["she", "her", "her", "hers"],
        "T": ["they", "their", "them", "theirs"]
    }

    def __init__(self, first_name, last_name, gender, report, grades, classroom, offset):
        self.first_name = first_name
        self.last_name = last_name
        self.report = report
        self.grades = grades
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
    dialog = QInputDialog(screens['Reports'])
    dialog.setOption(QInputDialog.UseListViewForComboBoxItems)
    def __init__(self, label, x, y, options, index):

        self.index = index

        self.x = x
        self.y = y

        self.checkbox = Checkbox("Reports", x, y)
        self.label = Label("Reports", label, x + self.checkbox.width(), y)
        self.dropdown = Dropdown("Reports", self.label.x() + self.label.width(), y, options)

        self.add = Button("Reports", "+", self.dropdown.x() + self.dropdown.width(), y, False)
        self.remove = Button("Reports", "-", self.add.x() + self.add.width(), y, False)
        self.change = Button("Reports", "Edit", self.remove.x() + self.remove.width(), y, False)

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
        text, ok = QInputDialog(screens['Reports']).getText(screens['Reports'], "Add Option", "Sentence", QLineEdit.Normal, "")
        if ok and len(text) > 0:
            self.dropdown.addItem(text)
            self.dropdown.setCurrentIndex(self.dropdown.count()-1)
            self.checkbox.setChecked(True)

        sentence_thread = Thread(target=self.write_sentences)
        sentence_thread.start()

    def removeOption(self):
        if self.dropdown.count() > 0:
            item_list = [self.dropdown.itemText(i) for i in range(self.dropdown.count())]
            SentenceGroup.dialog.setComboBoxItems(item_list)
            SentenceGroup.dialog.setWindowTitle("Remove Item")
            SentenceGroup.dialog.setLabelText("Choose an item to remove:")

            if SentenceGroup.dialog.exec():
                item_list.remove(SentenceGroup.dialog.textValue())
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
            SentenceGroup.dialog.setComboBoxItems(item_list)
            SentenceGroup.dialog.setWindowTitle("Edit Item")
            SentenceGroup.dialog.setLabelText("Choose an item to edit:")
            if SentenceGroup.dialog.exec():
                replace, ok = QInputDialog(screens['Reports']).getText(screens['Reports'], "Replacement Option", "Replace '{}' With:".format(SentenceGroup.dialog.textValue()), QLineEdit.Normal, SentenceGroup.dialog.textValue())
                if ok and len(replace) > 0:
                    item_list[item_list.index(SentenceGroup.dialog.textValue())] = replace
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
            tab_id = [tab[1] for tab in sentence_tabs if tab[0] == "Sentences " + class_dropdown.currentText().split("-")[0]]
            write_sheet(report_sheet, "", mode="COLUMNS", remove=[self.index, self.index+1], tab_id=tab_id[0])
        else:
            item_list = [self.dropdown.itemText(i) for i in range(self.dropdown.count())] + ["", "", "", "", "", "", "", "", "", ""]
            write_sheet(report_sheet, [item_list], "Sentences {}!{}2:{}".format(class_dropdown.currentText().split("-")[0], col, col + str(item_list.__len__() + 10)), "COLUMNS")

def fill_class_data():
    global report_sheet
    global class_students
    global class_dropdown
    global class_tabs
    global student_dropdown
    global report_area
    global row_offset


    student_dropdown.clear()
    class_students = []

    #Get full class sheet, including headers
    current_class = get_sheet(report_sheet, "{}!A1:Z1000".format(class_dropdown.currentText())).get('values')
    ro = row_offset #Row offset

    #Drop the headers, iterate over all student rows
    if current_class is not None:
        assignment_headers = None
        scheme_headers = None
        if len(current_class[0]) >= 5:
            scheme_headers = [c.split("$")[-1] if len(c.split("$")) == 2 else 'IB' for c in current_class[0][4:]]
            assignment_headers = [c.split("$")[0] if len(c.split("$")) == 2 else c for c in current_class[0][4:]]
        for student in current_class[1:]:
            class_students.append(
                Student(
                    student[0], #First Name
                    student[1] if len(student) >= 2 else "", #Last Name
                    student[2] if len(student) >= 3 else "", #Gender
                    student[3] if len(student) >= 4 else "", #Report
                    #scheme, assignment, and student grades SHOULD all be the same length, so zip to iterate over all 3 to make grades dict
                    {assignment:{'grade':grade, 'scheme':scheme} for assignment, grade, scheme in zip(assignment_headers, student[4:], scheme_headers)} if len(student) >= 5 else {},
                    class_dropdown.currentText(),
                    ro
                )
            )
            ro+=1

        student_dropdown.addItems([student.first_name + " " + student.last_name for student in class_students])
    if class_dropdown.history[-1].split("-")[0] != class_dropdown.currentText().split("-")[0]:
        update_sentences()
    class_dropdown.history.append(class_dropdown.currentText())
    update_report()
    setup_grades_table()

def update_tab_order():
    global sentences
    global class_dropdown
    global student_dropdown
    global report_area

    screens['Reports'].setTabOrder(class_dropdown, student_dropdown)

    if len(sentences) > 0:
        screens['Reports'].setTabOrder(student_dropdown, sentences[0].dropdown)
        count = 0
        if len(sentences) > 1:
            for sentence in sentences[:-1]:
                screens['Reports'].setTabOrder(sentences[count].dropdown, sentences[count+1].dropdown)
                count+=1
        screens['Reports'].setTabOrder(sentences[count].dropdown, generate_button)
    else:
        screens['Reports'].setTabOrder(student_dropdown, generate_button)
    screens['Reports'].setTabOrder(generate_button, report_area)
    screens['Reports'].setTabOrder(report_area, submit_button)

def update_sentences():
    global sentences
    global sentence_tabs
    global class_dropdown

    if len(sentence_tabs) > 0:
        for tab in sentence_tabs:
            if tab[0].endswith(class_dropdown.currentText().split("-")[0]):
                for elem in sentences: elem.delete()
                sentences = []
                print("Called update sentences...")
                current_sentences = get_sheet(report_sheet, "{}!A1:Z1000".format("Sentences " + str(class_dropdown.currentText().split("-")[0])), "COLUMNS").get('values')
                count = 0
                ro = 0
                if current_sentences is not None:
                    for entry in current_sentences:
                        if len(entry) > 1:
                            sentences.append(
                                SentenceGroup("S{}:".format(count+1), 50, 125 + 25 * count, list(filter(None, entry[1:])), ro)
                            )
                            count += 1
                        ro+=1
                populate_presets(current_sentences)
                break
    update_tab_order()

def add_sentence():
    global sentences
    sentences.append(
        SentenceGroup(f"S{sentences.__len__()+1}:", 50, 125 + 25 * sentences.__len__(), [], sentences.__len__())
    )
    update_tab_order()

class Preset:
    prefix = {
        "grade":"~",
        "linear":"*"
    }
    def __init__(self, text, group, index, ruleset=None, priority=None):
        self.text = text
        self.group = group
        self.index = index
        self.ruleset = ruleset
        self.priority = priority

    def __repr__(self):
        return f'Text: {self.text} | Group: {self.group} | Index: {self.index} | Ruleset: {self.ruleset} | Priority: {self.priority}'

def populate_presets(sentence_set):
    global preset_dropdown
    global preset_list
    global grade_rules

    preset_dropdown.clear()
    presets_found = []
    preset_list = {}
    grade_rules = []

    count = 1
    if sentence_set is not None:
        for elem in sentence_set:
            for cell in elem:
                #Split cell based on Preset delimiters
                cell_parts = re.split(f"[{Preset.prefix['grade']}{Preset.prefix['linear']}]", cell)
                if len(cell_parts) > 1:
                    preset_text = cell_parts[0] #Sentence comes first
                    for ps in cell_parts[1:]:
                        preset_parts = re.split("[|]", ps) #Split cell based into its components
                        if len(preset_parts) == 3: #3-part ones have a ruleset string
                            grade_rules.append(
                                Preset(preset_text, preset_parts[0], count, ruleset=preset_parts[1], priority=preset_parts[2])
                            )
                        elif len(preset_parts) == 2:
                            presets_found.append(
                                Preset(preset_text, preset_parts[0], preset_parts[1])
                            )
            count+=1

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

    if student_dropdown.count() > 0:
        report_area.setText(class_students[student_dropdown.currentIndex()].report)
        setup_grades_table()
    else:
        report_area.setText("")
    report_area.repaint()


def send_report():
    global class_students
    global student_dropdown

    if len(class_students) > 0:
        class_students[student_dropdown.currentIndex()].report = report_area.toPlainText()
        submit_thread = Thread(target=class_students[student_dropdown.currentIndex()].submit_report)
        submit_thread.start()

def generate_report():
    global sentences
    global report_area
    global student_dropdown
    global class_students

    report_area.setText("")
    if len(class_students) > 0:
        for sentence in sentences:
            if sentence.checkbox.isChecked():
                report_area.setText(report_area.toPlainText() + replace_generics(sentence.dropdown.currentText())+" ")
    report_area.repaint()

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
    report_area.repaint()


grades_label = Label('Grades', "Student has no grades! Try adding something!", 300, 50, visible=False)
class GradeTable(QTableWidget):
    def __init__(self, screen, header=["Assignment", "Grade", "Scheme"], data=None, x=None, y=None):
        if screen in screens:
            self.screen = screen
            super(GradeTable, self).__init__(len(data) if data else 0, len(data[0]) if data else 0, screens[screen])
        else:
            self.screen = None
        self.header = header
        self.setHorizontalHeaderLabels(self.header)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.data = data
        self.updateTable(self.data)
        self.move(x, y)
        self.show()


    def updateTable(self, data=None):
        global grades_label
        self.setRowCount(0)
        self.data = data
        self.setRowCount(len(data) if data is not None else 0)
        self.setColumnCount(len(data[0]) if data is not None and len(data) > 0 else 0)
        if self.data:
            self.show()
            grades_label.hide()
            for row in range(0, len(data)):
                for col in range(0, len(data[row])):
                    self.setItem(row, col, QTableWidgetItem(data[row][col]))
        else:
            self.hide()
            grades_label.show()
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.setHorizontalHeaderLabels(self.header)
        self.repaint()

grades_table = GradeTable('Grades', x=0, y=0)

def generate_report_from_grades():
    global class_students
    global grade_rules
    global class_dropdown

    report_area.setText("")
    if len(class_students) > 0:
        current_student = class_students[student_dropdown.currentIndex()]
        chosen_options = {}
        for elem in grade_rules:
            tk = GradeSet.tokenize(elem.ruleset)
            use_scheme = 'IB'
            if len(tk) == 3:
                if tk[0] in current_student.grades: use_scheme = current_student.grades[tk[0]]['scheme']
                elif tk[2] in current_student.grades: use_scheme = current_student.grades[tk[2]]['scheme']

                if GradeSet(use_scheme).evaluate(current_student.grades, elem.ruleset):
                    if elem.index in chosen_options:
                        #greater than because number is inverted
                        if chosen_options[elem.index].priority > elem.priority:
                            chosen_options[elem.index] = elem
                    else:
                        chosen_options[elem.index] = elem
        for option in chosen_options:
            report_area.setText(report_area.toPlainText() + replace_generics(chosen_options[option].text) + " ")
    report_area.repaint()

def setup_grades_table():
    global class_students
    global student_dropdown
    global grades_table

    if len(class_students) > 0:
        current_student = class_students[student_dropdown.currentIndex()]
        grades_table.updateTable([[g, current_student.grades[g]['grade'], current_student.grades[g]['scheme']] for g in current_student.grades])
    else:
        grades_table.updateTable()

load_grades()
fill_class_data()

class_dropdown.currentIndexChanged.connect(fill_class_data)
student_dropdown.currentIndexChanged.connect(update_report)
submit_button.clicked.connect(send_report)
generate_button.clicked.connect(generate_report)
preset_button.clicked.connect(generate_report_from_preset)
grade_button.clicked.connect(generate_report_from_grades)
reload_button.clicked.connect(setup)
refresh_button.clicked.connect(update_sentences)
reload_grade_schemes_button.clicked.connect(load_grades)
add_sentence_button.clicked.connect(add_sentence)

def replace_generics(fmt):
    global student_dropdown
    global class_students
    global pronouns

    if len(class_students) > 0:
        current_student = class_students[student_dropdown.currentIndex()]
        ps = current_student.get_pronouns()

        #* = Preset
        #~ = Grade Preset
        fmt = fmt.split(Preset.prefix['grade'])[0].split(Preset.prefix['linear'])[0].strip().format(
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
    else: return None

if __name__ == "__main__":
    app.exec()



