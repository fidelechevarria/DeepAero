from numba import jit
import numpy as np

@jit(nopython=True)
def update(controls, states):
    return np.array([0, 0, 0, 1], dtype=np.float32)
