'''Code derived from https://matplotlib.org/3.1.0/gallery/images_contours_and_fields/pcolormesh_levels.html'''

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import optimcore as optim
import numpy as np
import pandas as pd

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

frequency = 60.0
trajFile = "/home/fidel/repos/deepaero/data_clean.csv"
nsamples = pd.read_csv(trajFile).shape[0]
model = optim.Model(frequency)
model.loadTrajectory(trajFile, nsamples)
NP = 100
MIN = 0.5
MAX = 1.5
NROWS = 4
NCOLS = 2
useLinVels = False
numberOfSamplesToUse = -1

# make these smaller to increase the resolution
dx, dy = 1 / NP, 1 / NP

aero = [0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265]
aero[9] /= 100 # parameter encoding
aero[20] /= 100 # parameter encoding

orig = aero.copy()

fig = plt.figure(figsize=(6.73, 10.09), constrained_layout=True)

# names = ['Cd0', 'K', 'Cdb', 'Cyb', 'Cyda', 'Cydr', 'Cyp', 'Cyr', 'Cl0', 'Cla', 'Cllb', 'Cllda', 'Clldr', 'Cllp', 'Cllr', 'Cmm0', 'Cmma', 'Cmmda', 'Cmmde', 'Cmmdr', 'Cmmq', 'Cnnb', 'Cnnda', 'Cnndr', 'Cnnp', 'Cnnr']
names = [r'$C_{D_{0}}$', r'$K$', r'$C_{D_{\beta}}$', r'$C_{Y_{\beta}}$', r'$C_{Y_{\delta a}}$', r'$C_{Y_{\delta r}}$', r'$C_{Y_{p}}$', r'$C_{Y_{r}}$', r'$C_{L_{0}}$', r'$C_{L_{\alpha}}$', r'$C_{l_{\beta}}$', r'$C_{l_{{\delta} a}}$', r'$C_{l_{\delta r}}$', r'$C_{l_{p}}$', r'$C_{l_{r}}$', r'$C_{m_{0}}$', r'$C_{m_{\alpha}}$', r'$C_{m_{\delta a}}$', r'$C_{m_{\delta e}}$', r'$C_{m_{\delta r}}$', r'$C_{m_{q}}$', r'$C_{n_{\beta}}$', r'$C_{n_{\delta a}}$', r'$C_{n_{\delta r}}$', r'$C_{n_{p}}$', r'$C_{n_{r}}$']
param_idx_list = [3, 5, 7, 9, 11, 13, 16, 18, 20, 22]

for row in range(NROWS):
    for col in range(NCOLS):
        np.random.shuffle(param_idx_list)
        PARAM1 = param_idx_list[0]
        PARAM2 = param_idx_list[1]
        orig1 = orig[PARAM1]
        orig2 = orig[PARAM2]
        x = []
        y = []
        z = []
        for x_scale in range(NP):
            x_row = []
            y_row = []
            z_row = []
            for y_scale in range(NP):
                xval = ((MAX - MIN) * x_scale / NP + MIN)
                yval = ((MAX - MIN) * y_scale / NP + MIN)
                aero[PARAM1] = orig1 * xval
                aero[PARAM2] = orig2 * yval
                x_row.append(xval)
                y_row.append(yval)
                z_row.append(model.evaluate(aero[0], aero[1], aero[2], aero[3], aero[4], aero[5], aero[6], aero[7], aero[8], aero[9],
                                            aero[10], aero[11], aero[12], aero[13], aero[14], aero[15], aero[16], aero[17], aero[18], aero[19],
                                            aero[20], aero[21], aero[22], aero[23], aero[24], aero[25],
                                            useLinVels, numberOfSamplesToUse))
            x.append(x_row)
            y.append(y_row)
            z.append(z_row)
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        # x and y are bounds, so z should be the value *inside* those bounds.
        # Therefore, remove the last value from the z array.
        z = z[:-1, :-1]
        levels = MaxNLocator(nbins=50).tick_values(z.min(), z.max())

        # pick the desired colormap, sensible levels, and define a normalization
        # instance which takes data values and translates those into levels.
        cmap = plt.get_cmap('PiYG')
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

        ax = fig.add_subplot(NROWS, NCOLS, 1 + col + NCOLS * row)
        ax.set_xlabel(names[PARAM1], fontsize=16)
        ax.set_ylabel(names[PARAM2], fontsize=16)

        # contours are *point* based plots, so convert our bound into point
        # centers
        cf = ax.contourf(x[:-1, :-1] + dx/2.,
                        y[:-1, :-1] + dy/2., z, levels=levels,
                        cmap=cmap)
        fig.colorbar(cf, ax=ax)
        ax.set_aspect('equal', adjustable='box')
        print(f'Graph {1 + col + NCOLS * row}/{NROWS * NCOLS} generated.')

# ax.set_title('Función esfera desplazada (2D)')

plt.show()
