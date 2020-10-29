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
    // uint32_t fftSize;

    // if (!PyArg_ParseTuple(args, "i", &fftSize))
    // {
    //     return -1;
    // }    

    self->ptrObj = new Model();

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

    return Py_BuildValue("i", retval);
}

static PyObject * PyModel_getStates(PyModel* self, PyObject* args)
{
    States_t states;
    (self->ptrObj)->getStates(&states);

    return Py_BuildValue("ffffff", states.posNorth, states.posEast, states.alt, states.pitch, states.roll, states.yaw);
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

    return Py_BuildValue("fff", internals.lat, internals.lon, internals.rotor_rpm);
}

// static PyObject * optimcore_TsipCreatePacket(PyObject *self, PyObject *args)
// {
//     Py_buffer dst, src;
//     uint32_t dstcount;
//     if (!PyArg_ParseTuple(args, "s*s*", &dst, &src))
//     {
//         return NULL;
//     }
    
//     if (dst.len >= 11 + 2*src.len) // 1 (DLE) + 2*src.len (ALL DLE's) + 8 (ALL CRC DLE's) + 1 (DLE) + 1 (ETX)
//     {
//         dstcount = TsipCreatePacket((uint8_t*)dst.buf, (uint8_t*)src.buf, src.len);
//     }
//     else
//     {
//         return NULL;
//     }

//     return Py_BuildValue("k", dstcount);
// }

// static PyObject * optimcore_TsipInitRx(PyObject *self, PyObject *args)
// {
//     Py_buffer tsiprx, storageBuffer;
//     uint32_t maxPacketLength, maxPacketsToHold;
//     int32_t status;
//     if (!PyArg_ParseTuple(args, "s*s*II", &tsiprx, &storageBuffer, &maxPacketLength, &maxPacketsToHold))
//     {
//         return NULL;
//     }

//     status = TsipInitRx((TsipRx_t*)tsiprx.buf, (uint8_t*)storageBuffer.buf, maxPacketLength, maxPacketsToHold);

//     return Py_BuildValue("i", status);
// }

// static PyObject * optimcore_TsipProcessRawRx(PyObject *self, PyObject *args)
// {
//     Py_buffer tsiprx, storageBuffer;
//     uint32_t storageBufferLength;
//     int32_t status;
//     if (!PyArg_ParseTuple(args, "s*s*I", &tsiprx, &storageBuffer, &storageBufferLength))
//     {
//         return NULL;
//     }

//     status = TsipProcessRawRx((TsipRx_t*)tsiprx.buf, (uint8_t*)storageBuffer.buf, storageBufferLength);

//     return Py_BuildValue("i", status);
// }

// static PyObject * optimcore_TsipReadPacketRx(PyObject *self, PyObject *args)
// {
//     Py_buffer tsiprx, storageBuffer;
//     if (!PyArg_ParseTuple(args, "s*s*", &tsiprx, &storageBuffer))
//     {
//         return NULL;
//     }

//     int64_t packetsize = TsipReadPacketRx((TsipRx_t*)tsiprx.buf, (uint8_t*)storageBuffer.buf);

//     return Py_BuildValue("L", packetsize);
// }

// static PyObject * optimcore_TsipPendingPacketsRx(PyObject *self, PyObject *args)
// {
//     Py_buffer tsiprx;
//     if (!PyArg_ParseTuple(args, "s*", &tsiprx))
//     {
//         return NULL;
//     }

//     uint32_t pendingpackets = TsipPendingPacketsRx((TsipRx_t*)tsiprx.buf);

//     return Py_BuildValue("I", pendingpackets);
// }

// static PyObject * optimcore_TsipObtainStatistics(PyObject *self, PyObject *args)
// {
//     Py_buffer tsiprx;
//     if (!PyArg_ParseTuple(args, "s*", &tsiprx))
//     {
//         return NULL;
//     }

//     uint32_t goodPacketBytesReceived = ((TsipRx_t*)tsiprx.buf)->statistics.goodPacketBytesReceived;
//     uint32_t badPacketBytesReceived = ((TsipRx_t*)tsiprx.buf)->statistics.badPacketBytesReceived;
//     uint32_t goodPacketsReceived = ((TsipRx_t*)tsiprx.buf)->statistics.goodPacketsReceived;
//     uint32_t wrongPacketsReceived = ((TsipRx_t*)tsiprx.buf)->statistics.wrongPacketsReceived;
//     uint32_t badCrcPacketsReceived = ((TsipRx_t*)tsiprx.buf)->statistics.badCrcPacketsReceived;
//     uint32_t cutPacketsReceived = ((TsipRx_t*)tsiprx.buf)->statistics.cutPacketsReceived;
//     uint32_t tooLongPacketsReceived = ((TsipRx_t*)tsiprx.buf)->statistics.tooLongPacketsReceived;
//     uint32_t tooShortPacketsReceived = ((TsipRx_t*)tsiprx.buf)->statistics.tooShortPacketsReceived;
//     uint32_t overwrittenPackets = ((TsipRx_t*)tsiprx.buf)->statistics.overwrittenPackets;

//     return Py_BuildValue("IIIIIIIII", 
//                          goodPacketBytesReceived,
//                          badPacketBytesReceived,
//                          goodPacketsReceived,
//                          wrongPacketsReceived,
//                          badCrcPacketsReceived,
//                          cutPacketsReceived,
//                          tooLongPacketsReceived,
//                          tooShortPacketsReceived,
//                          overwrittenPackets);
// }

static PyObject * optimcore_GetStatesSize(PyObject *self, PyObject *args)
{
    return Py_BuildValue("I", sizeof(States_t));
}

static PyMethodDef PyModel_methods[] = 
{
    // {"TsipCreatePacket", optimcore_TsipCreatePacket, METH_VARARGS, "Create TSIP packet from data: CRC, DLE/ETX fields and escaped DLEs are inserted."},
    // {"TsipInitRx", optimcore_TsipInitRx, METH_VARARGS, "Initialize TsipRx_t state machine and data structures."},
    // {"TsipProcessRawRx", optimcore_TsipProcessRawRx, METH_VARARGS, "Process raw TSIP data and save packets to internal circular FIFO."},
    // {"TsipReadPacketRx", optimcore_TsipReadPacketRx, METH_VARARGS, "Read received TSIP packet content, including ID and Payload."},
    // {"TsipPendingPacketsRx", optimcore_TsipPendingPacketsRx, METH_VARARGS, "Number of pending packets available to be read with TsipReadPacketRx in the TsipRx_t state machine passed."},
    // {"TsipObtainStatistics", optimcore_TsipObtainStatistics, METH_VARARGS, "Returns data statistics"},
    {"propagate", (PyCFunction)PyModel_propagate, METH_VARARGS, "Propagates model"},
    {"getStates", (PyCFunction)PyModel_getStates, METH_VARARGS, "Get states"},
    {"getControls", (PyCFunction)PyModel_getControls, METH_VARARGS, "Get controls"},
    {"getInternals", (PyCFunction)PyModel_getInternals, METH_VARARGS, "Get internals"},
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