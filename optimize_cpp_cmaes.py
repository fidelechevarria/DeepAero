import optimcore as optim
import numpy as np
import pandas as pd
import cma

model = optim.Model()
model.loadTrajectory()

def fitness(aero):
    return model.evaluate(aero[0], aero[1], aero[2], aero[3], aero[4], aero[5], aero[6], aero[7], aero[8], aero[9],
                          aero[10], aero[11], aero[12], aero[13], aero[14], aero[15], aero[16], aero[17], aero[18], aero[19],
                          aero[20], aero[21], aero[22], aero[23], aero[24], aero[25])

def callback(xk, convergence):
    # xk is the current value of x0. convergence represents the fractional value of the population convergence.
    # When convergence is greater than one the function halts. If callback returns True, then the minimization
    # is halted (any polishing is still carried out).
    pass

period = 1.0 / 60.0 
def getTrajectory(aero):
    vismodel = optim.Model()
    vismodel.loadTrajectory()
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
    return pd.DataFrame({'north': posNorth, 'east': posEast, 'down': posDown})

def optimize():
    defaultAero = [0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265]
    x0 = [0.1, 0.01, 0.2, -0.5, 0, 0.2, 0, 0.4, 0.1, 6, 0, -0.3, 0, -1, 0.1, 0, -1, 0, -1, 0, -5, 0.2, 0, 0, 0, -0.2]
    es = cma.CMAEvolutionStrategy(x0, 0.2)
    es.optimize(fitness)
    res = es.result
    return getTrajectory(res[0]), getTrajectory(defaultAero)

if __name__ == "__main__":
    optimize()