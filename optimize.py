from individual import Individual
from scipy import optimize as opt
import pandas as pd
import numpy as np

def fitness(aero, traj):
    ind = Individual(aero)
    ind.evaluate(traj)
    print(ind.fitness)
    return ind.fitness

defaultAero = [0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265]
x0 = [element * (np.random.rand() + 0.5) for element in defaultAero]
bounds = [(element * 0.5, element * 1.5) if element > 0 else (element * 1.5, element * 0.5) for element in defaultAero]
df = pd.read_csv('./data.csv')

result = opt.minimize(fun=fitness, x0=x0, args=(df), method='SLSQP', bounds=bounds, tol=1e-2, options={'maxiter': 3000})
print(result['x'])

# result = opt.differential_evolution(func=fitness, args=(df,), bounds=bounds, polish=True)
# print(result['x'])