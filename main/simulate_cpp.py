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

# # Initialize variables for data recording
# da = []
# de = []
# dr = []
# dt = []
# roll = []
# pitch = []
# yaw = []
# posNorth = []
# posEast = []
# posDown = []
# vx = []
# vy = []
# vz = []
# p = []
# q = []
# r = []

import time
start = time.time()
def step():

	# Define global variables
	global iteration
	global turbulence

	# Get joystick values
	pygame.event.pump()
	dac = -js.get_axis(ROLL_AXIS) * angular_range_ailerons
	dec = -js.get_axis(PITCH_AXIS) * angular_range_elevator
	drc = -js.get_axis(THROTTLE_AXIS) * angular_range_rudder
	dtc = -js.get_axis(YAW_AXIS) / 2 + 0.5

	# Propagate model and send to FlightGear
	plane.propagate(dac, dec, drc, dtc, 1 / update_frequency)  # Propagate model
	states = plane.getStates()
	controls = plane.getControls()
	internals = plane.getInternals()
	lat = internals[0]
	lon = internals[1]
	alt = states[2]
	pitch = states[3]
	roll = states[4]
	yaw = states[5]
	rotor_rpm = internals[2]
	da = controls[0]
	de = controls[1]
	dr = controls[2]
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

	end = time.time()
	print(start - end)

	# # Fill in data structure
	# da.append(plane.da)
	# de.append(plane.de)
	# dr.append(plane.dr)
	# dt.append(plane.dt)
	# roll.append(plane.roll)
	# pitch.append(plane.pitch)
	# yaw.append(plane.yaw)
	# posNorth.append(plane.posNorth)
	# posEast.append(plane.posEast)
	# posDown.append(-plane.alt)
	# vx.append(plane.vx)
	# vy.append(plane.vy)
	# vz.append(plane.vz)
	# p.append(plane.p)
	# q.append(plane.q)
	# r.append(plane.r)

	# Update counter
	# iteration += 1

	# # Save data
	# if iteration == update_frequency * 20:
	# 	df = pd.DataFrame({'da': da, 'de': de, 'dr': dr, 'dt': dt, 'roll': roll, 'pitch': pitch, 'yaw': yaw, 'posNorth': posNorth, 'posEast': posEast, 'posDown': posDown, 'vx': vx, 'vy': vy, 'vz': vz, 'p': p, 'q': q, 'r': r})
	# 	print(df)
	# 	df.to_csv(path_or_buf='./data.csv')
	# 	sys.exit(0)


# Start task scheduler
scheduler = RepeatedTimer(1/update_frequency, step)

