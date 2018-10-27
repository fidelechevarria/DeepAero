import numpy as np
from Utilities.random_aero import create_random_aero_model
from dynamic_model import Model
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
	time_hist = []
	p_hist = []
	q_hist = []
	r_hist = []
	roll_hist = []
	pitch_hist = []
	yaw_hist = []
	vx_dot_hist = []
	vy_dot_hist = []
	vz_dot_hist = []
	vx_hist = []
	vy_hist = []
	vz_hist = []

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
			p_hist.append(plane.p)
			q_hist.append(plane.q)
			r_hist.append(plane.r)
			vx_dot_hist.append(plane.vx_dot)
			vy_dot_hist.append(plane.vy_dot)
			vz_dot_hist.append(plane.vz_dot)
			vx_hist.append(plane.vx)
			vy_hist.append(plane.vy)
			vz_hist.append(plane.vz)
			roll_hist.append(plane.roll)
			pitch_hist.append(plane.pitch)
			yaw_hist.append(plane.yaw)
			time_hist.append(time)

	# Create sample
	X = sum([da_hist, de_hist, dr_hist, dt_hist, p_hist, q_hist, r_hist, roll_hist, pitch_hist, yaw_hist, vx_dot_hist, vy_dot_hist, vz_dot_hist, vx_hist, vy_hist, vz_hist], [])
	y = random_aero

	return X, y


