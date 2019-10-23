from numba import jit
import numpy as np

@jit(nopython=True)
def update(controls, states):
    return np.ones((4), dtype=np.float32)
