import unittest
import random
import pandas as pd
import numpy as np

from .base import BaseEncoder


class EncoderTester(unittest.TestCase):

    encoder = BaseEncoder()
    num_to_encode = random.randint(50, 100)
    output_shape = (num_to_encode, 50, 26, 1)

    def generate_dummy_df(self):
        mrna = list()
        mirna = list()

        for i in range(self.num_to_encode):
            mrna.append("".join(np.random.choice(['A', 'T', 'G', 'C'], size=50)))
            mirna.append("".join(np.random.choice(['A', 'T', 'G', 'C'], size=26)))

        return pd.DataFrame(data={
            "mrna": mrna,
            "mirna": mirna
        })

    def test_expected_output_shape(self):
        test_data = self.generate_dummy_df()
        data = self.encoder.encode(test_data)
        self.assertEqual(self.output_shape, data.shape)
