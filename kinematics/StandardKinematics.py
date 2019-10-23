from numba import jit
import numpy as np

# Auxiliary parameters
f = 1 / 298.257223563  # Earth flattening
R = 6378137  # Earth equatorial radius
aux1 = 2 * f - f ** 2

@jit(nopython=True)
def update(states, forces, moments, parameters, dt):

    # Unpack states
    posNorth = states[0]
    posEast = states[1]
    alt = states[2]
    vx = states[3]
    vy = states[4]
    vz = states[5]
    roll = states[6]
    pitch = states[7]
    yaw = states[8]
    p = states[9]
    q = states[10]
    r = states[11]
    lat = states[16]
    lon = states[17]

    # Unpack parameters
    m = parameters[0]
    g = parameters[1]
    Ix = parameters[5]
    Iy = parameters[6]
    Iz = parameters[7]
    Ixz = parameters[8]
    incidence = parameters[11]
    windNorth = parameters[12]
    windEast = parameters[13]
    windUp = parameters[14]

    # Euler trigonometry variables
    cr = np.cos(roll)
    sr = np.sin(roll)
    cp = np.cos(pitch)
    sp = np.sin(pitch)
    tp = np.tan(pitch)
    cy = np.cos(yaw)
    sy = np.sin(yaw)

    # Linear accelerations in body-axes
    vx_dot = r * vy - q * vz - g * sp + forces[0] / m
    vy_dot = -r * vx + p * vz + g * sr * cp + forces[1] / m
    vz_dot = q * vx - p * vy + g * cr * cp + forces[2] / m

    # Euler rates
    roll_dot = p + tp * (q * sr + r * cr)
    pitch_dot = q * cr - r * sr
    yaw_dot = (q * sr + r * cr) / cp

    # Angular accelerations in body-axes
    aux = Ix * Iz - Ixz ** 2
    p_dot = (Ixz * (Ix - Iy + Iz) * p * q - (Iz * (Iz - Iy) + Ixz ** 2) * q * r + Iz * moments[0] + Ixz * moments[2]) / aux
    q_dot = ((Iz - Ix) * p * r - Ixz * (p ** 2 - r ** 2) + moments[1]) / Iy
    r_dot = (((Ix - Iy) * Ix + Ixz ** 2) * p * q - Ixz * (Ix - Iy + Iz) * q * r + Ixz * moments[0] + Ix * moments[2]) / aux

    # Linear velocities in NED axes
    posNorth_dot = vx * cp * cy + vy * (-cr * sy + sr * sp * cy) + vz * (sr * sy + cr * sp * cy)
    posEast_dot = vx * cp * sy + vy * (cr * cy + sr * sp * sy) + vz * (-sr * cy + cr * sp * sy)
    alt_dot = vx * sp - vy * sr * cp - vz * cr * cp

    # Propagate states
    vx += vx_dot * dt
    vy += vy_dot * dt
    vz += vz_dot * dt
    roll += roll_dot * dt
    pitch += pitch_dot * dt
    yaw += yaw_dot * dt
    p += p_dot * dt
    q += q_dot * dt
    r += r_dot * dt
    posNorth += posNorth_dot * dt
    posEast += posEast_dot * dt
    alt += alt_dot * dt

    # Transform flat earth position to LLA
    aux2 = np.sin(lat) ** 2
    RN = R / np.sqrt(1 - aux1 * aux2)
    RM = RN * ((1 - aux1) / (1 - aux1 * aux2))
    lon += np.arctan2(1, RN * np.cos(lat)) * posEast_dot * dt
    lat += np.arctan2(1, RM) * posNorth_dot * dt

    # Real velocity
    V = np.sqrt(vx ** 2 + vy ** 2 + vz ** 2)
    
    # True Airspeed
    TAS_North = posNorth_dot - windNorth
    TAS_East = posEast_dot - windEast
    TAS_Up = alt_dot - windUp
    TAS = np.sqrt(TAS_North ** 2 + TAS_East ** 2 + TAS_Up ** 2)
    TAS_x = cp * cy * TAS_North + cp * sy * TAS_East - sp * (-TAS_Up)  # Transform from flat-Earth axes to body-axes
    TAS_y = (sr * sp * cy - cr * sy) * TAS_North + (sr * sp * sy + cr * cy) * TAS_East + sr * cp * (-TAS_Up)
    TAS_z = (cr * sp * cy + sr * sy) * TAS_North + (cr * sp * sy - sr * cy) * TAS_East + cr * cp * (-TAS_Up)
    
    # Aerodynamic angles
    alpha = np.arctan2(TAS_z, TAS_x) - incidence
    beta = np.arcsin(TAS_y / TAS)

    # Pack states
    states[0] = posNorth
    states[1] = posEast
    states[2] = alt
    states[3] = vx
    states[4] = vy
    states[5] = vz
    states[6] = roll
    states[7] = pitch
    states[8] = yaw
    states[9] = p
    states[10] = q
    states[11] = r
    states[12] = alpha
    states[13] = beta
    states[14] = V
    states[15] = TAS

    return states