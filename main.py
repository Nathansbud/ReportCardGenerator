import re

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit
from PyQt5.QtCore import Qt, QEvent

from cuter import Application, Window, Button, Label, Input, Dropdown, Textarea #Pared down versions of ^, to reduce cluttered code
from googleapi import get_sheet, write_sheet

run_app = True

pronouns = {
    "M":["he", "his", "him", "his"],
    "F":["she", "her" , "her", "hers"],
    "T":["they", "their" , "them", "theirs"]
}

report_sheet = "1ermre2z1PwXIXXEymu2aKHRJqtkCKyn2jxR_HpuIxGQ"
report_cell = "D"

s = get_sheet(report_sheet)
all_tabs = [(tab['properties']['title'], tab['properties']['sheetId']) for tab in s.get('sheets')]

class_tabs = [sheet for sheet in all_tabs if not sheet[0].startswith("Sentences")]
sentence_tabs = [sheet for sheet in all_tabs if sheet[0].startswith("Sentences")]

class_students = []

if run_app:
    app = Application("Report Card Generator")
    main_window = Window("Report Card Generator", 0, 0, 1000, 750)
    text = Label(main_window, "Test", main_window.width()/2, main_window.height()/2)

    class_label = Label(main_window, "Class: ", main_window.width() / 2.5, 15)
    class_dropdown = Dropdown(
        main_window,
        class_label.x() + class_label.width(),
        class_label.y() ,
        [tab[0] for tab in class_tabs]
    )



# sentences = get_sheet(report_sheet, "Sentences {}!A1:Z30".format(tabs[0][0][0]), "COLUMNS").get('values')


class Student:
    def __init__(self, name, classroom, report, row_index, gender):
        self.name = name
        self.classroom = classroom
        self.report = report
        self.row_index = row_index
        self.gender = gender

    def submit_report(self, report=None):
        global report_sheet
        global report_cell
        if not report: #Cannot pass self.params as arguments to a function, as self is defined in that scope
            report = self.report

        write_sheet(report_sheet, [[report]], "{}!{}{}".format(self.classroom, report_cell, self.row_index))


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
    if run_app: app.exec()
