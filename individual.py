from modules.dynamic_model import Model
import numpy as np
import pandas as pd

class Individual():

    def __init__(self, aero):
        self.vehicle = Model(aero=aero)
        self.fitness = np.inf

    def __str__(self):
        return str(f'Individual fitness: {self.fitness:.2f}')

    def evaluate(self, traj):
        self.fitness = 0
        for idx in range(traj.shape[0]):
            if idx == 0:
                self.vehicle.roll = traj['roll'][0]
                self.vehicle.pitch = traj['pitch'][0]
                self.vehicle.yaw = traj['yaw'][0]
                self.vehicle.posNorth = traj['posNorth'][0]
                self.vehicle.posEast = traj['posEast'][0]
                self.vehicle.alt = - traj['posDown'][0]
                self.vehicle.vx = traj['vx'][0]
                self.vehicle.vy = traj['vy'][0]
                self.vehicle.vz = - traj['vz'][0]
                self.vehicle.p = traj['p'][0]
                self.vehicle.q = traj['q'][0]
                self.vehicle.r = - traj['r'][0]
            else:
                self.vehicle.propagate([traj['da'][idx], traj['de'][idx], traj['dr'][idx], traj['dt'][idx]], 1/60)
                self.fitness += ((self.vehicle.posNorth - traj['posNorth'][idx])**2 + (self.vehicle.posEast - traj['posEast'][idx])**2 + (self.vehicle.alt + traj['posDown'][idx])**2)
            # print(f'{self.vehicle.posNorth} {traj["posNorth"][idx]}')

if __name__ == '__main__':
    aero = [0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265]
    ind = Individual(aero)
    df = pd.read_csv('./data.csv')
    ind.evaluate(df)
    print(ind)
