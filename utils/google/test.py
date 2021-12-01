import unittest
import os

import pandas as pd

from .drive import GoogleDrive
from .sheets import GoogleSheets


class GoogleDriveTester(unittest.TestCase):

    def test_file_upload_test(self):
        with open("test.txt", "w") as writer:
            writer.write("""
            THIS IS A TEST FILE! PLEASE DELETE ME IF YOU SEE ME...
            
            Commodi deserunt ullam culpa laudantium culpa velit. Tempora et praesentium numquam tenetur minima. 
            Maxime a voluptate adipisci. Pariatur quam officiis consequatur. Totam illo nemo dolore vero est sed. 
            Doloribus asperiores asperiores enim eveniet fuga. Qui et dignissimos est in dolores. Maiores maiores ad 
            maxime reiciendis exercitationem laboriosam et ex. Eos dolores voluptas aperiam exercitationem non impedit.

            Veritatis aut explicabo dolores rem asperiores qui. Qui illo qui accusantium eaque officiis qui. 
            Magnam error hic ullam dolor eius.

            Est adipisci et minima excepturi et commodi nulla. Dignissimos assumenda sed velit accusantium est. 
            Perspiciatis quia dolorem corrupti voluptas aspernatur sit. Ullam qui sed debitis consequatur fuga 
            cupiditate quasi magni. Maiores non sit omnis asperiores amet ducimus dolor.

            Maxime dolores tempora ullam debitis. Voluptatem maiores amet qui nihil odio. Molestias architecto hic 
            tempore. Adipisci excepturi nihil recusandae quas quia nam ab sint. 
            Rerum voluptatem pariatur est ipsa nulla.
            """)

        gd = GoogleDrive(credentials="../credentials.json")

        file = "./test.txt"

        drive_file = gd.upload_file("test_drive.txt", file,
                                    "https://drive.google.com/drive/u/0/folders/1HioXiaThtx4iectL27xeSkthOTMCfKa9")

        if os.path.exists(file):
            os.remove(file)
            gd.delete_file(drive_file['id'])

        self.assertIsInstance(drive_file, dict)


class GoogleSheetsTester(unittest.TestCase):

    def test_logging(self):
        gs = GoogleSheets(credentials="../credentials.json",
                          sheet_url="https://docs.google.com/spreadsheets/d/1f8zGb_ebp301HsfJhS2QB0HnYm_azFUCmzCua7Z1DQU/edit#gid=58332320")

        df = pd.DataFrame(data={
            "Sales - Jan": [68,97,27,46,75,74],
            "Sales - Feb": [74,76,49,44,68,52],
            "Sales - Mar": [60,88,32,67,87,62],
            "Total Sales": [202,261,108,157,230,188]
        })
        # , index=["1.12.","2.12.","3.12.","4.12.","5.12.","6.12."]

        _ = gs.create_sheet("Test Worksheet", 50, 50)
        result = gs.insert_chart(data=df, title="Company sales", chart_type="LINE",
                                 legend_x_title="Date", legend_y_title="Sales")
        print(result)

        self.assertIsInstance(result, dict)
