from sklearn.model_selection import train_test_split
import numpy as np

from utils.data_generators.base import BaseDataGenerator


class BaseSampler:

    """
    The purpose of a sampler is to prepare training, validation and test data for model.
    """

    # ---------- Datasets | raw (not encoded => ne) ----------- #
    train_p_ne = None
    train_n_ne = None

    val_p_ne = None
    val_n_ne = None

    test_p_ne = None
    test_n_ne = None

    # ---------- Datasets | encoded ----------- #
    train_p = None
    train_n = None

    val_p = None
    val_n = None

    test_p = None
    test_n = None

    @staticmethod
    def __name__():
        return "Sampler"

    def __init__(self, negative_ratio, positive_dataset,
                 data_creator, encoder):
        """

        :param negative_ratio:  either a fixed ratio or scheduler (function that gets iteration as input
            and returns ratio)
        :param positive_dataset: dataset with non encoded mRNA and miRNA pairs
        :param data_creator:  generator that takes in positive samples and returns negative ones
        :param encoder:     object able to encode miRNA / mRNA into "one-hot encoding"
        """
        print("-" * 30)
        print(f" {self.__name__()}")
        print("-" * 30)

        # Utils
        self.creator = data_creator
        self.encoder = encoder

        self.negative_ratio = negative_ratio
        self.current_negative_ratio = None
        self.positive_dataset = positive_dataset

    @staticmethod
    def _get_ratio_(ratio, iteration):
        """
        Returns ratio positive, negative for current iteration. If passed ratio is a function, call it,
        else return static ratio.
        :param ratio:
        :param iteration:
        :return:
        """
        if isinstance(ratio, str):
            return ratio
        else:
            return ratio(iteration)

    def on_training_begin(self):

        self.current_negative_ratio = self._get_ratio_(self.negative_ratio, 0)

        # ------------------------------------------------------
        # Initial initialization

        if self.train_p_ne is None:

            positive_data = self.creator.make_dataset(mirna_df=self.positive_dataset,
                                                      mutation_mode="positive_class")
            negative_data = self.creator.make_dataset(mirna_df=self.positive_dataset,
                                                      n=self.current_negative_ratio,
                                                      mutation_mode="negative_class")

            self.train_p_ne, self.test_p_ne, self.train_n_ne, self.test_n_ne = train_test_split(positive_data,
                                                                                                negative_data,
                                                                                                test_size=0.2,
                                                                                                random_state=42)
            self.train_p_ne, self.val_p_ne, self.train_n_ne, self.val_n_ne = train_test_split(self.train_p_ne,
                                                                                              self.train_n_ne,
                                                                                              test_size=0.1,
                                                                                              random_state=42)
            # Encode data
            self.train_p = self.encoder.encode(self.train_p_ne)
            self.train_n = self.encoder.encode(self.train_n_ne)
            self.val_p = self.encoder.encode(self.train_p_ne)
            self.val_n = self.encoder.encode(self.val_n_ne)
            self.test_p = self.encoder.encode(self.test_p_ne)
            self.test_n = self.encoder.encode(self.test_n_ne)

    def on_training_end(self, model):
        """
        Evaluate current model and decide which data should be used in the next iteration.
        This function should be implemented in each experiment.
        :param model: current best model
        :return:
        """

        pass

    def get_data(self, batch_size):
        # Return data generators => train, valid, test
        # TODO: zmenit na dynamicke menenie ratia (ak je definovane)
        class_ratio = (1, self.current_negative_ratio)

        train_datagen = BaseDataGenerator(self.train_p, np.ones(len(self.train_p)),
                                          self.train_n, np.zeros(len(self.train_n)),
                                          class_ratio, batch_size)
        val_datagen = BaseDataGenerator(self.val_p, np.ones(len(self.val_p)),
                                        self.val_n, np.zeros(len(self.val_n)),
                                        class_ratio, batch_size)
        test_datagen = BaseDataGenerator(self.test_p, np.ones(len(self.test_p)),
                                         self.test_n, np.zeros(len(self.test_n)),
                                         class_ratio, batch_size)

        return train_datagen, val_datagen, test_datagen
