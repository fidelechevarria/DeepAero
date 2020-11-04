#include "dynamicModel.hpp"

//Constructor
Model::Model(void)
{
    _internals = {0};
    _states = {100, 0, 0, 0, 0, 0, 0, 0, 900};
    _params = {750, 9.8056, 1.225, 9.84, 7000, 7.87, 1.25, 3531.9, 2196.4, 4887.7, 0, 0, 0, 0, 0, 0, 0, 0, 100};
    _aero = {0.05, 0.01, 0.15, -0.4, 0, 0.19, 0, 0.4, 0.1205, 5.7, -0.0002, -0.33, 0.021, -0.79, 0.075, 0, -1.23, 0, -1.1, 0, -7.34, 0.21, -0.014, -0.11, -0.024, -0.265};
    _controls = {0, 0, 0, 0};

    //For estimation of AoA, pitch and body velocities for level flight
    float dynamicPressure = 0.5 * _params.rho * _params.initVelocity * _params.initVelocity;
    float term1 = tanf((((_params.m * _params.g) / (dynamicPressure * _params.S)) - _aero.Cl0) / _aero.Cla + _params.incidence);

    //Set initial velocities
    _internals.vx = sqrtf(_params.initVelocity * _params.initVelocity / (1 + term1 * term1));
    _internals.vz = _internals.vx * term1;

    std::cout << dynamicPressure << std::endl;

    //Set internal variables
    _internals.V = sqrtf(_internals.vx * _internals.vx + _internals.vy * _internals.vy + _internals.vz * _internals.vz);
    _internals.alpha = atan2f(_internals.vz, _internals.vx) - _params.incidence;
    _internals.beta = asinf(_internals.vy / _internals.V);
    _internals.lon = -3.574605617 * DEG2RAD;  //Madrid Barajas Airport (LEMD)
    _internals.lat = 40.49187427 * DEG2RAD;
    _internals.Xt = _params.Tmax * _controls.dt;

    //Set initial states
    _states.pitch = _internals.alpha + _params.incidence;  //Same as np.arctan2(_internals.vz, _internals.vx)

    //Set wind
    _internals.windNorth = _params.windVelocity * cosf(_params.windElevation) * cosf(_params.windHeading);
    _internals.windEast = _params.windVelocity * cosf(_params.windElevation) * sinf(_params.windHeading);
    _internals.windUp = _params.windVelocity * sinf(_params.windElevation);
}

Model::~Model()
{
    for (uint32_t i = 0 ; i < N_samples ; i++)
    {
        std::cout << _trajectory[16 * N_samples + i] << std::endl;
    }
    delete _trajectory;
}

uint16_t Model::propagate(Controls_t controls, float dtime)
{
    //Controls
    if (0.0F == _params.servosResponseTime)
    {
        _controls = controls;
    }
    else
    {
        _controls.da += (1.0F / (60.0F * _params.servosResponseTime)) * (controls.da - _controls.da);
        _controls.de += (1.0F / (60.0F * _params.servosResponseTime)) * (controls.de - _controls.de);
        _controls.dr += (1.0F / (60.0F * _params.servosResponseTime)) * (controls.dr - _controls.dr);
        _controls.dt += (1.0F / (60.0F * _params.servosResponseTime)) * (controls.dt - _controls.dt);
    }

    //Euler trigonometry variables
    float cr = cosf(_states.roll);
    float sr = sinf(_states.roll);
    float cp = cosf(_states.pitch);
    float sp = sinf(_states.pitch);
    float tp = tanf(_states.pitch);
    float cy = cosf(_states.yaw);
    float sy = sinf(_states.yaw);

    //Auxiliary coefficients
    float coeffA = _params.b / (2.0F * _internals.V);
    float coeffB = _params.c / (2.0F * _internals.V);

    //Introduce turbulence
    if (_params.turbulenceIntensity != 0.0F)
    {
        std::mt19937 _gen;
        std::uniform_real_distribution<float> _dist(0, 1);
        float turb = _params.turbulenceIntensity * 10.0F;
        float turbulenceCoeff = 1.0F / std::max(std::min(-1.08F * _internals.TAS + 120.0F, 0.1F), 100.0F);
        _internals.windNorth += turbulenceCoeff * (_dist(_gen) * turb - turb / 2.0F);
        _internals.windEast += turbulenceCoeff * (_dist(_gen) * turb - turb / 2.0F);
        _internals.windUp += turbulenceCoeff * (_dist(_gen) * turb - turb / 2.0F);
    }

    //Force coefficients
    _internals.Cl = _aero.Cl0 + _aero.Cla * _internals.alpha;
    _internals.Cd = _aero.Cd0 + _aero.K * _internals.Cl * _internals.Cl + _aero.Cdb * std::abs(_internals.beta);
    _internals.Cy = _aero.Cyb * _internals.beta + _aero.Cydr * _controls.dr + _aero.Cyda * _controls.da + coeffA * (_aero.Cyp * _states.p + _aero.Cyr * _states.r);

    //Moment coefficients
    _internals.Cll = _aero.Cllb * _internals.beta + _aero.Cllda * _controls.da + _aero.Clldr * _controls.dr + coeffA * (_aero.Cllp * _states.p + _aero.Cllr * _states.r);
    _internals.Cmm = _aero.Cmm0 + _aero.Cmma * _internals.alpha + _aero.Cmmde * _controls.de + _aero.Cmmdr * _controls.dr + _aero.Cmmda * std::fabs(_controls.da) + coeffB*(_aero.Cmmq * _states.q);
    _internals.Cnn = _aero.Cnnb * _internals.beta + _aero.Cnnda * _controls.da + _aero.Cnndr * _controls.dr + coeffA * (_aero.Cnnp * _states.p + _aero.Cnnr * _states.r);

    //Auxiliary variables
    float qd_times_S = 0.5*_params.rho * _internals.TAS * _internals.TAS * _params.S;
    float qd_times_S_times_b = qd_times_S * _params.b;
    float qd_times_S_times_c = qd_times_S * _params.c;

    //Dynamic forces
    _internals.D = qd_times_S_times_b * _internals.Cd;
    _internals.Y = qd_times_S_times_c * _internals.Cy;
	_internals.L = qd_times_S_times_b * _internals.Cl;

    //Dynamic moments
    _internals.LL = qd_times_S_times_b * _internals.Cll;
    _internals.MM = qd_times_S_times_c * _internals.Cmm;
    _internals.NN = qd_times_S_times_b * _internals.Cnn;

    //Aerodynamic angles trigonometry variables
    float ca = cosf(_internals.alpha);
    float sa = sinf(_internals.alpha);
    float cb = cosf(_internals.beta);
    float sb = sinf(_internals.beta);

    //Transform forces to body-axes
    _internals.Xa = -ca * cb * _internals.D - ca * sb * _internals.Y + sa * _internals.L;
    _internals.Ya = -sb * _internals.D + cb * _internals.Y;
    _internals.Za = -sa * cb * _internals.D - sa * sb * _internals.Y - ca * _internals.L;
    if (0.0F == _params.engineResponseTime)
    {
        _internals.Xt = _params.Tmax * _controls.dt;
    }
    else
    {
        _internals.Xt += (1 / (60 * _params.engineResponseTime)) * (_params.Tmax * _controls.dt - _internals.Xt);
    }
    _internals.rotor_rpm = _internals.Xt * 400 / _params.Tmax;

    //Linear accelerations in body-axes
    _internals.vx_dot = _states.r * _internals.vy - _states.q * _internals.vz - _params.g * sp + (_internals.Xa + _internals.Xt)/_params.m;
    _internals.vy_dot = -_states.r * _internals.vx + _states.p * _internals.vz + _params.g * sr * cp + _internals.Ya / _params.m;
    _internals.vz_dot = _states.q * _internals.vx - _states.p * _internals.vy + _params.g * cr * cp + _internals.Za / _params.m;

    //Euler rates
    _internals.roll_dot = _states.p + tp * (_states.q * sr + _states.r * cr);
    _internals.pitch_dot = _states.q * cr - _states.r * sr;
    _internals.yaw_dot = (_states.q * sr + _states.r * cr) / cp;

    //Angular accelerations in body-axes
    float aux = _params.Ix * _params.Iz - _params.Ixz * _params.Ixz;
    _internals.p_dot = (_params.Ixz * (_params.Ix - _params.Iy + _params.Iz) * _states.p * _states.q - (_params.Iz * (_params.Iz - _params.Iy) + _params.Ixz * _params.Ixz) * _states.q * _states.r + _params.Iz * _internals.LL + _params.Ixz * _internals.NN) / aux;
    _internals.q_dot = ((_params.Iz - _params.Ix) * _states.p * _states.r - _params.Ixz * (_states.p * _states.p - _states.r * _states.r) + _internals.MM) / _params.Iy;
    _internals.r_dot = (((_params.Ix - _params.Iy) * _params.Ix + _params.Ixz * _params.Ixz) * _states.p * _states.q - _params.Ixz * (_params.Ix - _params.Iy + _params.Iz) * _states.q * _states.r + _params.Ixz * _internals.LL + _params.Ix * _internals.NN) / aux;

    //Linear velocities in NED axes
    _internals.posNorth_dot = _internals.vx * cp * cy + _internals.vy * (-cr * sy + sr * sp * cy) + _internals.vz * (sr * sy + cr * sp * cy);
    _internals.posEast_dot = _internals.vx * cp * sy + _internals.vy * (cr * cy + sr * sp * sy) + _internals.vz * (-sr * cy + cr * sp * sy);
    _internals.alt_dot = _internals.vx * sp - _internals.vy * sr * cp - _internals.vz * cr * cp;

    //Propagate states
    _internals.vx += _internals.vx_dot * dtime;
    _internals.vy += _internals.vy_dot * dtime;
    _internals.vz += _internals.vz_dot * dtime;
    _states.roll += _internals.roll_dot * dtime;
    _states.pitch += _internals.pitch_dot * dtime;
    _states.yaw += _internals.yaw_dot * dtime;
    _states.p += _internals.p_dot * dtime;
    _states.q += _internals.q_dot * dtime;
    _states.r += _internals.r_dot * dtime;
    _states.posNorth += _internals.posNorth_dot * dtime;
    _states.posEast += _internals.posEast_dot * dtime;
    _states.alt += _internals.alt_dot * dtime;

    //Transform flat earth position to LLA
    float sinLat = sinf(_internals.lat);
    sinLat *= sinLat;
    float RN = ER / sqrtf(1 - EFDMEFS * sinLat);
    float RM = RN * ((1 - EFDMEFS) / (1 - EFDMEFS * sinLat));
    _internals.lon += atan2f(1, RN * cosf(_internals.lat)) * _internals.posEast_dot * dtime;
    _internals.lat += atan2f(1, RM) * _internals.posNorth_dot * dtime;

    //Real velocity
    _internals.V = sqrtf(_internals.vx * _internals.vx + _internals.vy * _internals.vy + _internals.vz * _internals.vz);
    
    //True Airspeed
    _internals.TAS_North = _internals.posNorth_dot - _internals.windNorth;
    _internals.TAS_East = _internals.posEast_dot - _internals.windEast;
    _internals.TAS_Up = _internals.alt_dot - _internals.windUp;
    _internals.TAS = sqrtf(_internals.TAS_North * _internals.TAS_North + _internals.TAS_East * _internals.TAS_East + _internals.TAS_Up * _internals.TAS_Up);
    _internals.TAS_x = cp * cy * _internals.TAS_North + cp * sy * _internals.TAS_East - sp * (-_internals.TAS_Up);  //Transform from flat-Earth axes to body-axes
    _internals.TAS_y = (sr * sp * cy - cr * sy) * _internals.TAS_North + (sr * sp * sy + cr * cy) * _internals.TAS_East + sr * cp * (-_internals.TAS_Up);
    _internals.TAS_z = (cr * sp * cy + sr * sy) * _internals.TAS_North + (cr * sp * sy - sr * cy) * _internals.TAS_East + cr * cp * (-_internals.TAS_Up);
    
    //Aerodynamic angles
    _internals.alpha = atan2f(_internals.TAS_z, _internals.TAS_x) - _params.incidence;
    _internals.beta = asinf(_internals.TAS_y / _internals.TAS);

    //Accumulate time
    _internals.total_time += dtime;

    return 69;
}

void Model::loadTrajectory(std::string filePath)
{
    std::string lineString;
    std::ifstream readStream;
    readStream.open(filePath);
    std::getline(readStream, lineString); // Reads first line since it is not needed
    uint16_t lineNumber = 0;
    for (;;)
    {
        lineString.clear();
        std::getline(readStream, lineString); // Reads next line in file
        if (lineString.empty())
        {
            break;
        }
        std::string delimiter = ",";
        size_t pos = 0;
        uint16_t stateNumber = 0;
        std::string token;
        while ((pos = lineString.find(delimiter)) != std::string::npos)
        {
            token = lineString.substr(0, pos); // Extract text from start until first delimiter is found
            _trajectory[stateNumber * N_samples + lineNumber] = std::stof(token);
            lineString.erase(0, pos + delimiter.length()); // Delete this section from the string since it has already been parsed
            stateNumber++;
        }
        _trajectory[stateNumber * N_samples + lineNumber] = std::stof(lineString);
        lineNumber++;
    }
}
