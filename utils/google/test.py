import unittest

from .drive import GoogleDrive


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

        link = gd.upload_file("test_drive.txt", "./test.txt",
                                       "https://drive.google.com/drive/u/0/folders/1HioXiaThtx4iectL27xeSkthOTMCfKa9")
        self.assertIsInstance(link, str)
