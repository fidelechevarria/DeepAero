import numpy as np

defaultAero = np.array([0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205,
                        5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23,
                        0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265])

mse = []
for _ in range(32 * 20):
    aero = np.random.uniform(defaultAero * 0.5, defaultAero * 1.5)
    mse.append((np.square(aero - defaultAero)).mean(axis=None))
mse = np.array(mse)
print(mse.mean(axis=None))
