from googleapiclient.http import MediaFileUpload

from .base import GoogleBase


class GoogleSheets(GoogleBase):

    def __init__(self, credentials, sheet_url):
        self.credentials = credentials
        self.service = self.__get_sheets_service__()
        self.sheet_id = self.__get_spreadsheet_id__(sheet_url)

    @staticmethod
    def __get_spreadsheet_id__(sheet_url):
        """
        Splits sheet url (https://docs.google.com/spreadsheets/d/1Bjj2WZO1l_6ZEnyAnd94Ui7rrSKHjOF-1SJRDznfADI/edit#gid=218800792)
        by "/", returns the id part (1Bjj2WZO1l_6ZEnyAnd94Ui7rrSKHjOF-1SJRDznfADI)
        """
        return sheet_url.split("/")[-2]

    def insert_data(self, sheet_title, data, row_offset):
        """
        Inserts rows into a sheet
        """

        COLUMN = "B"

        self.service.spreadsheets().values().update(
            spreadsheetId=self.sheet_id,
            range=f"{sheet_title}!{COLUMN}{row_offset}:{chr(ord(COLUMN) + len(data[0]))}{row_offset + len(data)}",
            valueInputOption="USER_ENTERED",
            body={
                "values": data
            }).execute()

    def create_sheet(self, title, rows, cols):
        resp = self.service.spreadsheets().batchUpdate(spreadsheetId=self.sheet_id, body={"requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": title,
                        "gridProperties": {
                            "rowCount": rows,
                            "columnCount": cols
                        },
                        # "tabColor": {
                        #   "red": 1.0,
                        #   "green": 0.3,
                        #   "blue": 0.4
                        # }
                    }
                }
            }
        ]
        }).execute()
        return resp['replies'][0]['addSheet']['properties']['sheetId']
