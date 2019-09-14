import re
import requests
import os
import json
from threading import Thread, ThreadError

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit, QColorDialog
from PyQt5.QtCore import Qt, QEvent

from cuter import Application, Window, Button, Label, Input, Dropdown, Textarea, ColorSelector, Checkbox #Pared down versions of ^, to reduce cluttered code
from googleapi import get_sheet, write_sheet

pronouns = {
    "M":["he", "his", "him", "his"],
    "F":["she", "her" , "her", "hers"],
    "T":["they", "their" , "them", "theirs"]
}

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


generate_button = Button(main_window, "Generate", main_window.width()/2 - 20, 410)
report_area = Textarea(main_window, "", 0, 450, main_window.width(), 250)
submit_button = Button(main_window, "Submit", main_window.width()/2 - 20, 710)

color_selector = ColorSelector(main_window, "BG")
color_button = Button(main_window, "Colors", main_window.width() - 150, student_label.y())
color_button.clicked.connect(color_selector.openColorDialog)


class Student:
    def __init__(self, first_name, last_name, gender, report, classroom, row_offset):
        self.first_name = first_name
        self.last_name = last_name
        self.report = report
        self.gender = gender
        self.classroom = classroom
        self.row_offset = row_offset


    def submit_report(self, report=None):
        global report_sheet
        global report_column
        #global report_cell
        if not report: #Cannot pass self.params as arguments to a function, as self is defined in that scope
            report = self.report

        write_sheet(report_sheet, [[report]], "{}!{}".format(self.classroom, report_column + str(self.row_offset)))

#Combination Label, Dropdown, & Checkbox
class SentenceGroup:
    def __init__(self, label, x, y, options):
        self.checkbox = Checkbox(main_window, x, y)
        self.label = Label(main_window, label, x + self.checkbox.width(), y)
        self.dropdown = Dropdown(main_window, self.label.x() + self.label.width(), y, options)
        self.visible = True

    @property
    def visible(self):
        return self.visible
    @visible.setter
    def visible(self, visible):
        self.visible = visible

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
    update_report()

def update_report():
    global class_students
    global student_dropdown
    global report_area

    report_area.setText(class_students[student_dropdown.currentIndex()].report)


def generate_report():
    report_area.setText("")

def send_report():
    global class_students
    global student_dropdown

    class_students[student_dropdown.currentIndex()].report = report_area.toPlainText()
    submit_thread = Thread(target=class_students[student_dropdown.currentIndex()].submit_report)
    submit_thread.start()

fill_class_data()

class_dropdown.currentIndexChanged.connect(fill_class_data)
student_dropdown.currentIndexChanged.connect(update_report)
submit_button.clicked.connect(send_report)

def replace_generics(preset, name, p):
    if len(p) == 0: p = "T"
    preset = preset.strip()\
                .replace("@", name)\
                .replace("#", pronouns[p][0])\
                .replace("$", pronouns[p][1])\
                .replace("%", pronouns[p][2])\
                .replace("^", pronouns[p][3]) + " "

    preset = preset.replace("they is", "they are")

    capitalizationIndices = []
    for i in range(0, len(preset)):
        if preset[i] == "." or preset[i] == "!" or preset[i] == "?": capitalizationIndices.append(i)



    for index in capitalizationIndices:
        if index+2 < len(preset):
            preset = preset[0:index+2] + preset[index+2].upper() + preset[index+3:]

    return preset.strip()



if __name__ == "__main__":
    app.exec()
