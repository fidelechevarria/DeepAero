import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# use seaborn-darkgrid style for more sophisticated visuals
plt.style.use('seaborn-darkgrid')

# Auxiliary variables
m2ft = 3.28084
rad2deg = 180/np.pi
deg2rad = np.pi/180

ax_A = []
ax_B = []
ax_C = []

fig = []
fig1 = []
fig2 = []

def live_plotter(x_vec, y1_data, line1, title='', y_label='', x_label='', pause_time=0.01):

	if line1 == []:

		# this is the call to matplotlib that allows dynamic plotting
		plt.ion()
		fig = plt.figure(figsize=(13, 6))
		ax = fig.add_subplot(111)
		# create a variable for the line so we can later update it
		line1, = ax.plot(x_vec, y1_data, '-o', alpha=0.8)
		# update plot label/title
		plt.ylabel(y_label)
		plt.xlabel(x_label)
		plt.title(title)
		plt.show()

	# after the figure, axis, and line are created, we only need to update the y-data
	line1.set_ydata(y1_data)
	# adjust limits if new data goes beyond bounds
	if np.min(y1_data) <= line1.axes.get_ylim()[0] or np.max(y1_data) >= line1.axes.get_ylim()[1]:
		plt.ylim([np.min(y1_data) - np.std(y1_data), np.max(y1_data) + np.std(y1_data)])
	# this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
	plt.pause(pause_time)

	# return line so we can update it again in the next iteration
	return line1


def live_plotter_xy(x_vec, y1_data, line1, title='', y_label='', x_label='', pause_time=0.01, plot_style='state'):

	if line1 == []:

		plt.ion()
		fig = plt.figure(figsize=(13, 6))
		ax = fig.add_subplot(111)
		line1, = ax.plot(x_vec, y1_data, 'r-o', alpha=0.8)
		plt.ylabel(y_label)
		plt.xlabel(x_label)
		plt.title(title)
		plt.show()
		if plot_style == 'wind':
			ax.set_aspect('equal', 'box')
			plt.xlim(-15, 15)
			plt.ylim(-15, 15)
		
	line1.set_data(x_vec, y1_data)
	if plot_style != 'wind':
		plt.xlim(np.min(x_vec), np.max(x_vec))
		if np.min(y1_data) <= line1.axes.get_ylim()[0] or np.max(y1_data) >= line1.axes.get_ylim()[1]:
			plt.ylim([np.min(y1_data) - np.std(y1_data), np.max(y1_data) + np.std(y1_data)])

	plt.pause(pause_time)

	return line1


def live_plotter_longitudinal_optimization(posNorth_ref, posNorth, alt_ref, alt, pitch_ref, pitch, V_ref, V, lines, title='', y_label_A='', y_label_B='', y_label_C='', x_label='', pause_time=0.1):

	global ax_A, ax_B, ax_C, fig

	line_A1 = lines[0]
	line_A2 = lines[1]
	line_B1 = lines[2]
	line_B2 = lines[3]
	line_C1 = lines[4]
	line_C2 = lines[5]

	if line_A1 == []:

		plt.ion()
		fig = plt.figure(figsize=(16, 9))
		ax_A = fig.add_subplot(311)
		line_A1, = ax_A.plot(posNorth_ref, alt_ref, '-b.', alpha=0.8)
		line_A2, = ax_A.plot(posNorth, alt, '-r.', alpha=0.2)
		ax_A.set_ylabel(y_label_A)
		ax_A.set_title(title)
		ax_B = fig.add_subplot(312)
		line_B1, = ax_B.plot(posNorth_ref, pitch_ref * rad2deg, '-b.', alpha=0.8)
		line_B2, = ax_B.plot(posNorth, pitch * rad2deg, '-r.', alpha=0.2)
		ax_B.set_ylabel(y_label_B)
		ax_C = fig.add_subplot(313)
		line_C1, = ax_C.plot(posNorth_ref, V_ref, '-b.', alpha=0.8)
		line_C2, = ax_C.plot(posNorth, V, '-r.', alpha=0.2)
		ax_C.set_ylabel(y_label_C)
		ax_C.set_xlabel(x_label)
		plt.show()

	# Update plot A data
	line_A1.set_data(posNorth_ref, alt_ref)
	line_A2.set_data(posNorth, alt)
	ax_A.set_title(title)
	ax_A.margins(0.1)

	# Update plot B data
	line_B1.set_data(posNorth_ref, pitch_ref * rad2deg)
	line_B2.set_data(posNorth, pitch * rad2deg)
	ax_B.margins(0.1)

	# Update plot C data
	line_C1.set_data(posNorth_ref, V_ref)
	line_C2.set_data(posNorth, V)
	ax_C.margins(0.1)

	plt.pause(pause_time)

	lines = [line_A1, line_A2, line_B1, line_B2, line_C1, line_C2]

	fig.savefig('Longitudinal/longitudinal.png')

	return lines


def live_plotter_complete_optimization(posNorth_ref, posNorth, posEast_ref, posEast, alt_ref, alt, pitch_ref, pitch, roll_ref, roll, yaw_ref, yaw, V_ref, V, total_time_ref, total_time, lines, title='', pause_time=0.1):

	global ax_A, ax_B, ax_C, ax_D, ax_E, fig1, fig2

	line_A1 = lines[0]
	line_A2 = lines[1]
	line_B1 = lines[2]
	line_B2 = lines[3]
	line_C1 = lines[4]
	line_C2 = lines[5]
	line_D1 = lines[6]
	line_D2 = lines[7]

	if line_A1 == []:

		plt.style.use('seaborn-darkgrid')

		plt.ion()
		fig1 = plt.figure(figsize=(16, 9))
		ax_A = fig1.add_subplot(411)
		line_A1, = ax_A.plot(total_time_ref, roll_ref * rad2deg, '-b.', alpha=0.8)
		line_A2, = ax_A.plot(total_time, roll * rad2deg, '-r.', alpha=0.2)
		ax_A.set_ylabel('Roll (°)')
		ax_A.set_title(title)
		ax_B = fig1.add_subplot(412)
		line_B1, = ax_B.plot(total_time_ref, pitch_ref * rad2deg, '-b.', alpha=0.8)
		line_B2, = ax_B.plot(total_time, pitch * rad2deg, '-r.', alpha=0.2)
		ax_B.set_ylabel('Pitch (°)')
		ax_C = fig1.add_subplot(413)
		line_C1, = ax_C.plot(total_time_ref, yaw_ref * rad2deg, '-b.', alpha=0.8)
		line_C2, = ax_C.plot(total_time, yaw * rad2deg, '-r.', alpha=0.2)
		ax_C.set_ylabel('Yaw (°)')
		ax_D = fig1.add_subplot(414)
		line_D1, = ax_D.plot(total_time_ref, V_ref, '-b.', alpha=0.8)
		line_D2, = ax_D.plot(total_time, V, '-r.', alpha=0.2)
		ax_D.set_ylabel('Velocity (m/s)')
		ax_D.set_xlabel('Time (s)')

		plt.style.use('seaborn-darkgrid')

		fig2 = plt.figure(figsize=(16, 9))
		ax_E = fig2.add_subplot(111, projection='3d')
		ax_E.plot(posNorth_ref, posEast_ref, alt_ref, '-b.', alpha=0.8)
		ax_E.plot(posNorth, posEast, alt, '-r.', alpha=0.2)
		ax_E.margins(0.1)
		ax_E.set_title(title)
		ax_E.set_xlabel('North (m)')
		ax_E.set_ylabel('East (m)')
		ax_E.set_zlabel('Altitude (m)')
		plt.show()

	plt.style.use('seaborn-darkgrid')

	# Update plot A data
	line_A1.set_data(total_time_ref, roll_ref * rad2deg)
	line_A2.set_data(total_time, roll * rad2deg)
	ax_A.set_title(title)
	ax_A.margins(0.1)

	# Update plot B data
	line_B1.set_data(total_time_ref, pitch_ref * rad2deg)
	line_B2.set_data(total_time, pitch * rad2deg)
	ax_B.margins(0.1)

	# Update plot C data
	line_C1.set_data(total_time_ref, yaw_ref * rad2deg)
	line_C2.set_data(total_time, yaw * rad2deg)
	ax_C.margins(0.1)

	# Update plot D data
	line_D1.set_data(total_time_ref, V_ref)
	line_D2.set_data(total_time, V)
	ax_D.margins(0.1)

	plt.style.use('seaborn-whitegrid')

	# Update plot E data
	ax_E.clear()
	ax_E.plot(posNorth_ref, posEast_ref, alt_ref, '-b.', alpha=0.8)
	ax_E.plot(posNorth, posEast, alt, '-r.', alpha=0.2)
	plt.sca(ax_E)
	ax_E.set_title(title)
	ax_E.margins(0.1)

	plt.pause(pause_time)

	lines = [line_A1, line_A2, line_B1, line_B2, line_C1, line_C2, line_D1, line_D2]

	fig1.savefig('Complete/complete_2D.png')
	fig2.savefig('Complete/complete_3D.png')

	return lines
