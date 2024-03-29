from scipy.spatial.distance import cdist
import optimcore as optim
import numpy as np
import pandas as pd
import datetime
import cma

frequency = 60.0

class Optimizer():

    def __init__(self):
        self.model = optim.Model(frequency)
        self.useLinVels = False
        self.trajFile = ''
        self.nsamples = 0
        self.numberOfSamplesToUse = -1

    def fitness(self, aero):
        return self.model.evaluate(aero[0], aero[1], aero[2], aero[3], aero[4], aero[5], aero[6], aero[7], aero[8], aero[9],
                                   aero[10], aero[11], aero[12], aero[13], aero[14], aero[15], aero[16], aero[17], aero[18], aero[19],
                                   aero[20], aero[21], aero[22], aero[23], aero[24], aero[25],
                                   self.useLinVels, self.numberOfSamplesToUse)
    
    def loadTrajectory(self, trajFile, nsamples):
        self.trajFile = trajFile
        self.nsamples = nsamples
        self.model.loadTrajectory(trajFile, nsamples)

    def getTrajectory(self, aero):
        period = 1.0 / frequency
        vismodel = optim.Model(frequency)
        vismodel.loadTrajectory(self.trajFile, self.nsamples)
        vismodel.setAeroCoeffs(*aero)
        roll = []
        pitch = []
        yaw = []
        p = []
        q = []
        r = []
        posNorth = []
        posEast = []
        posDown = []
        vx = []
        vy = []
        vz = []
        states = vismodel.getStates()
        roll.append(states[3])
        pitch.append(states[4])
        yaw.append(states[5])
        p.append(states[6])
        q.append(states[7])
        r.append(states[8])
        posNorth.append(states[0])
        posEast.append(states[1])
        posDown.append(-states[2])
        vx.append(states[9])
        vy.append(states[10])
        vz.append(states[11])
        for idx in range(self.nsamples):
            traj = vismodel.getTrajectorySample(idx)
            da = traj[1]
            de = traj[2]
            dr = traj[3]
            dt = traj[4]
            vismodel.propagate(da, de, dr, dt, period)
            states = vismodel.getStates()
            roll.append(states[3])
            pitch.append(states[4])
            yaw.append(states[5])
            p.append(states[6])
            q.append(states[7])
            r.append(states[8])
            posNorth.append(states[0])
            posEast.append(states[1])
            posDown.append(-states[2])
            vx.append(states[9])
            vy.append(states[10])
            vz.append(states[11])
        return pd.DataFrame({'posNorth': posNorth, 'posEast': posEast, 'posDown': posDown, 'roll': roll, 'pitch': pitch, 'yaw': yaw,
                             'vx': vx, 'vy': vy, 'vz': vz, 'p': p, 'q': q, 'r': r})

    def optimize(self, mode='single'):
        MBF = 0
        MSD = 0
        FSR = 0
        DSR = 0
        AES = 0
        if mode == 'single':
            N_runs = 1
        elif mode == 'eval':
            N_runs = 10
        defaultAero = [0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265]
        defaultAero_encoded = defaultAero.copy()
        defaultAero_encoded[9] /= 100
        defaultAero_encoded[20] /= 100
        for run in range(N_runs):
            x0 = [0.1, 0.1, 0.1, -0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1, 0.1, -0.1, 0.1, -1, 0.1, 0.1, -1, 0, -1, 0, -1, 0.1, -0.1, -0.1, -0.1, -0.1]
            x0_encoded = x0.copy()
            x0_encoded[9] /= 100 
            x0_encoded[20] /= 100
            for pop_size in [13]:
                self.useLinVels = False
                self.numberOfSamplesToUse = -1
                es = cma.CMAEvolutionStrategy(x0_encoded, 0.2, {'popsize': pop_size})
                print('POPSIZE = ' + str(pop_size))
                # es.optimize(self.fitness)
                while not es.stop():
                # for _ in range(5):
                    solutions = es.ask()
                    es.tell(solutions, [self.fitness(s) for s in solutions])
                    es.disp()
                es.result_pretty()
                res = es.result
                x0_encoded = [element for element in res[0]]
                self.useLinVels = True
                es._set_x0(x0_encoded)
                # sigma0 = 0.01
                # es.__init__(x0_encoded, sigma0)
                # es.optimize(self.fitness)
                while not es.stop():
                # for _ in range(5):
                    solutions = es.ask()
                    es.tell(solutions, [self.fitness(s) for s in solutions])
                    es.disp()
                es.result_pretty()
                res = es.result
                x0_encoded = [element for element in res[0]]
                x0 = x0_encoded.copy()
                x0[9] *= 100
                x0[20] *= 100
                pd.options.display.float_format = '{:,.5f}'.format
                print(pd.DataFrame({'real': defaultAero, 'optim': x0}))
            ref_array = np.expand_dims(np.array(defaultAero), axis=1).T
            sol_array = np.expand_dims(np.array(x0), axis=1).T
            sol_encoded = res[0]
            # self.useLinVels = True # Fitness for metric has to always be in (v+w) mode
            # BF = self.fitness(sol_encoded) # Also available in res[1] if fitness was (v+w) in last execution
            BF = res[1]
            SD = cdist(ref_array, sol_array, metric='cityblock')[0][0] # Calculate Manhattan distance
            FS = int(BF < 1e-2)
            DS = int(SD < 5)
            ES = res[2]
            FSR += FS
            DSR += DS
            print('Metrics of run number ' + str(run))
            print('Best fitness: ' + str(BF))
            print('Manhattan distance: ' + str(SD))
            print('Fitness success: ' + str(FS))
            print('Distance success: ' + str(DS))
            print('Number of evaluations: ' + str(ES))
            if not DS:
                continue
            MBF += BF
            MSD += SD
            AES += ES
        if mode == 'eval':
            FSR /= N_runs
            DSR /= N_runs
            successfulRuns = N_runs * DSR
            if successfulRuns > 0.0:
                MBF /= successfulRuns
                MSD /= successfulRuns
                AES /= successfulRuns
                print('Metrics after ' + str(N_runs) + ' runs')
                print('Mean best fitness: ' + str(MBF))
                print('Mean manhattan distance: ' + str(MSD))
                print('Fitness success rate: ' + str(FSR))
                print('Distance success rate: ' + str(DSR))
                print('Average number of evaluations: ' + str(AES))
            else:
                print('No successful runs')
                import sys
                sys.exit(0)
        return self.getTrajectory(sol_encoded), self.getTrajectory(defaultAero_encoded)

    def getEvaluationTimeInMicroseconds(self):
        now = datetime.datetime.now()
        self.model.evaluate(0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021,
                           -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265, True, self.nsamples)
        ellapsed = datetime.datetime.now() - now
        return int(ellapsed.total_seconds() * 1e6) # microseconds

if __name__ == "__main__":
    optimizer = Optimizer()
    optimizer.optimize("/home/fidel/repos/DeepAero/data.csv")
