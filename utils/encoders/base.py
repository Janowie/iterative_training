from multiprocessing import Pool
import numpy as np

# Annotations
import numpy.typing as npt

# Custom functions
from .functions import encode_ohe_matrix_2d


# TODO: proper documentation and typing hints!
class BaseEncoder:

    def __init__(self, func=encode_ohe_matrix_2d, tensor_dim=(50, 26, 1)):
        self.tensor_dim = tensor_dim
        self.func = func

    def __call_func__(self, x):
        """
        Helper function to call the "encoding function" supplied with the "tensor_dim" param.
        :param x: df row
        :return: ndarray
        """
        return self.func(x, tensor_dim=self.tensor_dim)

    def encode(self, df) -> npt.NDArray[np.bool_]:
        """
        Applies func to given df.
        :param df: pandas DataFrame to be encoded by func
        :return: ndarray (with encoded df)
        """

        with Pool() as executor:

            ohe_matrix = []

            # execute tasks concurrently and process results in order
            for result in executor.map(self.__call_func__, df.iterrows()):
                # report the result
                if result is not None:
                    ohe_matrix.append(result)

        return np.stack(ohe_matrix, axis=0)
