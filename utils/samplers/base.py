class BaseSampler:

    """
    The purpose of a sampler is to prepare training and validation data for model.
    """

    # ---------- Datasets | raw ----------- #
    train_p_x = None
    train_p_y = None
    train_n_x = None
    train_n_y = None

    val_p_x = None
    val_p_y = None
    val_n_x = None
    val_n_y = None

    test_p_x = None
    test_p_y = None
    test_n_x = None
    test_n_y = None

    # ---------- Datasets | encoded ----------- #
    train_p_x_e = None
    train_p_y_e = None
    train_n_x_e = None
    train_n_y_e = None

    val_p_x_e = None
    val_p_y_e = None
    val_n_x_e = None
    val_n_y_e = None

    test_p_x_e = None
    test_p_y_e = None
    test_n_x_e = None
    test_n_y_e = None

    @staticmethod
    def __name__():
        return "Sampler"

    def __init__(self, negative_ratio, positive_dataset,
                 negative_generator, encoder):
        print("-" * 30)
        print(f" {self.__name__()}")
        print("-" * 30)

        # Utils
        self.gen = negative_generator
        self.encoder = encoder

        self.negative_ratio = negative_ratio

        self.positive_dataset = positive_dataset
        self.negative_dataset = None

    def on_training_end(self):
        pass

    def _split_train_val_test_(self,
                               x, y,
                               random_state=42,
                               split_ratio=(0.2, 0.1)):
        """
        Helper function to split data into train, val and test
        """
        frac_val, frac_test = split_ratio

        x_train, x_test, y_train, y_test = train_test_split(x, y,
                                                            test_size=frac_test,
                                                            random_state=random_state)
        x_train, x_val, y_train, y_val = train_test_split(x_train, y_train,
                                                          test_size=frac_val,
                                                          random_state=random_state)

        return (x_train, y_train), (x_val, y_val), (x_test, y_test)

    def split(self):
        """
        This function init the variables with data
        """
        pass

    def get_data(self):
        # Return data generators => train, valid, test
        train_datagen = DataGenerator(X_train_p, y_train_p,
                                      X_train_n, y_train_n,
                                      class_ratio, batch_size)
        valid_datagen = DataGenerator(X_val_p, y_val_p,
                                      X_val_n, y_val_n,
                                      class_ratio, batch_size)
        test_datagen = DataGenerator(X_test_p, y_test_p,
                                     X_test_n, y_test_n,
                                     class_ratio, batch_size)

        return train_datagen, valid_datagen, test_datagen
