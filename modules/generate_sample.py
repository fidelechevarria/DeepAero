import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) # Add parent directory to path
import numpy as np
import optimcore as optim
from scipy.spatial.transform import Rotation as R
# import matplotlib.pyplot as plt

frequency = 200.0
period = 1 / frequency

defaultControls = np.array([0, 0, 0, 0])
defaultStates = np.array([0, 0, 0, 0, 0, 0, 0, 0, 900, 0, 0, 0])
defaultParams = np.array([750, 9.8056, 1.225, 9.84, 7000, 7.87, 1.25, 3531.9, 2196.4, 4887.7, 0, 0, 0, 0, 0, 1.0, 0, 0, 100])
defaultAero = np.array([0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265])

def generate_sample():

	# N_fails = 0

	while True: # Keep generating samples until one without divergence is found

		# Generate random dynamic model
		controls = np.random.uniform([-0.5, -0.5, -0.5, 0.0], [0.5, 0.5, 0.5, 1.0])
		states = np.random.uniform([-np.pi, -np.pi/2, -np.pi, -1.0, -1.0, -1.0, 0.0, 0.0, 900.0, 30.0, -5.0, -10.0],
		                           [+np.pi, +np.pi/2, +np.pi, +1.0, +1.0, +1.0, 0.0, 0.0, 900.0, 130.0, +5.0, +10.0])
		params = defaultParams
		aero = np.random.uniform(defaultAero * 0.5, defaultAero * 1.5)
		# aero = np.random.uniform(-np.ones_like(defaultAero), np.ones_like(defaultAero))

		# Create plane object
		# plane = Model(initVelocity=100, turbulenceIntensity=0, aero=aero)
		plane = optim.Model(frequency)
		plane.setControls(*controls)
		plane.setStates(*states)
		plane.setParams(*params)
		plane.setAeroCoeffs(*aero)
		plane.init()

		# Itialize variables
		da = controls[0]
		de = controls[1]
		dr = controls[2]
		dt = controls[3]
		time = 0
		da_hist = []
		de_hist = []
		dr_hist = []
		dt_hist = []
		# Fx_hist = []
		# Fy_hist = []
		# Fz_hist = []
		# Mx_hist = []
		# My_hist = []
		# Mz_hist = []
		vx_hist = []
		vy_hist = []
		vz_hist = []
		wx_hist = []
		wy_hist = []
		wz_hist = []
		# q1_hist = []
		# q2_hist = []
		# q3_hist = []
		# q4_hist = []
		# n_hist = []
		# e_hist = []
		# a_hist = []
		time_hist = []

		for iteration in range(4000):
			# Propagate model
			# plane.propagate([da, de, dr, dt], period, mode='complete')
			plane.propagate(da, de, dr, dt, period)
			time += period
			if iteration % 40 == 0: # 5 Hz in simulation
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
				states = plane.getStates()
				internals = plane.getInternals()
				# Fx_hist.append(-internals[6]) # D
				# Fy_hist.append(internals[7]) # Y
				# Fz_hist.append(-internals[8]) # L
				# Mx_hist.append(internals[9]) # LL
				# My_hist.append(internals[10]) # MM
				# Mz_hist.append(internals[11]) # NN
				# r = R.from_euler('ZYX', [states[3], states[4], states[5]], degrees=False)
				# quat = r.as_quat()
				vx_hist.append(states[9]) # vx
				vy_hist.append(states[10]) # vy
				vz_hist.append(states[11]) # vz
				wx_hist.append(states[6]) # p
				wy_hist.append(states[7]) # q
				wz_hist.append(states[8]) # r
				# q1_hist.append(quat[0]) # q1
				# q2_hist.append(quat[1]) # q2
				# q3_hist.append(quat[2]) # q3
				# q4_hist.append(quat[3]) # q4
				# n_hist.append(states[0] / 1000) # north
				# e_hist.append(states[1] / 1000) # east
				# a_hist.append(states[2] / 1000) # alt
				time_hist.append(time)

		# fig = plt.figure()
		# ax = fig.add_subplot(1, 1, 1)
		# ax.plot(vx_hist, color='red')
		# # ax.get_xaxis().set_ticklabels([])
		# # ax.get_yaxis().set_ticklabels([])
		# # Show the major grid lines with dark grey lines
		# plt.grid(b=True, which='major', color='#666666', linestyle='-')
		# # Show the minor grid lines with very faint and almost transparent grey lines
		# plt.minorticks_on()
		# plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
		# plt.show()

		# Create sample
		X = np.array([da_hist, de_hist, dr_hist, dt_hist,
		            #   q1_hist, q2_hist, q3_hist, q4_hist,
					#   n_hist, e_hist, a_hist])
					  vx_hist, vy_hist, vz_hist,
					  wx_hist, wy_hist, wz_hist])
		y = np.array(aero)
		if not np.any(np.isnan(X)):
			break
		# else:
		# 	N_fails += 1
		# 	print(f'{N_fails} Invalid solutions found')
	return X, y

if __name__ == '__main__':
	X, y = generate_sample()
	print(X.shape)
	print(y.shape)