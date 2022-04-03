import cupy as cp


def stack(matrix: cp.ndarray, array: cp.ndarray) -> cp.ndarray:
    # add row to bottom
    matrix = cp.vstack([matrix, array])

    # transform to column and add to right
    array = cp.pad(array, (0, 1), 'constant').reshape(-1, 1)
    return cp.hstack([matrix, array])
