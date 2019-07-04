#ifndef __DYNAMIC_MODEL_H__
#define __DYNAMIC_MODEL_H__

#include <math.h>

class Model
{
    public:
        Model(void);
        void propagate();

    private:

        //Geometric and aerodynamic parameters
        float _m;
        float _g;
        float _rho;
        float _S;
        float _Tmax;
        float _b;
        float _c;
        float _Ix;
        float _Iy;
        float _Iz;
        float _Ixz;
        float _incidence;

        //Aerodynamic coefficients
        float _Cd0;
        float _K;
        float _Cdb;
        float _Cyb;
        float _Cyda;
        float _Cydr;
        float _Cyp;
        float _Cyr;
        float _Cl0;
        float _Cla;
        float _Cllb;
        float _Cllda;
        float _Clldr;
        float _Cllp;
        float _Cllr;
        float _Cmm0;
        float _Cmma;
        float _Cmmda;
        float _Cmmde;
        float _Cmmdr;
        float _Cmmq;
        float _Cnnb;
        float _Cnnda;
        float _Cnndr;
        float _Cnnp;
        float _Cnnr;

        //Controls
        float _da;
        float _de;
        float _dr;
        float _dt;

        //Internal variables
        float _vx;
        float _vy;
        float _vz;
        float _V;
        float _alpha;
        float _beta;
        float _Cd;
        float _Cy;
        float _Cl;
        float _Cll;
        float _Cmm;
        float _Cnn;
        float _D;
        float _Y;
        float _L;
        float _LL;
        float _MM;
        float _NN;
        float _vx_dot;
        float _vy_dot;
        float _vz_dot;
        float _roll_dot;
        float _pitch_dot;
        float _yaw_dot;
        float _p_dot;
        float _q_dot;
        float _r_dot;
        float _posNorth_dot;
        float _posEast_dot;
        float _alt_dot;
        float _lon;
        float _lat;
        float _total_time;
        float _Xa;
        float _Xt;
        float _rotor_rpm;
        float _servosResponseTime;
        float _engineResponseTime;
        float _initVelocity;

        //States
        float _roll;
        float _pitch;
        float _yaw;
        float _p;
        float _q;
        float _r;
        float _posNorth;
        float _posEast;
        float _alt;

        //Wind
        float _windVelocity;
        float _windHeading;
        float _windElevation;
        float _turbulenceIntensity;
        float _windNorth;
        float _windEast;
        float _windUp;
        float _TAS;
        float _TAS_North;
        float _TAS_East;
        float _TAS_Down;
        float _TAS_x;
        float _TAS_y;
        float _TAS_z;

        //Defaults
        float _defaultStates[12];
        float _defaultParams[12];
        float _defaultAero[26];
        float _defaultControls[4];
        float _defaultWind[3];
};

#endif // __DYNAMIC_MODEL_H__