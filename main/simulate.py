import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) # Add parent directory to path
import numpy as np
import pandas as pd
import socket
import pygame
from utils.repeated_timer import RepeatedTimer
from modules.dynamic_model import Model

# Open socket connection
UDP_IP = "127.0.0.1"
UDP_PORT = 5502
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # AF_INET: Internet  SOCK_DGRAM: UDP

# Create plane object
plane = Model(initVelocity=100, turbulenceIntensity=0)

# Auxiliary variables
m2ft = 3.28084
rad2deg = 180/np.pi
deg2rad = np.pi/180
turbulence = 0

# Set these for each OS (Windows 10 values set here)
ROLL_AXIS = 0
PITCH_AXIS = 1
YAW_AXIS = 3
THROTTLE_AXIS = 2

# Initiate PyGame for joystick support
pygame.display.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()

# Set control surfaces angular ranges
angular_range_ailerons = 0.25
angular_range_elevator = 0.25
angular_range_rudder = 0.25

# Set update frequency (Hz)
update_frequency = 60

# Set parameters for real-time plotting
size = 60
x_vec = np.linspace(0, 10, size+1)[0:-1]
y_vec = np.zeros_like(x_vec)
line1 = []
iteration = 0
plot_style = 'state'

# Initialize variables for data recording
da = []
de = []
dr = []
dt = []
roll = []
pitch = []
yaw = []
posNorth = []
posEast = []
posDown = []
vx = []
vy = []
vz = []
p = []
q = []
r = []

def step():

	# Define global variables
	global iteration
	global x_vec
	global y_vec
	global line1
	global turbulence

	# Get joystick values
	pygame.event.pump()
	dac = -js.get_axis(ROLL_AXIS) * angular_range_ailerons
	dec = -js.get_axis(PITCH_AXIS) * angular_range_elevator
	drc = -js.get_axis(THROTTLE_AXIS) * angular_range_rudder
	dtc = -js.get_axis(YAW_AXIS) / 2 + 0.5

	# Propagate model and send to FlightGear
	plane.propagate([dac, dec, drc, dtc], 1/update_frequency, mode='complete')  # Propagate model
	array_FG = np.array([plane.lat*rad2deg, plane.lon*rad2deg, plane.alt*m2ft, plane.pitch*rad2deg, plane.roll*rad2deg, plane.yaw*rad2deg, plane.rotor_rpm, -plane.da/angular_range_ailerons, -plane.da/angular_range_ailerons, plane.de/angular_range_elevator, -plane.dr/angular_range_rudder])
	buffer = array_FG.tobytes()
	sock.sendto(buffer, (UDP_IP, UDP_PORT))  # Send array to FG

	# Fill in data structure
	da.append(plane.da)
	de.append(plane.de)
	dr.append(plane.dr)
	dt.append(plane.dt)
	roll.append(plane.roll)
	pitch.append(plane.pitch)
	yaw.append(plane.yaw)
	posNorth.append(plane.posNorth)
	posEast.append(plane.posEast)
	posDown.append(-plane.alt)
	vx.append(plane.vx)
	vy.append(plane.vy)
	vz.append(plane.vz)
	p.append(plane.p)
	q.append(plane.q)
	r.append(plane.r)

	# Update counter
	iteration += 1

	# Save data
	if iteration == update_frequency * 20:
		df = pd.DataFrame({'da': da, 'de': de, 'dr': dr, 'dt': dt, 'roll': roll, 'pitch': pitch, 'yaw': yaw, 'posNorth': posNorth, 'posEast': posEast, 'posDown': posDown, 'vx': vx, 'vy': vy, 'vz': vz, 'p': p, 'q': q, 'r': r})
		print(df)
		df.to_csv(path_or_buf='./data.csv')
		sys.exit(0)


# Start task scheduler
scheduler = RepeatedTimer(1/update_frequency, step)

