import unittest
import random
import pandas as pd

from .base import BaseEncoder


# TODO finish writing this test
class EncoderTester(unittest.TestCase):

    encoder = BaseEncoder()
    num_to_encode = random.randint(50, 100)
    test_data = df_positive.sample(n=num_to_encode)
    output_shape = (num_to_encode, 50, 26, 1)

    def test_expected_output_shape(self):
        data = self.encoder.encode(self.test_data)
        self.assertEqual(self.output_shape, data.shape)
