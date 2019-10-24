import numpy as np
from numba import jit
import pandas as pd

class Vehicle():

    def __init__(self):
        self.id = None
        self.name = None
        self.controls = np.array([0, 0, 0, 1], dtype=np.float32) #TODO: Add init functions for all elements
        self.forces = np.zeros((3), dtype=np.float32)
        self.moments = np.zeros((3), dtype=np.float32)
        self.states = np.array([0, 0, 600, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0.05, 0, 50, 40, 0], dtype=np.float32)
        self.parameters = np.array([750, 9.8056, 9.84, 7.87, 1.25, 3531.9, 2196.4, 4887.7, 0, 7000, 1.225, 0, 0, 0, 0, 0, 0.1, 0.1, 1], dtype=np.float32)
        self.coefficients = None
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
        self.coefficients = data['values'].values.astype(np.float32)

    def loadKinematics(self, name):
        from kinematics import StandardKinematics
        self.kinematics = StandardKinematics.update

    def step(self, dt):
        return step_optimized(self.control, self.dynamics, self.kinematics, self.states, self.controls, self.coefficients, self.parameters, dt)

    def propagate(self, time, frequency):
        return propagate_optimized(self.control, self.dynamics, self.kinematics, self.states, self.controls, self.coefficients, self.parameters, time, frequency)

# Optimized functions (Numba)
@jit(nopython=True)
def step_optimized(control, dynamics, kinematics, states, controls, coefficients, parameters, dt):
    controls = control(controls, states)
    forces, moments = dynamics(controls, states, coefficients, parameters)
    return kinematics(states, forces, moments, parameters, dt)

@jit(nopython=True)
def propagate_optimized(control, dynamics, kinematics, states, controls, coefficients, parameters, time, frequency):
    for _ in range(time * frequency):
        states = step_optimized(control, dynamics, kinematics, states, controls, coefficients, parameters, 1 / frequency)
    return states


test = Vehicle()
test.loadControl('whatever')
test.loadDynamics('whatever')
test.loadModel('ZivkoEdge540')
test.loadKinematics('whatever')
print(test.propagate(1, 100))