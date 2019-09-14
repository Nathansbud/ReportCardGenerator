import re
import sys
import os
import json

from cuter import Application, Window, Button, Label, Input, Dropdown, Textarea #Pared down versions of ^, to reduce cluttered code
from googleapi import get_sheet, write_sheet

'''
    First Name: A
    Last Name: B
    Gender: C 
    Report: D
'''

pronouns = {
    "M":["he", "his", "him", "his"],
    "F":["she", "her" , "her", "hers"],
    "T":["they", "their" , "them", "theirs"]
}

report_sheet = "1ermre2z1PwXIXXEymu2aKHRJqtkCKyn2jxR_HpuIxGQ"
s = get_sheet(report_sheet).get('sheets')


tabs = [(tab['properties']['title'], tab['properties']['sheetId']) for tab in s if not tab['properties']['title'].startswith("Sentences")]
entries = get_sheet(report_sheet, "{}!A2:Z30".format(tabs[0][0])).get('values')
sentences = get_sheet(report_sheet, "Sentences {}!A1:Z30".format(tabs[0][0][0]), "COLUMNS").get('values')

app = Application("Report Card Generator")
main_window = Window("Report Card Generator", 0, 0, 1000, 750, True)

class_label = Label(main_window, "Class: ", main_window.width()/2.5, 15)
class_dropdown = Dropdown(main_window, class_label.x() + class_label.width(), class_label.y() - 0.25*class_label.height(), [tab[0] for tab in tabs])

name_label = Label(main_window, "Name: ", 50, 75)
name_dropdown = Dropdown(main_window, name_label.x() + name_label.width(), name_label.y() - 0.25*name_label.height(), [e[0] for e in entries])

gender_label = Label(main_window, "Gender: " + entries[0][2], 50, 100)

sentence_label = []
sentence_dropdown = []


count = 0
for entry in sentences:
    if len(entry) > 1:
        pl = Label(main_window, "Sentence " + str(count + 1) + ": ", 50, 125 + 25 * count)
        sentence_label.append(
            pl)  # This is on 2 lines rather than one as a parent variable must exist for C++ binding to correctly function
        pd = Dropdown(main_window, sentence_label[count].x() + sentence_label[count].width(),
                      sentence_label[count].y() - 0.25 * sentence_label[count].height(), entry[1:])
        sentence_dropdown.append(pd)
        count += 1

report_area = Textarea(main_window, (entries[0][3] if len(entries[0]) >= 4 else ""), 0, 450, main_window.width(), 250)
generate_button = Button(main_window, "Generate", main_window.width()/2 - 20, 410)
submit_button = Button(main_window, "Submit", main_window.width()/2 - 20, 710)

# def update_sentences():
#     global sentence_label
#     global sentence_dropdown
#     global class_dropdown
#
#     sentences = get_sheet(report_sheet, "Sentences {}!A1:Z30".format(grade), "COLUMNS").get('values')
#
#     if len(sentence_label) > 0:
#         for l in sentence_label:
#             sentence_label.remove(l)
#             l.deleteLater()
#     if len(sentence_dropdown) > 0:
#         for d in sentence_dropdown:
#             sentence_dropdown.remove(d)
#             d.deleteLater()
#
#     # count = 0
#     # for entry in sentences:
#     #     if len(entry) > 1:
#     #         pl = Label(main_window, "Sentence " + str(count + 1) + ": ", 50, 125 + 25 * count)
#     #         sentence_label.append(pl) #This is on 2 lines rather than one as a parent variable must exist for C++ binding to correctly function
#     #         pd = Dropdown(main_window, sentence_label[count].x() + sentence_label[count].width(),
#     #                      sentence_label[count].y() - 0.25 * sentence_label[count].height(), entry[1:])
#     #         sentence_dropdown.append(pd)
#     #         count += 1
#
# update_sentences()

def update_entries():
    global entries
    global name_dropdown

    en = get_sheet(report_sheet, "{}!A2:D30".format((class_dropdown.currentText())))
    entries = en.get('values')

    name_dropdown.clear()
    name_dropdown.addItems([e[0] for e in entries])

    update_report()


def update_report():
    global entries
    global gender_label
    global report_area
    global name_dropdown

    gender_label.setText("Gender: " + entries[name_dropdown.currentIndex()][2])
    report_area.setText(entries[name_dropdown.currentIndex()][3] if len(entries[name_dropdown.currentIndex()]) >= 4 else "")

def update_cell():
    write_sheet(report_sheet, [[report_area.toPlainText()]], "{}!D{}".format(class_dropdown.currentText(), name_dropdown.currentIndex()+2))
    pass

def generate_report():
    report_area.setText("")
    for sentence in sentence_dropdown:
        report_area.setText(report_area.toPlainText() + replace_generics(sentence.currentText(), name_dropdown.currentText(), entries[name_dropdown.currentIndex()][2]) + " ")

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

class_dropdown.currentIndexChanged.connect(update_entries)
name_dropdown.currentIndexChanged.connect(update_report)
generate_button.clicked.connect(generate_report)
submit_button.clicked.connect(update_cell)


if __name__ == '__main__':
    app.exec()
    pass

