import tensorflow as tf
import numpy as np
import math


class BaseDataGenerator(tf.keras.utils.Sequence):

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

    def __get_slice__(self, arr, idx, num):
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
