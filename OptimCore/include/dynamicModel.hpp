/**
 *	\file dynamicModel.hpp
 *
 *	TSIP state machine related functions
 *	The main workflow with the functions included in this file should be the following:\n
 *
 *	\par Receiving TSIP
 *	NOTE: User should not care about the contents of TsipRx_t. There is no need to manually manipulate this struct by the end user.
 *	However the end user could extract usefull info from its TsipRxStatistics_t member for diagnosis purposes.
 *	-# User declares a TsipRx_t and initializes it with \link TsipInitRx \endlink.\n
 *	-# User feeds the TsipRx_t with raw bytes through \link TsipProcessRawRx \endlink.\n
 *	-# Depending on content of raw buffer passed:
 *		-# If bytes fed contained a valid TSIP packet, \link TsipPendingPacketsRx \endlink should return a number > 0 \n
 *		-# Otherwise user can keep feeding the TsipRx_t with more bytes (the state machine will preserve its state).
 *	-# User can get completed packets available in the state machine through \link TsipReadPacketRx \endlink.
 *	\par Sending TSIP
 *	Use \link TsipCreatePacket \endlink feeding the raw data to encapsulate in TSIP format. This function will add
 *	CRC, heading DLE, trailing DLE-ETX and escape DLEs of data if present.
 */

#ifndef __DYNAMIC_MODEL_H__
#define __DYNAMIC_MODEL_H__

/*----------------------------------------------------------------------------
 *        Headers
 *----------------------------------------------------------------------------*/

#include <math.h>
#include <algorithm>
#include <random>
#include <iostream>

/*----------------------------------------------------------------------------
 *        Definitions
 *----------------------------------------------------------------------------*/

#define EF (1/298.257223563)       /*!< [E]arth [F]lattening */
#define ER 6378137                 /*!< [E]arth equatorial [R]adius in meters */
#define EFDMEFS (2 * EF - EF * EF) /*!< [E]arth [F]lattening [D]oubled [M]inus [E]arth [F]lattening [S]quared */
#define M2FT 3.28084               /*!< Number of feet in a meter */
#define RAD2DEG (180 / M_PI)       /*!< Number of degrees in a radian */
#define DEG2RAD (M_PI / 180)       /*!< Number of radians in a degree */

#ifdef __cplusplus
extern "C" {
#endif //__cplusplus

/*----------------------------------------------------------------------------
 *        Types
 *----------------------------------------------------------------------------*/

/**
 * \brief Collection of geometric and aerodynamic parameters.
 */
typedef struct
{
    float m;                    /*!< Vehicle mass [kg] */
    float g;                    /*!< Acceleration due to gravity [m/(s^2)] */
    float rho;                  /*!< Air density [kg/(m^3)] */
    float S;                    /*!< Wing reference surface [m^2] */
    float Tmax;                 /*!< Maximum thrust [N] */
    float b;                    /*!<  */
    float c;                    /*!<  */
    float Ix;                   /*!<  */
    float Iy;                   /*!<  */
    float Iz;                   /*!<  */
    float Ixz;                  /*!<  */
    float incidence;            /*!<  */
    float windVelocity;         /*!<  */
    float windHeading;          /*!<  */
    float windElevation;        /*!<  */
    float turbulenceIntensity;  /*!<  */
    float servosResponseTime;   /*!<  */
    float engineResponseTime;   /*!<  */
    float initVelocity;         /*!<  */
} Params_t;

/**
 * \brief Collection of aerodynamic coefficients.
 */
typedef struct
{
    float Cd0;       /*!<  */
    float K;         /*!<  */
    float Cdb;       /*!<  */
    float Cyb;       /*!<  */
    float Cyda;      /*!<  */
    float Cydr;      /*!<  */
    float Cyp;       /*!<  */
    float Cyr;       /*!<  */
    float Cl0;       /*!<  */
    float Cla;       /*!<  */
    float Cllb;      /*!<  */
    float Cllda;     /*!<  */
    float Clldr;     /*!<  */
    float Cllp;      /*!<  */
    float Cllr;      /*!<  */
    float Cmm0;      /*!<  */
    float Cmma;      /*!<  */
    float Cmmda;     /*!<  */
    float Cmmde;     /*!<  */
    float Cmmdr;     /*!<  */
    float Cmmq;      /*!<  */
    float Cnnb;      /*!<  */
    float Cnnda;     /*!<  */
    float Cnndr;     /*!<  */
    float Cnnp;      /*!<  */
    float Cnnr;      /*!<  */
} AeroCoeffs_t;

/**
 * \brief Collection of control commands.
 */
typedef struct
{
    float da;        /*!<  */
    float de;        /*!<  */
    float dr;        /*!<  */
    float dt;        /*!<  */
} Controls_t;

/**
 * \brief Collection of internal variables.
 */
typedef struct
{
    float da;                 /*!<  */
    float de;                 /*!<  */
    float dr;                 /*!<  */
    float dt;                 /*!<  */
    float vx;                 /*!<  */
    float vy;                 /*!<  */
    float vz;                 /*!<  */
    float V;                  /*!<  */
    float alpha;              /*!<  */
    float beta;               /*!<  */
    float Cd;                 /*!<  */
    float Cy;                 /*!<  */
    float Cl;                 /*!<  */
    float Cll;                /*!<  */
    float Cmm;                /*!<  */
    float Cnn;                /*!<  */
    float D;                  /*!<  */
    float Y;                  /*!<  */
    float L;                  /*!<  */
    float LL;                 /*!<  */
    float MM;                 /*!<  */
    float NN;                 /*!<  */
    float vx_dot;             /*!<  */
    float vy_dot;             /*!<  */
    float vz_dot;             /*!<  */
    float roll_dot;           /*!<  */
    float pitch_dot;          /*!<  */
    float yaw_dot;            /*!<  */
    float p_dot;              /*!<  */
    float q_dot;              /*!<  */
    float r_dot;              /*!<  */
    float posNorth_dot;       /*!<  */
    float posEast_dot;        /*!<  */
    float alt_dot;            /*!<  */
    float lon;                /*!<  */
    float lat;                /*!<  */
    float total_time;         /*!<  */
    float Xa;                 /*!<  */
    float Ya;                 /*!<  */
    float Za;                 /*!<  */
    float Xt;                 /*!<  */
    float Yt;                 /*!<  */
    float Zt;                 /*!<  */
    float rotor_rpm;          /*!<  */
    float windNorth;          /*!<  */
    float windEast;           /*!<  */
    float windUp;             /*!<  */
    float TAS;                /*!<  */
    float TAS_North;          /*!<  */
    float TAS_East;           /*!<  */
    float TAS_Up;             /*!<  */
    float TAS_x;              /*!<  */
    float TAS_y;              /*!<  */
    float TAS_z;              /*!<  */
} Internals_t;

/**
 * \brief Collection of states.
 */
typedef struct
{
    float roll;      /*!<  */
    float pitch;     /*!<  */
    float yaw;       /*!<  */
    float p;         /*!<  */
    float q;         /*!<  */
    float r;         /*!<  */
    float posNorth;  /*!<  */
    float posEast;   /*!<  */
    float alt;       /*!<  */
} States_t;

/*----------------------------------------------------------------------------
 *        Exported functions
 *----------------------------------------------------------------------------*/

class Model
{
    public:
        Model(void);
        ~Model();
        
        uint16_t propagate(Controls_t controls, float dtime);

        inline void getStates(States_t * states)
        {
            states[0] = _states;
        }

        inline void getControls(Controls_t * controls)
        {
            controls[0] = _controls;
        }

        inline void getInternals(Internals_t * internals)
        {
            internals[0] = _internals;
        }

    private:
        Params_t _params;
        AeroCoeffs_t _aero;
        Controls_t _controls;
        Internals_t _internals;
        States_t _states;
};

#ifdef __cplusplus
}
#endif //__cplusplus

#endif // __DYNAMIC_MODEL_H__