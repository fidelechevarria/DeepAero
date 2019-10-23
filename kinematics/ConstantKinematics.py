from numba import jit
import numpy as np

@jit(nopython=True)
def update(states, forces, moments, dt):
    return states
