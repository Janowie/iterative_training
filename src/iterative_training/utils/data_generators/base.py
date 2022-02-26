import typing

import tensorflow as tf
import numpy as np
import pandas as pd
import math
from random import randint, sample


class BaseDataGenerator(tf.keras.utils.Sequence):
    """
    This class feeds training data to keras model. It does not generate new samples - this functionality
    is provided by other classes.
    """

    def __init__(self,
                 x_set_positive, y_set_positive,
                 x_set_negative, y_set_negative,
                 class_ratio,
                 batch_size):
        self.x_positive, self.y_positive = x_set_positive, y_set_positive
        self.x_negative, self.y_negative = x_set_negative, y_set_negative

        # Figure out how many positive and negative samples to include in batches
        class_ratio_positive, class_ratio_negative = class_ratio
        self.positive_in_batch = int(
            class_ratio_positive * (batch_size / (class_ratio_positive + class_ratio_negative)))
        self.negative_in_batch = int(
            class_ratio_negative * (batch_size / (class_ratio_positive + class_ratio_negative)))

        self.batch_size = batch_size

    def __len__(self):
        """
        Returns the total number of batches.
        """
        return math.ceil((len(self.y_positive) + len(self.y_negative)) / self.batch_size)

    @staticmethod
    def __get_slice__(arr, idx, num):
        return arr[idx * num: (idx + 1) * num]

    def __getitem__(self, idx):
        """
        Returns one batch with positive and negative examples specified by
        the "class_ratio".
        """

        batch_x_positive = self.__get_slice__(self.x_positive, idx, self.positive_in_batch)
        batch_y_positive = self.__get_slice__(self.y_positive, idx, self.positive_in_batch)

        batch_x_negative = self.__get_slice__(self.x_negative, idx, self.negative_in_batch)
        batch_y_negative = self.__get_slice__(self.y_negative, idx, self.negative_in_batch)

        # Concat and shuffle samples
        batch_x = np.concatenate([batch_x_positive, batch_x_negative], axis=0)
        np.random.seed(idx)
        np.random.shuffle(batch_x)

        batch_y = np.concatenate([batch_y_positive, batch_y_negative], axis=0)
        np.random.seed(idx)
        np.random.shuffle(batch_y)

        return batch_x, batch_y


class BaseDataCreator:
    """
    This base class provides base methods for creating samples.
    """

    @staticmethod
    def get_mutation_rate(mode):
        """
        Create array of probabilities of mutating each nucleotide in the miRNA sequence based on the mode.
        :param mode:
            - canonical_perfect - 2-7nt 0 mutation rate, others 0.8
            - canonical_20 - 2-7nt 0.1 mutation rate, others 0.8
            - non_canonical - from random position between 1, 6 following 4 nt have 0 mutation probability,
            from random position between 16, 23 following 4 nt have 0 mutation probability, others 0.8
            - noise - 1.0 mutation probability,
        :return: array of probabilities of mutation
        """
        mutation_rate = np.ones(22)

        # 20% "Canonical Seed 0% (perfect)" (i.e. pos 2-7 = 0%, other = 100 % mut.rate)
        if mode == "canonical_perfect":
            for i in range(2, 8):
                mutation_rate[i] = 0

        # 30% "Canonical Seed 20% (mismatch)" (i.e. pos 2-7 = 20%, other = 100 % mut.rate)
        elif mode == "canonical_20":
            for i in range(2, 8):
                mutation_rate[i] = 0.2

        # 30% "Non-canonical Seed Complementary" (i.e. within pos 1-9 have 3-5 consecutive nt at 0%. AND within pos
        # 12-20 another 3-5 consecutive at 20%. Rest 100% mut.rate)
        elif mode == "non_canonical":
            start = randint(0, 6)
            end = randint(12, 15)

            for i in range(start, start + 4):
                mutation_rate[i] = 0
            for i in range(end, end + randint(4, 6)):
                mutation_rate[i] = 0.2

        # 20% "Noise" (i.e. 100% mut. rate)
        elif mode == "noise":
            pass

        return mutation_rate

    @staticmethod
    def create_target(mirna, mutation_rate, target_len=50):
        """
        Function to create target sequence based on miRNA sequence and mutation rate.
        :param mirna: - miRNA sequence
        :param mutation_rate: - array with probabilities of mutation of mirna sequence
        :param target_len: int -> length of generated target mRNA
        :return: mRNA target; reverse complement miRNA based on probabilities,
        pad to the length of TARGET_LEN
        """

        alphabet = ["A", "C", "G", "T"]
        complementarity = {
            "A": "T",
            "T": "A",
            "C": "G",
            "G": "C"
        }

        tmp_mrna = ""
        for i in range(len(mirna)):
            if randint(0, 100) / 100 <= mutation_rate[i]:
                choice = set(alphabet).difference(set(mirna[i]))
                tmp_mrna = tmp_mrna + sample(list(choice), 1)[0]
            else:
                tmp_mrna = tmp_mrna + mirna[i]

        mrna = ""
        for nt in tmp_mrna:
            mrna = complementarity[nt] + mrna
        random_sequence = ''.join(np.random.choice(alphabet, target_len - len(mirna), replace=True))
        random_point = randint(0, target_len - len(mirna))
        mrna = random_sequence[0:random_point] + mrna + random_sequence[random_point:(target_len - len(mirna))]

        return mrna, random_point

    def make_dataset(self,
                     mirna_df=None,
                     store_dataset=None,
                     n=1,
                     target_len=50,
                     mutation_mode=None,
                     include_mutation_mode=False,
                     include_seed_start=False,
                     mirna_column_name='Mature sequence',
                     **kwargs):
        """
        Main function of the program. Go through input miRNA file and for each sequence based on given mode
        create N artificial targets. Output miRNAs and mRNAs to two separate tsv files.

        :param mirna_df: pandas.DataFrame with mirnas
        :param store_dataset: str => path where created dataset should be stored (if None is passed, dataset will not
        be stored).
        :param n: int => number of samples created from each mirna
        :param target_len: int => len of output mrna target sequence
        :param mutation_mode: str => either specific mode or "positive_class"
        :param include_mutation_mode: mutation applied to each sequence returned with it
        :param include_seed_start: seed start (starting position) returned with it
        :param mirna_column_name: str => column name to use from mirna_df
        :return: pandas.DataFrame
        """

        output = {
            "mirna": [],
            "mrna": []
        }

        if include_mutation_mode is True:
            output['mutation'] = []
        if include_seed_start is True:
            output['seed_start'] = []

        percent = lambda a, b: a / b * 100

        for i, index_row in enumerate(mirna_df.iterrows()):

            _, row = index_row

            mode = None

            if mutation_mode == "negative_class":
                mode = "noise"
            elif mutation_mode == "positive_class":

                p = percent(i, len(mirna_df))

                if p < 20:
                    mode = "canonical_perfect"
                elif 20 <= p < 50:
                    mode = "canonical_20"
                elif 50 <= p < 80:
                    mode = "non_canonical"
                else:
                    mode = "noise"

            if len(row[mirna_column_name]) <= 22:
                for _ in range(n):
                    mutation_rate = self.get_mutation_rate(mode)

                    # Replace U => T
                    mirna = row[mirna_column_name].replace('U', 'T')

                    output['mirna'].append(mirna)
                    target, seed_start = self.create_target(mirna, mutation_rate, target_len=target_len)
                    output['mrna'].append(target)

                    if include_mutation_mode is True:
                        output['mutation'].append(mode)
                    if include_seed_start is True:
                        output['seed_start'].append(seed_start)

        # Create pd.DataFrame from data
        df = pd.DataFrame(data=output)

        if store_dataset is not None:
            df.to_csv(path_or_buf=store_dataset, index=False)

        return df
