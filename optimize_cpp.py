import optimcore as optim
from scipy import optimize as opt
import numpy as np
import pandas as pd

GRADIENT = 0
DIFFERENTIAL = 1
DUAL_ANNEALING = 2
SHGO = 3
BASIN_HOPPING = 4

model = optim.Model()
model.loadTrajectory()

optimizer = DIFFERENTIAL

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
    x0 = [element * (np.random.rand() + 0.5) for element in defaultAero]
    bounds = [(element * 0.5, element * 1.5) if element > 0 else (element * 1.5, element * 0.5) for element in defaultAero]
    for idx in range(len(bounds)):
        if bounds[idx] == (0, 0):
            bounds[idx] = (-0.5, 0.5)
            x0[idx] = np.random.rand() * 0.5
            
    # lower = np.array([element[0] for element in bounds])
    # upper = np.array([element[1] for element in bounds])
    # print((lower < upper))

    if optimizer == GRADIENT:
        result = opt.minimize(fun=fitness, x0=x0, args=(), method='SLSQP', bounds=bounds, tol=1e-2, options={'maxiter': 3000})
    elif optimizer == DIFFERENTIAL:
        result = opt.differential_evolution(func=fitness, args=(), bounds=bounds, maxiter=1000, popsize=15, polish=True, workers=-1, callback=callback)
    elif optimizer == DUAL_ANNEALING:
        result = opt.dual_annealing(func=fitness, args=(), bounds=bounds)
    elif optimizer == SHGO:
        result = opt.shgo(func=fitness, args=(), bounds=bounds)
    elif optimizer == BASIN_HOPPING:
        result = opt.basinhopping(func=fitness, x0=x0)

    print(f'Best coefficients found: {np.array(result["x"])}')
    print(f'Best fitness: {result["fun"]}')
    print(f'Number of function evaluations: {result["nfev"]}')
    print(f'Cause of termination: {result["message"]}')

    return getTrajectory(result["x"]), getTrajectory(defaultAero)