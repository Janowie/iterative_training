import unittest

from .base import GSLogger


class LoggerTester(unittest.TestCase):

    logger = GSLogger(
        credentials="../loggers/credentials.json",
        sheet_url="https://docs.google.com/spreadsheets/d/1f8zGb_ebp301HsfJhS2QB0HnYm_azFUCmzCua7Z1DQU/edit",
        model_folder_url="https://drive.google.com/drive/u/0/folders/1HioXiaThtx4iectL27xeSkthOTMCfKa9"
    )

    def test_upload_to_google_drive(self):

        with open("test.txt", "w") as writer:
            writer.write("""
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

        self.logger.upload_file_to_drive("test_test.txt", "test.txt")

        self.assertEqual(True, True)
