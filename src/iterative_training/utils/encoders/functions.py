import numpy as np


# TODO: proper documentation and typing hints!
def encode_ohe_matrix_2d(row, tensor_dim=(50, 26, 1)):  # , categories=False
    """
    fun transform input database to one hot encoding numpy array.

    parameters:
    df = Pandas df with col names "binding_sequence", "label", "mirna_binding_sequence"
    tensor_dim= 2d matrix shape

    output:
    2d dot matrix, labels as np array
    """

    row = row[1]

    # Check if input sequences have the expected length
    if (len(row['mrna']) > tensor_dim[0]) or (len(row['mirna']) > tensor_dim[1]):
        print(len(row['mrna']), tensor_dim[0], len(row['mirna']), tensor_dim[1])
        return None

    # alphabet for watson-crick interactions.
    alphabet = {"AT": 1., "TA": 1., "GC": 1., "CG": 1.}

    # initialize dot matrix with zeros
    ohe_matrix_2d = np.zeros(tensor_dim, dtype="float32")

    # compile matrix with watson-crick interactions.
    for bind_index, bind_nt in enumerate(row['mrna'].upper()):

        for mirna_index, mirna_nt in enumerate(row['mirna'].upper()):
            base_pairs = bind_nt + mirna_nt
            ohe_matrix_2d[bind_index, mirna_index, 0] = alphabet.get(base_pairs, 0)

    return ohe_matrix_2d
