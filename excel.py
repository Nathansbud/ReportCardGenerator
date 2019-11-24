import openpyxl
#Todo: this

def get_excel_sheet(path):
    return openpyxl.load_workbook(path)

if __name__ == '__main__':
    sheet = get_excel_sheet('/Users/zackamiton/Desktop/Test.xlsx')
    sentences = []
    for s in sheet.sheetnames:
        if s.startswith("Sentences"):
            for column in sheet[s].columns:
                sentences.append([s.value for s in column[1:]])
    print(sentences)
