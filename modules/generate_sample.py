import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) # Add parent directory to path
import numpy as np
import optimcore as optim
# import matplotlib.pyplot as plt

frequency = 200.0
period = 1 / frequency

defaultAero = np.array([0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265])

def generate_sample():

	X = np.nan
	while np.any(np.isnan(X)):

		# Generate random dynamic model
		aero = np.random.uniform(defaultAero * 0.5, defaultAero * 1.5)

		# Create plane object
		# plane = Model(initVelocity=100, turbulenceIntensity=0, aero=aero)
		plane = optim.Model(frequency)
		plane.setAeroCoeffs(aero[0], aero[1], aero[2], aero[3], aero[4], aero[5], aero[6], aero[7], aero[8],
							aero[9], aero[10], aero[11], aero[12], aero[13], aero[14], aero[15], aero[16], aero[17],
							aero[18], aero[19], aero[20], aero[21], aero[22], aero[23], aero[24], aero[25])

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
		wx_hist = []
		wy_hist = []
		wz_hist = []
		time_hist = []

		# Set control surfaces angular ranges
		angular_range_ailerons = 0.25
		angular_range_elevator = 0.25
		angular_range_rudder = 0.25

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
				Fx_hist.append(-internals[6]) # D
				Fy_hist.append(internals[7]) # Y
				Fz_hist.append(-internals[8]) # L
				Mx_hist.append(internals[9]) # LL
				My_hist.append(internals[10]) # MM
				Mz_hist.append(internals[11]) # NN
				vx_hist.append(states[9]) # vx
				vy_hist.append(states[10]) # vy
				vz_hist.append(states[11]) # vz
				wx_hist.append(states[6]) # p
				wy_hist.append(states[7]) # q
				wz_hist.append(states[8]) # r
				time_hist.append(time)

		# fig = plt.figure()
		# ax = fig.add_subplot(1, 1, 1)
		# ax.plot(wx_hist)
		# plt.show()

		# Create sample
		X = np.array([da_hist, de_hist, dr_hist, dt_hist,
					Fx_hist, Fy_hist, Fz_hist, Mx_hist,
					My_hist, Mz_hist, vx_hist, vy_hist,
					vz_hist, wx_hist, wy_hist, wz_hist])
		y = np.array(aero)

	return X, y

if __name__ == '__main__':
	X, y = generate_sample()
	print(X.shape)
	print(y.shape)