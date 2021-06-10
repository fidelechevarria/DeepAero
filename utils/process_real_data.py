from scipy.spatial.transform import Rotation as R
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.close("all")

# Function definitions
def ResamplePacket(packet, frequency=None, numberOfSamples=None, timeReference='totalTime'):
    if (frequency == None) & (numberOfSamples == None): 
        print('Error - ResamplePacket - Frequency or number of samples must be specified for resampling.')
        newDataDF = None
    else:
        data = packet.drop(timeReference, axis=1).values
        time = np.array(packet[timeReference])
        names = list(packet.drop(timeReference, axis=1).columns.values)
        interpFcn = interp1d(time, data, axis=0, fill_value="extrapolate")
        if frequency == None:
            newTime = np.linspace(time[0], time[-1], numberOfSamples, endpoint=True)
        else:
            newTime = np.arange(time[0], time[-1], 1.0/frequency)
        newData = interpFcn(newTime)
        newDataDF = pd.DataFrame(data=newData, columns=names)
        newDataDF[timeReference] = pd.Series(newTime)
    return newDataDF

def TrimPacket(packet, timeStart, timeEnd, timeReference='totalTime'):
    return packet[(packet[timeReference] >= timeStart) & (packet[timeReference] <= timeEnd)].reset_index()

data = pd.read_csv('real_data.csv') # Read real data from file
data = TrimPacket(data, 1400, 1450, timeReference='time') # Trim packet to desired time range
data = ResamplePacket(data, frequency=60, timeReference='time') # Resample packet to 60 Hz frequency

# Transform LLA to NED coordinates
RT = 6378000
data['posNorth'] = np.deg2rad(data['lat'] - data['lat'][0]) * RT
data['posEast'] = np.deg2rad(data['lon'] - data['lon'][0]) * np.cos(np.deg2rad(data['lat'][0])) * RT
data['posDown'] = - data['alt']

# Rotate velocities from NED to body axes
r = R.from_euler('ZYX', np.swapaxes([data['yaw'].values, data['pitch'].values, data['roll'].values], 0, 1), degrees=True)
dcm = r.as_matrix()
vned = np.moveaxis(np.expand_dims([data['vn'].values, data['ve'].values, data['vd'].values], 1), -1, 0)
print(dcm.shape)
print(vned.shape)
vbody = np.matmul(np.linalg.inv(dcm), vned)
print(vbody.shape)
data['vx'] = vbody[:, 0, 0]
data['vy'] = vbody[:, 1, 0]
data['vz'] = vbody[:, 2, 0]

# Plot vels and attitude
data.plot(x='time', y=['vx', 'vy', 'vz'])
data.plot(x='time', y=['roll', 'pitch', 'yaw'])
data.plot(x='time', y=['vn', 've', 'vd'])
plt.show()

# Save data to file
data.to_csv(path_or_buf='data_real_processed.csv',
            columns=('da','de','dr','dt','roll','pitch','yaw','posNorth','posEast','posDown','vx','vy','vz','p','q','r'),
            header=True)