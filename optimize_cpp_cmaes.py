import optimcore as optim
import numpy as np
import pandas as pd
import cma

class Optimizer():

    def __init__(self):
        self.model = optim.Model()

    def fitness(self, aero):
        return self.model.evaluate(aero[0], aero[1], aero[2], aero[3], aero[4], aero[5], aero[6], aero[7], aero[8], aero[9],
                                   aero[10], aero[11], aero[12], aero[13], aero[14], aero[15], aero[16], aero[17], aero[18], aero[19],
                                   aero[20], aero[21], aero[22], aero[23], aero[24], aero[25])

    def getTrajectory(self, aero, trajFile):
        period = 1.0 / 60.0
        vismodel = optim.Model()
        vismodel.loadTrajectory(trajFile)
        vismodel.setAeroCoeffs(aero[0], aero[1], aero[2], aero[3], aero[4], aero[5], aero[6], aero[7], aero[8],
                            aero[9], aero[10], aero[11], aero[12], aero[13], aero[14], aero[15], aero[16], aero[17],
                            aero[18], aero[19], aero[20], aero[21], aero[22], aero[23], aero[24], aero[25])
        posNorth = []
        posEast = []
        posDown = []
        states = vismodel.getStates()
        posNorth.append(states[0])
        posEast.append(states[1])
        posDown.append(-states[2])
        for idx in range(1200):
            traj = vismodel.getTrajectorySample(idx)
            da = traj[1]
            de = traj[2]
            dr = traj[3]
            dt = traj[4]
            vismodel.propagate(da, de, dr, dt, period)
            states = vismodel.getStates()
            posNorth.append(states[0])
            posEast.append(states[1])
            posDown.append(-states[2])
        return pd.DataFrame({'posNorth': posNorth, 'posEast': posEast, 'posDown': posDown})

    def optimize(self, trajFile):
        self.model.loadTrajectory(trajFile)
        defaultAero = [0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265]
        x0 = [0.1, 0.01, 0.2, -0.5, 0, 0.2, 0, 0.4, 0.1, 6, 0, -0.3, 0, -1, 0.1, 0, -1, 0, -1, 0, -5, 0.2, 0, 0, 0, -0.2]
        es = cma.CMAEvolutionStrategy(x0, 0.2)
        es.optimize(self.fitness)
        res = es.result
        return self.getTrajectory(res[0], trajFile), self.getTrajectory(defaultAero, trajFile)

if __name__ == "__main__":
    optimizer = Optimizer()
    optimizer.optimize("/home/fidel/repos/DeepAero/data.csv")
