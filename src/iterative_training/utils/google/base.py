from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import json


class GoogleBase:

    credentials = None
    client_email = None

    def __read_client_email__(self):
        with open(self.credentials, "r") as f:
            data = json.load(f)
            self.client_email = data['client_email']

    def __get_sheets_service__(self):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials, scope)
        return build('sheets', 'v4', credentials=creds)

    def __get_drive_service__(self):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://www.googleapis.com/auth/drive.metadata.readonly',
                 'https://www.googleapis.com/auth/drive.file']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials, scope)
        return build('drive', 'v3', credentials=creds)
