import pickle
import os.path
import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from util import index_to_column

def make_token(scope, cred_name):
    creds = None

    token_path = os.path.join(os.getcwd(), "credentials" + os.sep + cred_name + "_token.pickle")
    cred_path = os.path.join(os.getcwd(), "credentials" + os.sep + cred_name + ".json")

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, scope)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
sheets_token = make_token(scope=SCOPES, cred_name="sheets")
service = build('sheets', 'v4', credentials=sheets_token)

def get_sheet(sheet, r='', mode='ROWS'):
    if len(r) > 0:
        return service.spreadsheets().values().get(spreadsheetId=sheet, range=r, majorDimension=mode).execute()
    return service.spreadsheets().get(spreadsheetId=sheet).execute()

def write_sheet(sheet, values, r='', mode="ROWS", tab_id=None, option=None):
    if option is None: option={"operation":"write"}
    if 'operation' in option:
        if option['operation'] == "write":
            service.spreadsheets().values().update(spreadsheetId=sheet, range=r, valueInputOption="RAW", body={
                'values': values,
                'majorDimension': mode
            }).execute(),
        elif option['operation'] == "remove":
            if 'start' in option and 'end' in option:
                service.spreadsheets().batchUpdate(spreadsheetId=sheet, body={"requests": {
                    "deleteRange": {
                        "range": {
                            "sheetId": tab_id,
                            "startColumnIndex": option['start'],
                            "endColumnIndex": option['end']
                        },
                        "shiftDimension": "COLUMNS"
                    }
                }}).execute()
        elif option['operation'] == "insert":
            if 'start' in option and 'end' in option:
                service.spreadsheets().batchUpdate(spreadsheetId=sheet, body={"requests":{
                        "insertDimension":{
                            "range":{
                                "sheetId":tab_id,
                                "dimension":mode,
                                "startIndex":option['start'],
                                "endIndex":option['end']
                            },
                            "inheritFromBefore": True if option['start'] > 0 else False
                        },
                    }}).execute()

def make_report_sheet(title=None, tabs=None):
    if not tabs: tabs = []

    #added grade schemes now to avoid doing it later + ensure at least 1 sheet exists (so removal can be done on Sheet1)
    for tab in tabs:
        if 'title' in tab and tab['title'].startswith("Grade Scheme"):
            break
    else:
        tabs.append({"title":"Grade Schemes", "data":[]})

    today = datetime.datetime.now()
    report_spreadsheet = {'properties':{'title':title if title else f"Report Sheet {today.strftime('%B')} {today.year}"}}

    spreadsheet = service.spreadsheets().create(body=report_spreadsheet, fields='spreadsheetId').execute()
    if len(tabs) > 0:
        print(tabs)
        create_sheet_tabs = {"requests":[{
            "addSheet":{
                "properties":{
                    "title":t['title']
                }
            }} for t in tabs]}

        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet['spreadsheetId'], body=create_sheet_tabs).execute()
        for t in tabs:
            if 'data' in t and len(t['data']) > 0:
                max_width = max([len(r) for r in t['data']])
                r = f"'{t['title']}'!A1:{index_to_column(max_width)}{len(t['data'])}"
                service.spreadsheets().values().update(spreadsheetId=spreadsheet['spreadsheetId'], valueInputOption="RAW", range=r, body={
                    "majorDimension":"ROWS",
                    "values": t['data'],
                }).execute()

    #remove Sheet1
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet['spreadsheetId'], body={"requests":{"deleteSheet":{"sheetId":0}}}).execute()
    return spreadsheet['spreadsheetId']