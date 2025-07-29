#define PY_SSIZE_T_CLEAN
#include <Python.h>









static PyMethodDef TopLevelMethods[] = {


};

static struct PyModuleDef TopLevel = {
    PyModuleDef_HEAD_INIT,
    "TopLevel",
    NULL,
    -1,
    TopLevelMethods
};