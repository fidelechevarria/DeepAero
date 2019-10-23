import numpy as np
from numba import jit
import pandas as pd

class Vehicle():

    def __init__(self):
        self.id = None
        self.name = None
        self.controls = np.zeros((4), dtype=np.float32)
        self.forces = np.zeros((3), dtype=np.float32)
        self.moments = np.zeros((3), dtype=np.float32)
        self.states = np.zeros((3), dtype=np.float32)
        self.coefficients = None
        self.config = None
        self.control = None
        self.dynamics = None
        self.model = None
        self.kinematics = None

    def loadControl(self, name):
        from controls import ConstantControl
        self.control = ConstantControl.update

    def loadDynamics(self, name):
        from dynamics import AircraftEuler
        self.dynamics = AircraftEuler.update

    def loadModel(self, name):
        data = pd.read_csv(f'models/{name}.model', sep=' ', names=['coefficients', 'values'])
        self.coefficients = data['values'].values

    def loadKinematics(self, name):
        from kinematics import StandardKinematics
        self.kinematics = StandardKinematics.update

    def step(self, dt):
        return step_optimized(self.control, self.dynamics, self.kinematics, self.coefficients, dt)

    def propagate(self, time, frequency):
        return propagate_optimized(self.control, self.dynamics, self.kinematics, self.coefficients, time, frequency)


# Optimized functions (Numba)

@jit(nopython=True)
def step_optimized(control, dynamics, kinematics, coefficients, dt):
    controls = control(np.ones((4), dtype=np.float32),
                       np.ones((7), dtype=np.float32))
    forces, moments = dynamics(controls,
                               np.ones((7), dtype=np.float32), 
                               coefficients,
                               np.ones((19), dtype=np.float32))
    return kinematics(np.ones((18), dtype=np.float32),
                      forces,
                      moments,
                      5*np.random.rand((19)),
                      dt)

@jit(nopython=True)
def propagate_optimized(control, dynamics, kinematics, coefficients, time, frequency):
    for _ in range(time * frequency):
        step_optimized(control, dynamics, kinematics, coefficients, 1 / frequency)
    return step_optimized(control, dynamics, kinematics, coefficients, 1 / frequency)


test = Vehicle()
test.loadControl('whatever')
test.loadDynamics('whatever')
test.loadModel('ZivkoEdge540')
test.loadKinematics('whatever')
print(test.propagate(1, 100))