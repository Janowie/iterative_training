import typing

import numpy
import numpy as np
import pandas as pd
from googleapiclient.http import MediaFileUpload

from .base import GoogleBase


class GoogleSheets(GoogleBase):

    def __init__(self, credentials, sheet_url):
        self.credentials = credentials
        self.service = self.__get_sheets_service__()
        self.spreadsheet_id = self.__get_spreadsheet_id__(sheet_url)

        # Current worksheet (tab)
        self.worksheet_title = None
        self.worksheet_id = None
        self.endRowIndex = 1  # Helper variable to keep track of where to start writing values

    @staticmethod
    def __get_spreadsheet_id__(sheet_url):
        """
        Splits sheet url (https://docs.google.com/spreadsheets/d/1Bjj2WZO1l_6ZEnyAnd94Ui7rrSKHjOF-1SJRDznfADI/edit#gid=218800792)
        by "/", returns the id part (1Bjj2WZO1l_6ZEnyAnd94Ui7rrSKHjOF-1SJRDznfADI)
        """
        return sheet_url.split("/")[-2]

    def get_sheet(self, sheet_id=None, sheet_title=None):

        """
        This function sets current worksheet within the "parent" sheet. Call this function before working with insert
        data or chart functions or if worksheet is needed.
        :param sheet_id:
        :param sheet_title:
        :return: worksheet object or None if not found
        """

        if sheet_id is None and sheet_title is None:
            return None

        spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()

        for _sheet in spreadsheet['sheets']:
            if (sheet_id and _sheet['properties']['sheetId'] == sheet_id) or \
                    (sheet_title and _sheet['properties']['title'] == sheet_title):
                self.worksheet_id = sheet_id
                self.worksheet_title = sheet_title

                return _sheet

        return None

    def create_sheet(self, title, rows, cols):
        resp = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body={"requests": [
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

        self.worksheet_title = title
        self.worksheet_id = resp['replies'][0]['addSheet']['properties']['sheetId']

    def remove_sheet(self, sheet_id):
        resp = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body={"requests": [
            {
                "deleteSheet": {
                    "sheetId": sheet_id
                }
            }
        ]
        }).execute()

    def insert_data(self, data: typing.Union[list, numpy.ndarray], row: int = 0, column: str = "B") -> dict:
        """
        Inserts rows into a sheet

        :param data:
        :param row:
        :param column:
        :return:
        """

        # Transform  column to uppercase
        column = column.upper()

        coords = {
            "startRowIndex": row - 1,  # indexes start at 0 not 1 !
            "endRowIndex": row + len(data) - 1,
            "startColumnIndex": ord(column) - 65,
            "endColumnIndex": ord(column) + len(data[0]) - 65
        }

        self.endRowIndex = row + len(data)

        # TODO: replace with ...values.append(...) ?
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.worksheet_title}!{column}{row}:{chr(ord(column) + len(data[0]))}{row + len(data)}",
            # range=f"{self.worksheet_title}!A1:Z1",
            valueInputOption="USER_ENTERED",
            body={
                "values": data
            }).execute()

        return coords

    @staticmethod
    def column_to_index(col):
        if isinstance(col, str):
            return ord(col) - 65
        return col

    def insert_chart(self,
                     data: pd.DataFrame = None,
                     title: str = "Chart",
                     chart_type: str = "LINE",
                     **kwargs) -> dict:

        """

        Insert data into the worksheet. Index is used as domain for chart, columns as individual series.

        :param data: pandas DataFrame with data to plot
        :param title: title of chart
        :param chart_type: one of: (BAR, LINE, AREA, COLUMN, SCATTER, COMBO, STEPPED_AREA)
        :param kwargs: data_offset, legend_x_title, legend_y_title, legend_position, ...
            data_offset can specify the offset used when inserting chart data
        :return: result dict
        """

        # TODO: add option to add data to a different sheet (better visual)

        # 1.)   Check if data is an instance of pandas DataFrame, if not, convert it
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data=data)

        # 2.)   Insert data into current sheet
        data_to_insert = data.values.tolist()

        data_offset = kwargs.get("data_offset", self.endRowIndex)

        data_to_insert.insert(0, list(data.columns))

        coords = self.insert_data(data_to_insert, row=data_offset, column=kwargs.get("data_column_letter", "B"))

        # 3.)   Prepare chart request body

        domain_source = {
            "sheetId": self.worksheet_id,
            "startRowIndex": coords['startRowIndex'],
            "endRowIndex": coords['endRowIndex'],
            "startColumnIndex": coords['startColumnIndex'],
            "endColumnIndex": coords['startColumnIndex'] + 1
        }

        series = list()

        for i, column in enumerate(data.columns, start=1):
            series.append({
                "series": {
                    "sourceRange": {
                        "sources": [
                            {
                                "sheetId": self.worksheet_id,
                                "startRowIndex": coords['startRowIndex'],
                                "endRowIndex": coords['endRowIndex'],
                                "startColumnIndex": coords['startColumnIndex'] + i,
                                "endColumnIndex": coords['startColumnIndex'] + i + 1
                            }
                        ]
                    }
                },
                "targetAxis": "LEFT_AXIS"
            })

        body = {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": title,
                        "basicChart": {
                            "chartType": chart_type,
                            "legendPosition": kwargs.get("legend_position", "BOTTOM_LEGEND"),
                            "axis": [
                                {
                                    "position": "BOTTOM_AXIS",
                                    "title": kwargs.get("legend_x_title", "x")
                                },
                                {
                                    "position": "LEFT_AXIS",
                                    "title": kwargs.get("legend_y_title", "y")
                                }
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                domain_source
                                            ]
                                        }
                                    }
                                }
                            ],
                            "series": series,
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": kwargs.get("worksheet_id", self.worksheet_id),
                                "rowIndex": kwargs.get("row_index", self.endRowIndex - len(data_to_insert)),
                                "columnIndex": self.column_to_index(kwargs.get("column", len(data_to_insert[0]) + 2)),
                            },
                        },
                    }
                }
            }
        }

        result = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={"requests": [body]}).execute()
        return result
