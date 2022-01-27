from datetime import datetime
import contextlib
import io
import pandas as pd
import numpy as np
from sklearn import metrics


class GoogleDriveLogger:

    def __init__(self, google_drive=None, google_sheets=None):
        self.gd = google_drive
        self.gs = google_sheets

        self.data_sheet = {
            "title": "",
            "id": ""
        }

        self.display_sheet = {
            "title": "",
            "id": ""
        }

    def log(self,
            title="",
            description="",
            model=None,
            save_model=True,
            sampler=None,
            evaluation_functions=[],
            history=None,
            gd_folder_url=None,
            saved_model_path=None,
            experiment_link=None,
            chart_anchor_column="J",
            iterative_training_conf=None):

        """

        :param title:
        :param description:
        :param model:
        :param save_model:
        :param sampler:
        :param evaluation_functions: array of callables taking arguments y_pred, y_true. Each will be added.
        :param history:
        :param gd_folder_url:
        :param saved_model_path:
        :param experiment_link:
        :param chart_anchor_column:
        :param iterative_training_conf:
        :return:
        """

        # Add new sheet for current experiment
        # TODO: Check if given sheet already exists => causes "APIError"

        # Create the main sheet for displaying results

        self.gs.create_sheet(title, 100, 20)
        self.display_sheet['title'] = title
        self.display_sheet['id'] = self.gs.worksheet_id

        # Create "helper" sheet for storing data
        self.gs.create_sheet(f"{title} => data", 100, 20)
        self.data_sheet['title'] = f"{title} => data"
        self.data_sheet['id'] = self.gs.worksheet_id

        # Switch to data sheet
        self.gs.worksheet_id = self.display_sheet['id']
        self.gs.worksheet_title = self.display_sheet['title']
        self.gs.endRowIndex = 1

        data = list()

        # Add date and title
        data.append(["Date:", datetime.now().strftime('%Y/%m/%d, %H:%M:%S')])
        data.append(["Title:", title])
        data.append([""])

        # Experiment description
        data.append(["Description:", description])
        data.append([""])

        # Experiment and trained model links
        if experiment_link is not None:
            data.append(["Ntb. link: ", experiment_link])
            data.append([""])

        if sampler is not None:

            predictions_proba = model.predict(np.concatenate((sampler.test_n, sampler.test_p)))
            labels = np.concatenate((np.zeros(len(sampler.test_n)), np.ones(len(sampler.test_p))))

            # Evaluate - precision, recall
            predictions = np.zeros(len(predictions_proba))
            predictions[np.reshape(predictions_proba, (len(predictions_proba))) >= 0.5] = 1

            if len(evaluation_functions):
                data.append(["Evaluation"])

                for fun in evaluation_functions:
                    data.append([str(fun.__name__), str(fun(predictions, labels))])

            data.append([""])

        # Save model to drive and include link
        if save_model is True:
            url = self.gd.upload_file(f"model_{title}_{datetime.now().strftime('%Y%m%d_%H:%M:%S')}",
                                      saved_model_path,
                                      gd_folder_url)["webViewLink"]
            data.append(["Model link: ", url])
            data.append([""])

        # Get model summary
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            model.summary()
        model_summary = f.getvalue()

        # Experiment model description
        data.append(["Model Summary:", model_summary])
        data.append([""])

        self.gs.insert_data(data, 2, "B")

        # Switch to data sheet
        self.gs.worksheet_id = self.data_sheet['id']
        self.gs.worksheet_title = self.data_sheet['title']
        self.gs.endRowIndex = 1

        if sampler is not None:

            # Insert ROC AUC
            fpr, tpr, _ = metrics.roc_curve(
                labels, predictions_proba
            )

            auc = metrics.roc_auc_score(np.concatenate((np.zeros(len(sampler.test_n)), np.ones(len(sampler.test_p)))),
                                        predictions_proba)
            df_roc = pd.DataFrame(data={
                'False Positive Rate': fpr,
                'True Positive Rate': tpr
            })
            self.gs.insert_chart(data=pd.DataFrame(data=df_roc),
                                 title=f"AUC - {auc}",
                                 chart_type="LINE",
                                 legend_x_title="False Positive Rate",
                                 legend_y_title="True Positive Rate",
                                 worksheet_id=self.display_sheet['id'],
                                 row_index=5,
                                 column=chart_anchor_column
                                 )

        if history is not None:
            # Insert history
            df_history = pd.DataFrame(data=history)
            df_history.reset_index(inplace=True)
            df_history.rename(columns={"index": "epochs"}, inplace=True)
            self.gs.insert_chart(data=df_history,
                                 title="History",
                                 chart_type="LINE",
                                 legend_x_title="Epoch",
                                 legend_y_title="Value",
                                 worksheet_id=self.display_sheet['id'],
                                 row_index=2,
                                 column=chart_anchor_column
                                 )
