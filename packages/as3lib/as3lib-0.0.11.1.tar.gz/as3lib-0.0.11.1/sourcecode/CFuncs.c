#define PY_SSIZE_T_CLEAN
#include <Python.h>





static PyMethodDef CFuncsMethods[] = {


};

static struct PyModuleDef CFuncs = {
    PyModuleDef_HEAD_INIT,
    "CFuncs",
    NULL,
    -1,
    CFuncsMethods
};