import numpy as np


def stack(matrix: np.ndarray, array: np.ndarray) -> np.ndarray:
    # add row to bottom
    matrix = np.vstack([matrix, array])

    # transform to column and add to right
    array = np.pad(array, (0, 1), 'constant').reshape(-1, 1)
    return np.hstack([matrix, array])
