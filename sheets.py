import pickle
import os.path
import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def make_token(scope, cred_name):
    creds = None

    token_path = os.path.join(os.path.dirname(__file__), "credentials" + os.sep + cred_name + "_token.pickle")
    cred_path = os.path.join(os.path.dirname(__file__), "credentials" + os.sep + cred_name + ".json")

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


def get_sheet(sheet, r='', mode='ROWS'):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    sheets_token = make_token(scope=SCOPES, cred_name="sheets")
    service = build('sheets', 'v4', credentials=sheets_token)
    if len(r) > 0:
        return service.spreadsheets().values().get(spreadsheetId=sheet, range=r, majorDimension=mode).execute()
    return service.spreadsheets().get(spreadsheetId=sheet).execute()

def write_sheet(sheet, values, r='', mode="ROWS", tab_id=None, option=None):
    if option is None: option={"operation":"write"}
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    sheets_token = make_token(scope=SCOPES, cred_name="sheets")
    service = build('sheets', 'v4', credentials=sheets_token)
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

def make_sheet(title=None):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    sheets_token = make_token(scope=SCOPES, cred_name="sheets")
    service = build('sheets', 'v4', credentials=sheets_token)
    today = datetime.datetime.now()
    month, year = today.strftime("%B"), today.year
    report_spreadsheet = {
        'properties':{
            'title':title if title else f"Report Sheet {month} {year}"
        }
    }

    spreadsheet = service.spreadsheets().create(body=report_spreadsheet, fields='spreadsheetId').execute()


if __name__ == '__main__':
    make_sheet()
