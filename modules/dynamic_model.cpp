#include <dynamic_model.hpp>

//Constructor
Model::Model(void)
{
    //Set initial parameters
    // _m = ;
    // _g = ;
    // _rho = ;
    // _S = ;
    // _Tmax = ;
    // _b = ;
    // _c = ;
    // _Ix = ;
    // _Iy = ;
    // _Iz = ;
    // _Ixz = ;
    // _incidence = ;
}

void Model::propagate(void)
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
    float cr = cos(_roll);
    float sr = sin(_roll);
    float cp = cos(_pitch);
    float sp = sin(_pitch);
    float tp = tan(_pitch);
    float cy = cos(_yaw);
    float sy = sin(_yaw);

    //Auxiliary coefficients
    float coeffA = _b/(2.0F*_V);
    float coeffB = _c/(2.0F*_V);

    //Introduce turbulence
    
}