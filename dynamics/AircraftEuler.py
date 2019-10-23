from numba import jit
import numpy as np

@jit(nopython=True)
def dynamics(controls, states, coefficients, parameters):

    forces = np.zeros((3), dtype=np.float32)
    moments = np.zeros((3), dtype=np.float32)

    # Unpack states
    p = states[0]
    q = states[1]
    r = states[2]
    alpha = states[3]
    beta = states[4]
    V = states[5]
    TAS = states[6]

    # Unpack coefficients
    Cd0 = coefficients[0]
    K = coefficients[1]
    Cdb = coefficients[2]
    Cyb = coefficients[3]
    Cyda = coefficients[4]
    Cydr = coefficients[5]
    Cyp = coefficients[6]
    Cyr = coefficients[7]
    Cl0 = coefficients[8]
    Cla = coefficients[9]
    Cllb = coefficients[10]
    Cllda = coefficients[11]
    Clldr = coefficients[12]
    Cllp = coefficients[13]
    Cllr = coefficients[14]
    Cmm0 = coefficients[15]
    Cmma = coefficients[16]
    Cmmda = coefficients[17]
    Cmmde = coefficients[18]
    Cmmdr = coefficients[19]
    Cmmq = coefficients[20]
    Cnnb = coefficients[21]
    Cnnda = coefficients[22]
    Cnndr = coefficients[23]
    Cnnp = coefficients[24]
    Cnnr = coefficients[25]

    # Unpack parameters
    servosResponseTime = parameters[0]
    engineResponseTime = parameters[1]
    rho = parameters[2]
    S = parameters[3]
    Tmax = parameters[4]
    b = parameters[5]
    c = parameters[6]
    windNorth = parameters[7]
    windEast = parameters[8]
    windUp = parameters[9]
    turbulenceIntensity = parameters[10]
    complete = parameters[11]

    # Controls
    da = 0
    de = 0
    dr = 0
    dt = 0
    if servosResponseTime == 0:
        da = controls[0]
        de = controls[1]
        dr = controls[2]
        dt = controls[3]
    else:
        da += (1/(60*servosResponseTime))*(controls[0]-da)
        de += (1/(60*servosResponseTime))*(controls[1]-de)
        dr += (1/(60*servosResponseTime))*(controls[2]-dr)
        dt += (1/(60*servosResponseTime))*(controls[3]-dt)

    # Auxiliary coefficients
    coeffA = b / (2 * V)
    coeffB = c / (2 * V)

    # Introduce turbulence
    if turbulenceIntensity != 0:
        turb = turbulenceIntensity * 10
        turbulenceCoeff = 1/np.maximum(np.minimum(-1.08*TAS+120, 0.1), 100)
        windNorth += turbulenceCoeff*((np.random.rand()*turb-turb/2))
        windEast += turbulenceCoeff*((np.random.rand()*turb-turb/2))
        windUp += turbulenceCoeff*((np.random.rand()*turb-turb/2))

    if complete > 0.0:

        # Force coefficients
        Cl = Cl0 + Cla * alpha
        Cd = Cd0 + K * Cl ** 2 + Cdb * np.abs(beta)
        Cy = Cyb * beta + Cydr * dr + Cyda * da + coeffA * (Cyp * p + Cyr * r)

        # Moment coefficients
        Cll = Cllb*beta + Cllda*da + Clldr*dr + coeffA*(Cllp*p + Cllr*r)
        Cmm = Cmm0 + Cmma*alpha + Cmmde*de + Cmmdr*dr + Cmmda*np.abs(da) + coeffB*(Cmmq*q)
        Cnn = Cnnb*beta + Cnnda*da + Cnndr*dr + coeffA*(Cnnp*p + Cnnr*r)

    else:

        # Force coefficients
        Cl = Cl0 + Cla * alpha
        Cd = Cd0 + K * Cl ** 2 + Cdb * np.abs(beta)
        Cy = 0

        # Moment coefficients
        Cll = 0
        Cmm = Cmm0 + Cmma * alpha + Cmmde * de + coeffB * (Cmmq * q)
        Cnn = 0

    # Auxiliary variables
    qd_times_S = 0.5*rho*TAS**2*S
    qd_times_S_times_b = qd_times_S*b
    qd_times_S_times_c = qd_times_S*c

    # Dynamic forces
    D = qd_times_S*Cd
    Y = qd_times_S*Cy
    L = qd_times_S*Cl

    # Dynamic moments
    LL = qd_times_S_times_b*Cll
    MM = qd_times_S_times_c*Cmm
    NN = qd_times_S_times_b*Cnn

    # coefficientsdynamic angles trigonometry variables
    ca = np.cos(alpha)
    sa = np.sin(alpha)
    cb = np.cos(beta)
    sb = np.sin(beta)

    # Transform forces to body-axes
    Xa = -ca*cb*D-ca*sb*Y+sa*L
    Ya = -sb*D+cb*Y
    Za = -sa*cb*D-sa*sb*Y-ca*L
    Xt = 0
    if engineResponseTime > 0.0:
        Xt = Tmax*dt
    else:
        Xt += (1/(60*engineResponseTime))*(Tmax*dt-Xt)

    # Pack forces
    forces[0] = Xa + Xt
    forces[1] = Ya
    forces[2] = Za

    # Pack moments
    moments[0] = LL
    moments[1] = MM
    moments[2] = NN

    return forces, moments
