import numpy as np

# Default model (aerobatic plane "Zivko Edge 450")
defaultStates = [100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 900]
defaultParams = [750, 9.8056, 1.225, 9.84, 7000, 7.87, 1.25, 3531.9, 2196.4, 4887.7, 0, 0]
defaultAero = [0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265]
defaultControls = [0, 0, 0, 0]
defaultWind = [0, 0, 0]

# Auxiliary parameters
f = 1/298.257223563  # Earth flattening
R = 6378137  # Earth equatorial radius
aux1 = 2*f-f**2
m2ft = 3.28084
rad2deg = 180/np.pi
deg2rad = np.pi/180


class Model:

	def __init__(self, states=defaultStates, params=defaultParams, aero=defaultAero, controls=defaultControls, wind=defaultWind, turbulenceIntensity=None, servosResponseTime=None, engineResponseTime=None, initVelocity=100):

		# Set initial parameters
		self.m = params[0]
		self.g = params[1]
		self.rho = params[2]
		self.S = params[3]
		self.Tmax = params[4]
		self.b = params[5]
		self.c = params[6]
		self.Ix = params[7]
		self.Iy = params[8]
		self.Iz = params[9]
		self.Ixz = params[10]
		self.incidence = params[11]*deg2rad  # Angle of incidence (degrees). Calado del ala

		# Set initial aerodynamic coefficients
		self.Cd0 = aero[0]
		self.K = aero[1]
		self.Cdb = aero[2]
		self.Cyb = aero[3]
		self.Cyda = aero[4]
		self.Cydr = aero[5]
		self.Cyp = aero[6]
		self.Cyr = aero[7]
		self.Cl0 = aero[8]
		self.Cla = aero[9]
		self.Cllb = aero[10]
		self.Cllda = aero[11]
		self.Clldr = aero[12]
		self.Cllp = aero[13]
		self.Cllr = aero[14]
		self.Cmm0 = aero[15]
		self.Cmma = aero[16]
		self.Cmmda = aero[17]
		self.Cmmde = aero[18]
		self.Cmmdr = aero[19]
		self.Cmmq = aero[20]
		self.Cnnb = aero[21]
		self.Cnnda = aero[22]
		self.Cnndr = aero[23]
		self.Cnnp = aero[24]
		self.Cnnr = aero[25]

		# Set controls
		self.da = controls[0]
		self.de = controls[1]
		self.dr = controls[2]
		self.dt = controls[3]

		# For estimation of AoA, pitch and body velocities for level flight
		self.initVelocity = initVelocity
		dynamic_pressure = 0.5 * self.rho * self.initVelocity ** 2
		term1 = np.tan((((self.m*self.g)/(dynamic_pressure*self.S))-self.Cl0)/self.Cla + self.incidence)

		# Set initial velocities
		self.vx = np.sqrt(self.initVelocity**2/(1+term1**2))
		self.vy = 0
		self.vz = self.vx * term1

		# Set internal variables
		self.V = np.sqrt(self.vx**2+self.vy**2+self.vz**2)
		self.alpha = np.arctan2(self.vz, self.vx) - self.incidence
		self.beta = np.arcsin(self.vy / self.V)
		self.Cd = self.Cy = self.Cl = 0
		self.Cll = self.Cmm = self.Cnn = 0
		self.D = self.Y = self.L = 0
		self.LL = self.MM = self.NN = 0
		self.vx_dot = self.vy_dot = self.vz_dot = 0
		self.roll_dot = self.pitch_dot = self.yaw_dot = 0
		self.p_dot = self.q_dot = self.r_dot = 0
		self.posNorth_dot = self.posEast_dot = self.alt_dot = 0
		self.lon = -3.574605617 * deg2rad  # Madrid Barajas Airport (LEMD)
		self.lat = 40.49187427 * deg2rad
		self.total_time = 0
		self.Xa = self.Ya = self.Za = 0
		self.Xt = self.Tmax*self.dt
		self.rotor_rpm = 0
		self.servosResponseTime = servosResponseTime
		self.engineResponseTime = engineResponseTime

		# Set initial states
		self.roll = 0
		self.pitch = self.alpha + self.incidence  # Same as np.arctan2(self.vz, self.vx)
		self.yaw = states[5]
		self.p = states[6]
		self.q = states[7]
		self.r = states[8]
		self.posNorth = states[9]
		self.posEast = states[10]
		self.alt = states[11]

		# Set wind
		self.windVelocity = wind[0]
		self.windHeading = wind[1] * deg2rad
		self.windElevation = wind[2] * deg2rad
		self.turbulenceIntensity = turbulenceIntensity
		self.windNorth = self.windVelocity * np.cos(self.windElevation) * np.cos(self.windHeading)
		self.windEast = self.windVelocity * np.cos(self.windElevation) * np.sin(self.windHeading)
		self.windUp = self.windVelocity * np.sin(self.windElevation)

		# Set true airspeed
		self.TAS_North = self.TAS_East = self.TAS_Up = self.TAS = self.TAS_x = self.TAS_y = self.TAS_z = 0

	def propagate(self, controls=defaultControls, dtime=1/60, mode='complete'):

		# Controls
		if self.servosResponseTime == None:
			self.da = controls[0]
			self.de = controls[1]
			self.dr = controls[2]
			self.dt = controls[3]
		else:
			self.da += (1/(60*self.servosResponseTime))*(controls[0]-self.da)
			self.de += (1/(60*self.servosResponseTime))*(controls[1]-self.de)
			self.dr += (1/(60*self.servosResponseTime))*(controls[2]-self.dr)
			self.dt += (1/(60*self.servosResponseTime))*(controls[3]-self.dt)

		# Euler trigonometry variables
		cr = np.cos(self.roll)
		sr = np.sin(self.roll)
		cp = np.cos(self.pitch)
		sp = np.sin(self.pitch)
		tp = np.tan(self.pitch)
		cy = np.cos(self.yaw)
		sy = np.sin(self.yaw)

		# Auxiliary coefficients
		coeffA = self.b/(2*self.V)
		coeffB = self.c/(2*self.V)

		# Introduce turbulence
		if self.turbulenceIntensity != None:
			turb = self.turbulenceIntensity * 10
			turbulenceCoeff = 1/np.max((np.min((-1.08*self.TAS+120, 0.1)), 100))
			self.windNorth += turbulenceCoeff*((np.random.rand()*turb-turb/2))
			self.windEast += turbulenceCoeff*((np.random.rand()*turb-turb/2))
			self.windUp += turbulenceCoeff*((np.random.rand()*turb-turb/2))

		if mode == 'complete':

			# Force coefficients
			self.Cl = self.Cl0 + self.Cla * self.alpha
			self.Cd = self.Cd0 + self.K*self.Cl**2 + self.Cdb*np.abs(self.beta)
			self.Cy = self.Cyb*self.beta + self.Cydr*self.dr + self.Cyda*self.da + coeffA*(self.Cyp*self.p+self.Cyr*self.r)

			# Moment coefficients
			self.Cll = self.Cllb*self.beta + self.Cllda*self.da + self.Clldr*self.dr + coeffA*(self.Cllp*self.p + self.Cllr*self.r)
			self.Cmm = self.Cmm0 + self.Cmma*self.alpha + self.Cmmde*self.de + self.Cmmdr*self.dr + self.Cmmda*np.abs(self.da) + coeffB*(self.Cmmq*self.q)
			self.Cnn = self.Cnnb*self.beta + self.Cnnda*self.da + self.Cnndr*self.dr + coeffA*(self.Cnnp*self.p + self.Cnnr*self.r)

		elif mode == 'longitudinal':

			# Force coefficients
			self.Cl = self.Cl0 + self.Cla * self.alpha
			self.Cd = self.Cd0 + self.K * self.Cl ** 2 + self.Cdb * np.abs(self.beta)
			self.Cy = 0

			# Moment coefficients
			self.Cll = 0
			self.Cmm = self.Cmm0 + self.Cmma * self.alpha + self.Cmmde * self.de + coeffB * (self.Cmmq * self.q)
			self.Cnn = 0

		# Auxiliary variables
		qd_times_S = 0.5*self.rho*self.TAS**2*self.S
		qd_times_S_times_b = qd_times_S*self.b
		qd_times_S_times_c = qd_times_S*self.c

		# Dynamic forces
		self.D = qd_times_S*self.Cd
		self.Y = qd_times_S*self.Cy
		self.L = qd_times_S*self.Cl

		# Dynamic moments
		self.LL = qd_times_S_times_b*self.Cll
		self.MM = qd_times_S_times_c*self.Cmm
		self.NN = qd_times_S_times_b*self.Cnn

		# Aerodynamic angles trigonometry variables
		ca = np.cos(self.alpha)
		sa = np.sin(self.alpha)
		cb = np.cos(self.beta)
		sb = np.sin(self.beta)

		# Transform forces to body-axes
		self.Xa = -ca*cb*self.D-ca*sb*self.Y+sa*self.L
		self.Ya = -sb*self.D+cb*self.Y
		self.Za = -sa*cb*self.D-sa*sb*self.Y-ca*self.L
		if self.engineResponseTime == None:
			self.Xt = self.Tmax*self.dt
		else:
			self.Xt += (1/(60*self.engineResponseTime))*(self.Tmax*self.dt-self.Xt)
		self.rotor_rpm = self.Xt*400/self.Tmax

		# Linear accelerations in body-axes
		self.vx_dot = self.r*self.vy-self.q*self.vz-self.g*sp+(self.Xa+self.Xt)/self.m
		self.vy_dot = -self.r*self.vx+self.p*self.vz+self.g*sr*cp+self.Ya/self.m
		self.vz_dot = self.q*self.vx-self.p*self.vy+self.g*cr*cp+self.Za/self.m

		# Euler rates
		self.roll_dot = self.p+tp*(self.q*sr+self.r*cr)
		self.pitch_dot = self.q*cr-self.r*sr
		self.yaw_dot = (self.q*sr+self.r*cr)/cp

		# Angular accelerations in body-axes
		aux = self.Ix*self.Iz-self.Ixz**2
		self.p_dot = (self.Ixz*(self.Ix-self.Iy+self.Iz)*self.p*self.q-(self.Iz*(self.Iz-self.Iy)+self.Ixz**2)*self.q*self.r+self.Iz*self.LL+self.Ixz*self.NN)/aux
		self.q_dot = ((self.Iz-self.Ix)*self.p*self.r-self.Ixz*(self.p**2-self.r**2)+self.MM)/self.Iy
		self.r_dot = (((self.Ix-self.Iy)*self.Ix+self.Ixz**2)*self.p*self.q-self.Ixz*(self.Ix-self.Iy+self.Iz)*self.q*self.r+self.Ixz*self.LL+self.Ix*self.NN)/aux

		# Linear velocities in NED axes
		self.posNorth_dot = self.vx*cp*cy+self.vy*(-cr*sy+sr*sp*cy)+self.vz*(sr*sy+cr*sp*cy)
		self.posEast_dot = self.vx*cp*sy+self.vy*(cr*cy+sr*sp*sy)+self.vz*(-sr*cy+cr*sp*sy)
		self.alt_dot = self.vx*sp-self.vy*sr*cp-self.vz*cr*cp

		# Propagate states
		self.vx += self.vx_dot * dtime
		self.vy += self.vy_dot * dtime
		self.vz += self.vz_dot * dtime
		self.roll += self.roll_dot * dtime
		self.pitch += self.pitch_dot * dtime
		self.yaw += self.yaw_dot * dtime
		self.p += self.p_dot * dtime
		self.q += self.q_dot * dtime
		self.r += self.r_dot * dtime
		self.posNorth += self.posNorth_dot * dtime
		self.posEast += self.posEast_dot * dtime
		self.alt += self.alt_dot * dtime

		# Transform flat earth position to LLA
		aux2 = np.sin(self.lat)**2
		RN = R/np.sqrt(1-aux1*aux2)
		RM = RN*((1-aux1)/(1-aux1*aux2))
		self.lon += np.arctan2(1, RN * np.cos(self.lat)) * self.posEast_dot * dtime
		self.lat += np.arctan2(1, RM) * self.posNorth_dot * dtime

		# Real velocity
		self.V = np.sqrt(self.vx**2+self.vy**2+self.vz**2)
		
		# True Airspeed
		self.TAS_North = self.posNorth_dot - self.windNorth
		self.TAS_East = self.posEast_dot - self.windEast
		self.TAS_Up = self.alt_dot - self.windUp
		self.TAS = np.sqrt(self.TAS_North**2 + self.TAS_East**2 + self.TAS_Up**2)
		self.TAS_x = cp*cy*self.TAS_North + cp*sy*self.TAS_East - sp*(-self.TAS_Up)  # Transform from flat-Earth axes to body-axes
		self.TAS_y = (sr*sp*cy-cr*sy)*self.TAS_North + (sr*sp*sy+cr*cy)*self.TAS_East + sr*cp*(-self.TAS_Up)
		self.TAS_z = (cr*sp*cy+sr*sy)*self.TAS_North + (cr*sp*sy-sr*cy)*self.TAS_East + cr*cp*(-self.TAS_Up)
		
		# Aerodynamic angles
		self.alpha = np.arctan2(self.TAS_z, self.TAS_x) - self.incidence
		self.beta = np.arcsin(self.TAS_y/self.TAS)

		# Accumulate time
		self.total_time += dtime
