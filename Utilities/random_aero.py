import numpy as np

defaultAero = [0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265]

def create_random_aero_model():
	random_aero = []
	for i in range(len(defaultAero)):
		random_aero.append(np.random.uniform(defaultAero[i]*0.5, defaultAero[i]*1.5))
	return random_aero

