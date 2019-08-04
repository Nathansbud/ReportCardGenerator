from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit
from PyQt5.QtCore import Qt, QEvent

from cuter import Button, Window, Label, Input, Dropdown, Textarea #Pared down versions of ^, to reduce cluttered code
from googleapi import get_sheet

# class Student:
#     def __init__(self, first_name, last_name, gender, report):
#         self.first_name = first_name
#         self.last_name = last_name
#         self.gender = gender
#         self.report = report
# 
# students = []

report_sheet = "1ermre2z1PwXIXXEymu2aKHRJqtkCKyn2jxR_HpuIxGQ"
s = get_sheet(report_sheet).get('sheets')

tabs = [(tab['properties']['title'], tab['properties']['sheetId']) for tab in s[1:]]
entries = get_sheet(report_sheet, "{}!A2:D30".format(tabs[0][0])).get('values')


app = QApplication([])
app.setApplicationName("Report Card Generator")

main_window = Window("Report Card Generator", 0, 0, 500, 750)

class_label = Label(main_window, "Class: ", main_window.width()/2.5, 15)
class_dropdown = Dropdown(main_window, class_label.x() + class_label.width(), class_label.y() - 0.25*class_label.height(), [tab[0] for tab in tabs])

name_label = Label(main_window, "Name: ", 50, 75)
name_dropdown = Dropdown(main_window, name_label.x() + name_label.width(), name_label.y() - 0.25*name_label.height(), [e[0] for e in entries])

gender_label = Label(main_window, "Gender: " + entries[0][2], 50, 100)
report_area = Textarea(main_window, entries[0][3] if len(entries) >= 3 else "", 0, 450, main_window.width(), 250)

generate_button = Button(main_window, "Generate", main_window.width()/2 - 20, 410)
submit_button = Button(main_window, "Submit", main_window.width()/2 - 20, 710)

def update_entries():
    global entries
    global name_dropdown

    entries = get_sheet(report_sheet, "{}!A2:D30".format((class_dropdown.currentText()))).get('values')
    name_dropdown.deleteLater()
    name_dropdown = Dropdown(main_window, name_label.x() + name_label.width(), name_label.y() - 0.25*name_label.height(), [e[0] for e in entries])
    update_report()

def update_report():
    global entries
    global gender_label
    global report_area
    global name_dropdown

    gender_label.setText("Gender: " + entries[name_dropdown.currentIndex()][2])
    report_area.deleteLater()
    report_area = Textarea(main_window, entries[name_dropdown.currentIndex()][3] if len(entries) >= 4 else "", 0, 450, main_window.width(), 250)

def update_cell():
    print("Should trigger an update to the spreadsheet!")
    pass

def generate_report():
    pass

class_dropdown.currentIndexChanged.connect(update_entries)
name_dropdown.currentIndexChanged.connect(update_report)
generate_button.clicked.connect(generate_report)
submit_button.clicked.connect(update_cell)

if __name__ == '__main__':
    app.exec()
    pass

