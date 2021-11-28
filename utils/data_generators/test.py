import unittest
import random
import numpy as np

# Import tested class
from utils.data_generators.base import BaseDataGenerator


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
