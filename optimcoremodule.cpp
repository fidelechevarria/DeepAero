#include <Python.h>
#include "OptimCore/include/dynamicModel.hpp"

#define MODULE_DOC "Evolutionary optimization library for parameter estimation."

typedef struct
{
    PyObject_HEAD
    Model * ptrObj;
} PyModel;


static int PyModel_init(PyModel *self, PyObject *args, PyObject *kwds)
// initialize PyModel Object
{
    float freq;

    if (!PyArg_ParseTuple(args, "f", &freq))
    {
        return -1;
    }

    self->ptrObj = new Model(freq);

    return 0;
}

static void PyModel_dealloc(PyModel * self)
// destruct the object
{
    delete self->ptrObj;
    Py_TYPE(self)->tp_free(self);
}

static PyObject * PyModel_propagate(PyModel* self, PyObject* args)
{
    float da, de, dr, dt, dtime;
    uint32_t retval;

    if (!PyArg_ParseTuple(args, "fffff", &da, &de, &dr, &dt, &dtime))
    {
        return NULL;
    }

    Controls_t controls = {da, de, dr, dt};
    retval = (self->ptrObj)->propagate(controls, dtime);

    return Py_BuildValue("I", retval);
}

static PyObject * PyModel_loadTrajectory(PyModel* self, PyObject* args)
{
    char * file;
    uint32_t nsamples;
    
    if (!PyArg_ParseTuple(args, "sI", &file, &nsamples))
    {
        return NULL;
    }

    (self->ptrObj)->loadTrajectory((std::string)file, nsamples);

    return Py_BuildValue("i", 0);
}

static PyObject * PyModel_getTrajectorySample(PyModel* self, PyObject* args)
{
    uint32_t idx;

    if (!PyArg_ParseTuple(args, "I", &idx))
    {
        return NULL;
    }

    float states[17];
    (self->ptrObj)->getTrajectorySample(states, idx);

    return Py_BuildValue("fffffffffffffffff", states[0], states[1], states[2], states[3], states[4], states[5],
                                              states[6], states[7], states[8], states[9], states[10], states[11],
                                              states[12], states[13], states[14], states[15], states[16]);
}

static PyObject * PyModel_evaluate(PyModel* self, PyObject* args)
{
    float coefs[26];
    bool useLinVels;
    int32_t numberOfSamplesToUse;

    if (!PyArg_ParseTuple(args, "ffffffffffffffffffffffffffpi",
                          &coefs[0], &coefs[1], &coefs[2], &coefs[3], &coefs[4], &coefs[5],
                          &coefs[6], &coefs[7], &coefs[8], &coefs[9], &coefs[10], &coefs[11],
                          &coefs[12], &coefs[13], &coefs[14], &coefs[15], &coefs[16], &coefs[17],
                          &coefs[18], &coefs[19], &coefs[20], &coefs[21], &coefs[22], &coefs[23],
                          &coefs[24], &coefs[25], &useLinVels, &numberOfSamplesToUse))
    {
        return NULL;
    }

    AeroCoeffs_t aero = {coefs[0], coefs[1], coefs[2], coefs[3], coefs[4], coefs[5],
                         coefs[6], coefs[7], coefs[8], coefs[9], coefs[10], coefs[11],
                         coefs[12], coefs[13], coefs[14], coefs[15], coefs[16], coefs[17],
                         coefs[18], coefs[19], coefs[20], coefs[21], coefs[22], coefs[23],
                         coefs[24], coefs[25]};
    float retval = (self->ptrObj)->evaluate(aero, useLinVels, numberOfSamplesToUse);

    return Py_BuildValue("f", retval);
}

static PyObject * PyModel_getStates(PyModel* self, PyObject* args)
{
    States_t states;
    (self->ptrObj)->getStates(&states);

    return Py_BuildValue("ffffffffffff", states.posNorth, states.posEast, states.alt,
                                         states.pitch, states.roll, states.yaw,
                                         states.p, states.q, states.r,
                                         states.vx, states.vy, states.vz);
}

static PyObject * PyModel_getControls(PyModel* self, PyObject* args)
{
    Controls_t controls;
    (self->ptrObj)->getControls(&controls);

    return Py_BuildValue("ffff", controls.da, controls.de, controls.dr, controls.dt);
}

static PyObject * PyModel_getInternals(PyModel* self, PyObject* args)
{
    Internals_t internals;
    (self->ptrObj)->getInternals(&internals);

    return Py_BuildValue("ffffffffffff", internals.lat, internals.lon, internals.rotor_rpm,
                                         internals.V, internals.alpha, internals.beta,
                                         internals.D, internals.Y, internals.L,
                                         internals.LL, internals.MM, internals.NN);
}

static PyObject * PyModel_getAeroCoeffs(PyModel* self, PyObject* args)
{
    AeroCoeffs_t coefs;
    (self->ptrObj)->getAeroCoeffs(&coefs);

    return Py_BuildValue("ffffffffffffffffffffffffff",
                         coefs.Cd0, coefs.K, coefs.Cdb, coefs.Cyb, coefs.Cyda, coefs.Cydr,
                         coefs.Cyp, coefs.Cyr, coefs.Cl0, coefs.Cla, coefs.Cllb, coefs.Cllda,
                         coefs.Clldr, coefs.Cllp, coefs.Cllr, coefs.Cmm0, coefs.Cmma, coefs.Cmmda,
                         coefs.Cmmde, coefs.Cmmdr, coefs.Cmmq, coefs.Cnnb, coefs.Cnnda, coefs.Cnndr,
                         coefs.Cnnp, coefs.Cnnr);
}

static PyObject * PyModel_setStates(PyModel* self, PyObject* args)
{
    float statesRcv[12];

    if (!PyArg_ParseTuple(args, "ffffffffffff",
                          &statesRcv[0], &statesRcv[1], &statesRcv[2],
                          &statesRcv[3], &statesRcv[4], &statesRcv[5],
                          &statesRcv[6], &statesRcv[7], &statesRcv[8],
                          &statesRcv[9], &statesRcv[10], &statesRcv[11]))
    {
        return NULL;
    }

    States_t states = {statesRcv[0], statesRcv[1], statesRcv[2],
                       statesRcv[3], statesRcv[4], statesRcv[5],
                       statesRcv[6], statesRcv[7], statesRcv[8],
                       statesRcv[9], statesRcv[10], statesRcv[11]};
    (self->ptrObj)->setStates(states);

    return Py_BuildValue("i", 0);
}

static PyObject * PyModel_setControls(PyModel* self, PyObject* args)
{
    float controlsRcv[4];

    if (!PyArg_ParseTuple(args, "ffff", &controlsRcv[0], &controlsRcv[1], &controlsRcv[2], &controlsRcv[3]))
    {
        return NULL;
    }

    Controls_t controls = {controlsRcv[0], controlsRcv[1], controlsRcv[2], controlsRcv[3]};
    (self->ptrObj)->setControls(controls);

    return Py_BuildValue("i", 0);
}

static PyObject * PyModel_setInternals(PyModel* self, PyObject* args)
{
    float internalsRcv[51];

    if (!PyArg_ParseTuple(args, "ffffffffffffffffffffffffffffffffffffffffffffffffffffff",
                         &internalsRcv[0], &internalsRcv[1], &internalsRcv[2], &internalsRcv[3], &internalsRcv[4], &internalsRcv[5],
                         &internalsRcv[6], &internalsRcv[7], &internalsRcv[8], &internalsRcv[9], &internalsRcv[10], &internalsRcv[11],
                         &internalsRcv[12], &internalsRcv[13], &internalsRcv[14], &internalsRcv[15], &internalsRcv[16], &internalsRcv[17],
                         &internalsRcv[18], &internalsRcv[19], &internalsRcv[20], &internalsRcv[21], &internalsRcv[22], &internalsRcv[23],
                         &internalsRcv[24], &internalsRcv[25], &internalsRcv[26], &internalsRcv[27], &internalsRcv[28], &internalsRcv[29],
                         &internalsRcv[30], &internalsRcv[31], &internalsRcv[32], &internalsRcv[33], &internalsRcv[34], &internalsRcv[35],
                         &internalsRcv[36], &internalsRcv[37], &internalsRcv[38], &internalsRcv[39], &internalsRcv[40], &internalsRcv[41],
                         &internalsRcv[42], &internalsRcv[43], &internalsRcv[44], &internalsRcv[45], &internalsRcv[46], &internalsRcv[47],
                         &internalsRcv[48], &internalsRcv[49], &internalsRcv[50]))
    {
        return NULL;
    }

    Internals_t internals = {internalsRcv[0], internalsRcv[1], internalsRcv[2], internalsRcv[3], internalsRcv[4], internalsRcv[5],
                             internalsRcv[6], internalsRcv[7], internalsRcv[8], internalsRcv[9], internalsRcv[10], internalsRcv[11],
                             internalsRcv[12], internalsRcv[13], internalsRcv[14], internalsRcv[15], internalsRcv[16], internalsRcv[17],
                             internalsRcv[18], internalsRcv[19], internalsRcv[20], internalsRcv[21], internalsRcv[22], internalsRcv[23],
                             internalsRcv[24], internalsRcv[25], internalsRcv[26], internalsRcv[27], internalsRcv[28], internalsRcv[29],
                             internalsRcv[30], internalsRcv[31], internalsRcv[32], internalsRcv[33], internalsRcv[34], internalsRcv[35],
                             internalsRcv[36], internalsRcv[37], internalsRcv[38], internalsRcv[39], internalsRcv[40], internalsRcv[41],
                             internalsRcv[42], internalsRcv[43], internalsRcv[44], internalsRcv[45], internalsRcv[46], internalsRcv[47],
                             internalsRcv[48], internalsRcv[49], internalsRcv[50]};
    (self->ptrObj)->setInternals(internals);

    return Py_BuildValue("i", 0);
}

static PyObject * PyModel_setAeroCoeffs(PyModel* self, PyObject* args)
{
    float aeroRcv[26];

    if (!PyArg_ParseTuple(args, "ffffffffffffffffffffffffff",
                         &aeroRcv[0], &aeroRcv[1], &aeroRcv[2], &aeroRcv[3], &aeroRcv[4], &aeroRcv[5],
                         &aeroRcv[6], &aeroRcv[7], &aeroRcv[8], &aeroRcv[9], &aeroRcv[10], &aeroRcv[11],
                         &aeroRcv[12], &aeroRcv[13], &aeroRcv[14], &aeroRcv[15], &aeroRcv[16], &aeroRcv[17],
                         &aeroRcv[18], &aeroRcv[19], &aeroRcv[20], &aeroRcv[21], &aeroRcv[22], &aeroRcv[23],
                         &aeroRcv[24], &aeroRcv[25]))
    {
        return NULL;
    }

    AeroCoeffs_t aero = {aeroRcv[0], aeroRcv[1], aeroRcv[2], aeroRcv[3], aeroRcv[4], aeroRcv[5],
                         aeroRcv[6], aeroRcv[7], aeroRcv[8], aeroRcv[9], aeroRcv[10], aeroRcv[11],
                         aeroRcv[12], aeroRcv[13], aeroRcv[14], aeroRcv[15], aeroRcv[16], aeroRcv[17],
                         aeroRcv[18], aeroRcv[19], aeroRcv[20], aeroRcv[21], aeroRcv[22], aeroRcv[23],
                         aeroRcv[24], aeroRcv[25]};
    (self->ptrObj)->setAeroCoeffs(aero);

    return Py_BuildValue("i", 0);
}

static PyObject * optimcore_GetStatesSize(PyObject *self, PyObject *args)
{
    return Py_BuildValue("I", sizeof(States_t));
}

static PyMethodDef PyModel_methods[] = 
{
    {"propagate", (PyCFunction)PyModel_propagate, METH_VARARGS, "Propagates model"},
    {"loadTrajectory", (PyCFunction)PyModel_loadTrajectory, METH_VARARGS, "Loads trajectory"},
    {"getTrajectorySample", (PyCFunction)PyModel_getTrajectorySample, METH_VARARGS, "Gets trajectory sample"},
    {"evaluate", (PyCFunction)PyModel_evaluate, METH_VARARGS, "Evaluate"},
    {"getStates", (PyCFunction)PyModel_getStates, METH_VARARGS, "Get states"},
    {"getControls", (PyCFunction)PyModel_getControls, METH_VARARGS, "Get controls"},
    {"getInternals", (PyCFunction)PyModel_getInternals, METH_VARARGS, "Get internals"},
    {"getAeroCoeffs", (PyCFunction)PyModel_getAeroCoeffs, METH_VARARGS, "Get aerodynamic coefficients"},
    {"setStates", (PyCFunction)PyModel_setStates, METH_VARARGS, "Set states"},
    {"setControls", (PyCFunction)PyModel_setControls, METH_VARARGS, "Set controls"},
    {"setInternals", (PyCFunction)PyModel_setInternals, METH_VARARGS, "Set internals"},
    {"setAeroCoeffs", (PyCFunction)PyModel_setAeroCoeffs, METH_VARARGS, "Set aerodynamic coefficients"},
    {"GetStatesSize", (PyCFunction)optimcore_GetStatesSize, METH_VARARGS, "Gets states size"},
    {NULL}  /* Sentinel */
};

static struct PyModuleDef OptimCoreModule = 
{
   PyModuleDef_HEAD_INIT,
   "model",
   MODULE_DOC,
   -1,
   PyModel_methods
};

static PyTypeObject PyModelType =
{
    PyVarObject_HEAD_INIT(NULL, 0)
    "model.Model"   /* tp_name */
};

PyMODINIT_FUNC PyInit_optimcore(void)
// create the module
{
    PyObject* m;

    PyModelType.tp_new = PyType_GenericNew;
    PyModelType.tp_basicsize = sizeof(PyModel);
    PyModelType.tp_dealloc = (destructor) PyModel_dealloc;
    PyModelType.tp_flags = Py_TPFLAGS_DEFAULT;
    PyModelType.tp_doc = "Model objects";
    PyModelType.tp_methods = PyModel_methods;
    //~ PyModelType.tp_members = Noddy_members;
    PyModelType.tp_init = (initproc)PyModel_init;

    if (PyType_Ready(&PyModelType) < 0)
    {
        return NULL;
    }

    m = PyModule_Create(&OptimCoreModule);
    if (m == NULL)
    {
        return NULL;
    }

    Py_INCREF(&PyModelType);
    PyModule_AddObject(m, "Model", (PyObject *)&PyModelType); // Add Model object to the module
    return m;
}