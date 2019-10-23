import numpy as np
from numba import jit

class Vehicle():

    def __init__(self):
        self.id = None
        self.name = None
        self.controls = np.zeros(4)
        self.forces = np.zeros(3)
        self.moments = np.zeros(3)
        self.states = np.zeros(3)
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

    def loadKinematics(self, name):
        from kinematics import StandardKinematics
        self.kinematics = StandardKinematics.update

    def step(self, dt):
        return step_optimized(self.control, self.dynamics, self.kinematics, dt)

    def propagate(self, time, frequency):
        return propagate_optimized(self.control, self.dynamics, self.kinematics, time, frequency)


# Optimized functions (Numba)

@jit(nopython=True)
def step_optimized(control, dynamics, kinematics, dt):
    controls = control(np.ones((4), dtype=np.float32),
                       np.ones((7), dtype=np.float32))
    forces, moments = dynamics(controls, np.ones((7), dtype=np.float32),
                                         np.ones((26), dtype=np.float32),
                                         np.ones((19), dtype=np.float32))
    return kinematics(np.ones((18), dtype=np.float32), forces, moments, 5*np.random.rand((19)), dt)

@jit(nopython=True)
def propagate_optimized(control, dynamics, kinematics, time, frequency):
    for _ in range(time * frequency):
        step_optimized(control, dynamics, kinematics, 1 / frequency)
    return step_optimized(control, dynamics, kinematics, 1 / frequency)


test = Vehicle()
test.loadControl('whatever')
test.loadDynamics('whatever')
test.loadKinematics('whatever')
print(test.propagate(1, 100))