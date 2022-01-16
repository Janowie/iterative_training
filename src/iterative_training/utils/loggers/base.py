from datetime import datetime
import contextlib, io
import gspread
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials


class GoogleDriveLogger:

    def __init__(self, google_drive, google_sheets):
        self.gd = google_drive
        self.gs = google_sheets

    def log(self,
            title="",
            description="",
            model=None,
            evaluation_dict={},
            history={},
            iterative_training_conf={}):

        # Add new sheet for current experiment
        # TODO: Check if given sheet already exists => causes "APIError"
        self.gs.create_sheet(title, 100, 20)

        data = list()

        # Add date and title
        data.append([datetime.now().strftime('%Y/%m/%d, %H:%M:%S')])
        data.append([title])
        data.append([""])

        # Experiment description
        data.append([description])
        data.append([""])

        # Get model summary
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            model.summary()
        model_summary = f.getvalue()

        # Experiment model description
        data.append([model_summary])
        data.append([""])

        self.gs.insert_data(title, data, 2)

        # data = self.get_data_from_history(history)

        self.gs.insert_data(title, data, 10)
