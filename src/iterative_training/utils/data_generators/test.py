import unittest
import random
import numpy as np

# Import tested class
import pandas as pd

from ..data_generators.base import BaseDataGenerator, BaseDataCreator


class TestDataGen(unittest.TestCase):

    ratio = (1, 4)
    batch_size = np.random.choice([32, 64, 256], size=1)[0]
    num_samples = random.randint(50, 100)

    positive = np.ones(num_samples)
    negative = np.zeros(len(positive) * ratio[1])
    data_gen = BaseDataGenerator(positive, np.ones(len(positive)),
                                 negative, np.zeros(len(negative)),
                                 ratio,
                                 batch_size)

    def test_correct_num_negative(self):
        self.assertEqual(len(self.positive) * self.ratio[1], len(self.negative))

    def test_class_ratio_in_batches(self):
        """
        Tests if class ratio is "met" in each (but last) batch of data
        :return: None
        """

        batch_x, batch_y = self.data_gen.__getitem__(random.randint(0, self.data_gen.__len__()-1))

        num_positive = sum(batch_y)
        num_negative = len(batch_y) - num_positive

        self.assertEqual(num_positive * self.ratio[1], num_negative * self.ratio[0])


class TestDataCreation(unittest.TestCase):

    def test_positive_dataset_creation(self):
        path = "./positive.csv"

        df_mirna = pd.read_csv("../data_generators/miR_Family_Info.csv").sample(n=1000, random_state=42)

        bc = BaseDataCreator()

        df = bc.make_dataset(mirna_df=df_mirna, store_dataset=path,
                             mutation_mode="positive_class", test=True)
        counts = df.groupby("mode").count()

        with self.subTest():
            self.assertAlmostEqual(counts.loc["noise"]["mirna"], 200, delta=10)

        with self.subTest():
            self.assertAlmostEqual(counts.loc["canonical_20"]["mirna"], 300, delta=10)

    def test_negative_dataset_creation(self):
        path = "./negative.csv"

        df_mirna = pd.read_csv("../data_generators/miR_Family_Info.csv").sample(n=1000, random_state=42)

        bc = BaseDataCreator()

        df = bc.make_dataset(mirna_df=df_mirna, store_dataset=path, n=10,
                             mutation_mode="negative_class", test=True)

        counts = df.groupby("mode").count()

        with self.subTest():
            self.assertAlmostEqual(counts.loc["noise"]["mirna"], 2000, delta=10)

        with self.subTest():
            self.assertAlmostEqual(counts.loc["canonical_20"]["mirna"], 3000, delta=10)
