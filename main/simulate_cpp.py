import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) # Add parent directory to path
import numpy as np
import pandas as pd
import socket
import pygame
from utils.repeated_timer import RepeatedTimer
from modules.dynamic_model import Model
import optimcore as optim

# Open socket connection
UDP_IP = "127.0.0.1"
UDP_PORT = 5502
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # AF_INET: Internet  SOCK_DGRAM: UDP

# Create plane object
plane = optim.Model()

# Auxiliary variables
m2ft = 3.28084
rad2deg = 180/np.pi
deg2rad = np.pi/180
iteration = 0

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

# Set recording parameters
update_frequency = 60 # Update frequency (Hz)
setup_time = 5 # Initial setup time (s)
recording_time = 20 # Duration of recording process (s)

# Initialize variables for data recording
da_buf = []
de_buf = []
dr_buf = []
dt_buf = []
roll_buf = []
pitch_buf = []
yaw_buf = []
posNorth_buf = []
posEast_buf = []
posDown_buf = []
vx_buf = []
vy_buf = []
vz_buf = []
p_buf = []
q_buf = []
r_buf = []

def step():

	# Define global variables
	global iteration

	# Send to FlightGear
	states = plane.getStates()
	controls = plane.getControls()
	internals = plane.getInternals()
	lat = internals[0]
	lon = internals[1]
	rotor_rpm = internals[2]
	posNorth = states[0]
	posEast = states[1]
	alt = states[2]
	pitch = states[3]
	roll = states[4]
	yaw = states[5]
	p = states[6]
	q = states[7]
	r = states[8]
	vx = states[9]
	vy = states[10]
	vz = states[11]
	da = controls[0]
	de = controls[1]
	dr = controls[2]
	dt = controls[3]
	array_FG = np.array([lat * rad2deg,
	                     lon * rad2deg,
						 alt * m2ft,
						 pitch * rad2deg,
						 roll * rad2deg,
						 yaw * rad2deg,
						 rotor_rpm,
						 -da / angular_range_ailerons,
						 -da / angular_range_ailerons,
						 de / angular_range_elevator,
						 -dr / angular_range_rudder])
	buffer = array_FG.tobytes()
	sock.sendto(buffer, (UDP_IP, UDP_PORT))  # Send array to FG

	# Fill in data structure
	if iteration >= update_frequency * setup_time:
		da_buf.append(da)
		de_buf.append(de)
		dr_buf.append(dr)
		dt_buf.append(dt)
		roll_buf.append(roll)
		pitch_buf.append(pitch)
		yaw_buf.append(yaw)
		posNorth_buf.append(posNorth)
		posEast_buf.append(posEast)
		posDown_buf.append(-alt)
		vx_buf.append(vx)
		vy_buf.append(vy)
		vz_buf.append(vz)
		p_buf.append(p)
		q_buf.append(q)
		r_buf.append(r)

	# Get joystick values
	pygame.event.pump()
	dac = -js.get_axis(ROLL_AXIS) * angular_range_ailerons
	dec = -js.get_axis(PITCH_AXIS) * angular_range_elevator
	drc = -js.get_axis(THROTTLE_AXIS) * angular_range_rudder
	dtc = -js.get_axis(YAW_AXIS) / 2 + 0.5

	# Propagate model
	plane.propagate(dac, dec, drc, dtc, 1 / update_frequency)
	
	# Update counter
	iteration += 1

	# Save data
	if iteration == update_frequency * (recording_time + setup_time):
		df = pd.DataFrame({'da': da_buf,
		                   'de': de_buf,
						   'dr': dr_buf,
						   'dt': dt_buf,
						   'roll': roll_buf,
						   'pitch': pitch_buf,
						   'yaw': yaw_buf,
						   'posNorth': posNorth_buf,
						   'posEast': posEast_buf,
						   'posDown': posDown_buf,
						   'vx': vx_buf,
						   'vy': vy_buf,
						   'vz': vz_buf,
						   'p': p_buf,
						   'q': q_buf,
						   'r': r_buf})
		print(df)
		df.to_csv(path_or_buf='./data.csv')
		sys.exit(0)


# Start task scheduler
scheduler = RepeatedTimer(1/update_frequency, step)

