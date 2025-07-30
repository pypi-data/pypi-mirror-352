import numpy as np


def to_np_array(p):
    if isinstance(p, np.ndarray):
        return p
    return np.array(p)
