#include <dynamic_model.hpp>

//Constructor
Model::Model(float states[], float params[], float aero[],
             float controls[], float wind[], float turbulenceIntensity,
             float servosResponseTime, float engineResponseTime, float initVelocity)
{
    //Auxiliary parameters
    _f = 1.0F/298.257223563F;  //Earth flattening
    _R = 6378137;  //Earth equatorial radius
    _aux1 = 2*_f-_f*_f;
    _m2ft = 3.28084;
    _rad2deg = 180/std::_Pi;
    _deg2rad = std::_Pi/180;

    //Set initial parameters
    _m = params[0];
    _g = params[1];
    _rho = params[2];
    _S = params[3];
    _Tmax = params[4];
    _b = params[5];
    _c = params[6];
    _Ix = params[7];
    _Iy = params[8];
    _Iz = params[9];
    _Ixz = params[10];
    _incidence = params[11] * _deg2rad; //Angle of incidence (degrees). Calado del ala

    //Set initial aerodynamic coefficients
    _Cd0 = aero[0];
    _K = aero[1];
    _Cdb = aero[2];
    _Cyb = aero[3];
    _Cyda = aero[4];
    _Cydr = aero[5];
    _Cyp = aero[6];
    _Cyr = aero[7];
    _Cl0 = aero[8];
    _Cla = aero[9];
    _Cllb = aero[10];
    _Cllda = aero[11];
    _Clldr = aero[12];
    _Cllp = aero[13];
    _Cllr = aero[14];
    _Cmm0 = aero[15];
    _Cmma = aero[16];
    _Cmmda = aero[17];
    _Cmmde = aero[18];
    _Cmmdr = aero[19];
    _Cmmq = aero[20];
    _Cnnb = aero[21];
    _Cnnda = aero[22];
    _Cnndr = aero[23];
    _Cnnp = aero[24];
    _Cnnr = aero[25];

    //Set controls
    _da = controls[0];
    _de = controls[1];
    _dr = controls[2];
    _dt = controls[3];

    //For estimation of AoA, pitch and body velocities for level flight
    _initVelocity = initVelocity;
    float dynamic_pressure = 0.5 * _rho * _initVelocity * _initVelocity;
    float term1 = tanf((((_m*_g)/(dynamic_pressure*_S))-_Cl0)/_Cla + _incidence);

    //Set initial velocities
    _vx = sqrtf(_initVelocity*_initVelocity/(1+term1*term1));
    _vy = 0.0F;
    _vz = _vx * term1;

    //Set internal variables
    _V = sqrtf(_vx*_vx+_vy*_vy+_vz*_vz);
    _alpha = atan2f(_vz, _vx) - _incidence;
    _beta = asin(_vy / _V);
    _Cd = 0.0F;
    _Cy = 0.0F;
    _Cl = 0.0F;
    _Cll = 0.0F;
    _Cmm = 0.0F;
    _Cnn = 0.0F;
    _D = 0.0F;
    _Y = 0.0F;
    _L = 0.0F;
    _LL = 0.0F;
    _MM = 0.0F;
    _NN = 0.0F;
    _vx_dot = 0.0F;
    _vy_dot = 0.0F;
    _vz_dot = 0.0F;
    _roll_dot = 0.0F;
    _pitch_dot = 0.0F;
    _yaw_dot = 0.0F;
    _p_dot = 0.0F;
    _q_dot = 0.0F;
    _r_dot = 0.0F;
    _posNorth_dot = 0.0F;
    _posEast_dot = 0.0F;
    _alt_dot = 0.0F;
    _lon = -3.574605617 * _deg2rad;  //Madrid Barajas Airport (LEMD)
    _lat = 40.49187427 * _deg2rad;
    _total_time = 0.0F;
    _Xa = 0.0F;
    _Ya = 0.0F;
    _Za = 0.0F;
    _Xt = _Tmax*_dt;
    _rotor_rpm = 0.0F;
    _servosResponseTime = servosResponseTime;
    _engineResponseTime = engineResponseTime;

    //Set initial states
    _roll = 0.0F;
    _pitch = _alpha + _incidence;  //Same as np.arctan2(_vz, _vx)
    _yaw = states[5];
    _p = states[6];
    _q = states[7];
    _r = states[8];
    _posNorth = states[9];
    _posEast = states[10];
    _alt = states[11];

    //Set wind
    _windVelocity = wind[0];
    _windHeading = wind[1] * _deg2rad;
    _windElevation = wind[2] * _deg2rad;
    _turbulenceIntensity = turbulenceIntensity;
    _windNorth = _windVelocity * cosf(_windElevation) * cosf(_windHeading);
    _windEast = _windVelocity * cosf(_windElevation) * sinf(_windHeading);
    _windUp = _windVelocity * sinf(_windElevation);

    //Set true airspeed
    _TAS_North = 0.0F;
    _TAS_East = 0.0F;
    _TAS_Up = 0.0F;
    _TAS = 0.0F;
    _TAS_x = 0.0F;
    _TAS_y = 0.0F;
    _TAS_z = 0.0F;
}

void Model::propagate(float controls[], float dtime)
{
    //Controls
    if (_servosResponseTime == 0.0F)
    {
        _da = controls[0];
        _de = controls[1];
        _dr = controls[2];
        _dt = controls[3];
    }
    else
    {
        _da += (1.0F/(60.0F*_servosResponseTime))*(controls[0]-_da);
        _de += (1.0F/(60.0F*_servosResponseTime))*(controls[1]-_de);
        _dr += (1.0F/(60.0F*_servosResponseTime))*(controls[2]-_dr);
        _dt += (1.0F/(60.0F*_servosResponseTime))*(controls[3]-_dt);
    }

    //Euler trigonometry variables
    float cr = cosf(_roll);
    float sr = sinf(_roll);
    float cp = cosf(_pitch);
    float sp = sinf(_pitch);
    float tp = tan(_pitch);
    float cy = cosf(_yaw);
    float sy = sinf(_yaw);

    //Auxiliary coefficients
    float coeffA = _b/(2.0F*_V);
    float coeffB = _c/(2.0F*_V);

    //Introduce turbulence
    if (_turbulenceIntensity != 0.0F)
    {
        std::mt19937 _gen;
        std::uniform_real_distribution<float> _dist(0, 1);
        float turb = _turbulenceIntensity * 10.0F;
        float turbulenceCoeff = 1.0F/std::max(std::min(-1.08F*_TAS+120.0F, 0.1F), 100.0F);
        _windNorth += turbulenceCoeff * (_dist(_gen)*turb - turb/2.0F);
        _windEast += turbulenceCoeff * (_dist(_gen)*turb - turb/2.0F);
        _windUp += turbulenceCoeff * (_dist(_gen)*turb - turb/2.0F);
    }

    //Force coefficients
    _Cl = _Cl0 + _Cla * _alpha;
    _Cd = _Cd0 + _K * _Cl * _Cl + _Cdb * std::abs(_beta);
    _Cy = _Cyb*_beta + _Cydr*_dr + _Cyda*_da + coeffA*(_Cyp*_p+_Cyr*_r);

    //Moment coefficients
    _Cll = _Cllb*_beta + _Cllda*_da + _Clldr*_dr + coeffA*(_Cllp*_p + _Cllr*_r);
    _Cmm = _Cmm0 + _Cmma*_alpha + _Cmmde*_de + _Cmmdr*_dr + _Cmmda*std::abs(_da) + coeffB*(_Cmmq*_q);
    _Cnn = _Cnnb*_beta + _Cnnda*_da + _Cnndr*_dr + coeffA*(_Cnnp*_p + _Cnnr*_r);

    //Auxiliary variables
    float qd_times_S = 0.5*_rho*_TAS*_TAS*_S;
    float qd_times_S_times_b = qd_times_S*_b;
    float qd_times_S_times_c = qd_times_S*_c;

    //Dynamic forces
    _LL = qd_times_S_times_b*_Cll;
    _MM = qd_times_S_times_c*_Cmm;
	_NN = qd_times_S_times_b*_Cnn;

    //Dynamic moments
    _LL = qd_times_S_times_b*_Cll;
    _MM = qd_times_S_times_c*_Cmm;
    _NN = qd_times_S_times_b*_Cnn;

    //Aerodynamic angles trigonometry variables
    float ca = cosf(_alpha);
    float sa = sinf(_alpha);
    float cb = cosf(_beta);
    float sb = sinf(_beta);

    //Transform forces to body-axes
    _Xa = -ca*cb*_D-ca*sb*_Y+sa*_L;
    _Ya = -sb*_D+cb*_Y;
    _Za = -sa*cb*_D-sa*sb*_Y-ca*_L;
    if (_engineResponseTime == 0.0F)
    {
        _Xt = _Tmax*_dt;
    }
    else
    {
        _Xt += (1/(60*_engineResponseTime))*(_Tmax*_dt-_Xt);
    }
    _rotor_rpm = _Xt*400/_Tmax;

    //Linear accelerations in body-axes
    _vx_dot = _r*_vy-_q*_vz-_g*sp+(_Xa+_Xt)/_m;
    _vy_dot = -_r*_vx+_p*_vz+_g*sr*cp+_Ya/_m;
    _vz_dot = _q*_vx-_p*_vy+_g*cr*cp+_Za/_m;

    //Euler rates
    _roll_dot = _p+tp*(_q*sr+_r*cr);
    _pitch_dot = _q*cr-_r*sr;
    _yaw_dot = (_q*sr+_r*cr)/cp;

    //Angular accelerations in body-axes
    float aux = _Ix*_Iz-_Ixz*_Ixz;
    _p_dot = (_Ixz*(_Ix-_Iy+_Iz)*_p*_q-(_Iz*(_Iz-_Iy)+_Ixz*_Ixz)*_q*_r+_Iz*_LL+_Ixz*_NN)/aux;
    _q_dot = ((_Iz-_Ix)*_p*_r-_Ixz*(_p*_p-_r*_r)+_MM)/_Iy;
    _r_dot = (((_Ix-_Iy)*_Ix+_Ixz*_Ixz)*_p*_q-_Ixz*(_Ix-_Iy+_Iz)*_q*_r+_Ixz*_LL+_Ix*_NN)/aux;

    //Linear velocities in NED axes
    _posNorth_dot = _vx*cp*cy+_vy*(-cr*sy+sr*sp*cy)+_vz*(sr*sy+cr*sp*cy);
    _posEast_dot = _vx*cp*sy+_vy*(cr*cy+sr*sp*sy)+_vz*(-sr*cy+cr*sp*sy);
    _alt_dot = _vx*sp-_vy*sr*cp-_vz*cr*cp;

    //Propagate states
    _vx += _vx_dot * dtime;
    _vy += _vy_dot * dtime;
    _vz += _vz_dot * dtime;
    _roll += _roll_dot * dtime;
    _pitch += _pitch_dot * dtime;
    _yaw += _yaw_dot * dtime;
    _p += _p_dot * dtime;
    _q += _q_dot * dtime;
    _r += _r_dot * dtime;
    _posNorth += _posNorth_dot * dtime;
    _posEast += _posEast_dot * dtime;
    _alt += _alt_dot * dtime;

    //Transform flat earth position to LLA
    float aux2 = sinf(_lat);
    aux2 *= aux2;
    float RN = _R/sqrtf(1-_aux1*aux2);
    float RM = RN*((1-_aux1)/(1-_aux1*aux2));
    _lon += atan2f(1, RN * cosf(_lat)) * _posEast_dot * dtime;
    _lat += atan2f(1, RM) * _posNorth_dot * dtime;

    //Real velocity
    _V = sqrtf(_vx*_vx+_vy*_vy+_vz*_vz);
    
    //True Airspeed
    _TAS_North = _posNorth_dot - _windNorth;
    _TAS_East = _posEast_dot - _windEast;
    _TAS_Up = _alt_dot - _windUp;
    _TAS = sqrtf(_TAS_North*_TAS_North + _TAS_East*_TAS_East + _TAS_Up*_TAS_Up);
    _TAS_x = cp*cy*_TAS_North + cp*sy*_TAS_East - sp*(-_TAS_Up);  //Transform from flat-Earth axes to body-axes
    _TAS_y = (sr*sp*cy-cr*sy)*_TAS_North + (sr*sp*sy+cr*cy)*_TAS_East + sr*cp*(-_TAS_Up);
    _TAS_z = (cr*sp*cy+sr*sy)*_TAS_North + (cr*sp*sy-sr*cy)*_TAS_East + cr*cp*(-_TAS_Up);
    
    //Aerodynamic angles
    _alpha = atan2f(_TAS_z, _TAS_x) - _incidence;
    _beta = asinf(_TAS_y/_TAS);

    //Accumulate time
    _total_time += dtime;
}