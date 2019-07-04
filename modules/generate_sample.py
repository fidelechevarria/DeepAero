import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) # Add parent directory to path
import numpy as np
from utils.random_aero import create_random_aero_model
from modules.dynamic_model import Model
import matplotlib.pyplot as plt

def generate_sample():

	# Generate random dynamic model
	random_aero = create_random_aero_model()

	# Create plane object
	plane = Model(initVelocity=100, turbulenceIntensity=0, aero=random_aero)

	# Auxiliary variables
	m2ft = 3.28084
	rad2deg = 180/np.pi
	deg2rad = np.pi/180
	turbulence = 0

	# Itialize variables
	da = 0
	de = 0
	dr = 0
	dt = 0.5
	time = 0
	da_hist = []
	de_hist = []
	dr_hist = []
	dt_hist = []
	Fx_hist = []
	Fy_hist = []
	Fz_hist = []
	Mx_hist = []
	My_hist = []
	Mz_hist = []
	vx_hist = []
	vy_hist = []
	vz_hist = []
	ox_hist = []
	oy_hist = []
	oz_hist = []
	time_hist = []

	# Set control surfaces angular ranges
	angular_range_ailerons = 0.25
	angular_range_elevator = 0.25
	angular_range_rudder = 0.25

	# Set update frequency (Hz)
	update_frequency = 50

	for iteration in range(500):
		# Propagate model
		plane.propagate([da, de, dr, dt], 1/update_frequency, mode='complete')
		time += 1/update_frequency
		if iteration % 5 == 0: # 10 Hz in simulation
			# Set controls
			da += 0.05*((np.random.rand()-0.5))
			de += 0.05*((np.random.rand()-0.5))
			dr += 0.05*((np.random.rand()-0.5))
			dt += 0.05*((np.random.rand()-0.5))
			da = np.maximum(np.minimum(da, 0.5), -0.5)
			de = np.maximum(np.minimum(de, 0.5), -0.5)
			dr = np.maximum(np.minimum(dr, 0.5), -0.5)
			dt = np.maximum(np.minimum(dt, 1.0), 0.0)
			# Save controls and states
			da_hist.append(da)
			de_hist.append(de)
			dr_hist.append(dr)
			dt_hist.append(dt)
			Fx_hist.append(-plane.D)
			Fy_hist.append(plane.Y)
			Fz_hist.append(-plane.L)
			Mx_hist.append(plane.LL)
			My_hist.append(plane.MM)
			Mz_hist.append(plane.NN)
			vx_hist.append(plane.vx)
			vy_hist.append(plane.vy)
			vz_hist.append(plane.vz)
			ox_hist.append(plane.p)
			oy_hist.append(plane.q)
			oz_hist.append(plane.r)
			time_hist.append(time)

	# Create sample
	X = sum([da_hist, de_hist, dr_hist, dt_hist, Fx_hist, Fy_hist, Fz_hist, Mx_hist, My_hist, Mz_hist, vx_hist, vy_hist, vz_hist, ox_hist, oy_hist, oz_hist], [])
	y = random_aero

	return X, y


