#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h> 
#include <stdlib.h>

#ifdef __unix__
char* GenRandBytes(int nb, char* chars) {
    FILE* fptr = fopen("/dev/urandom", "rb");
    int i, j;
    for (i = 0, j = 0; i <= nb; i++) {
        chars[j] = fgetc(fptr);
        j++;
    };
    fclose(fptr);
    return chars;
};
#elif defined(_WIN32) || defined(_WIN64)
//I'm not sure if this actually works
char* GenRandBytes(int nb, char* chars) {
    memcpy(&chars, (void*)memcpy, nb);
    return chars;
};
#endif

static PyObject * generateRandomBytes(PyObject *self, PyObject *args) {
    int numBytes;
    if (!PyArg_ParseTuple(args, "i", &numBytes))
        return NULL;
    if (numBytes < 1 || numBytes > 1024)
        return NULL;
    #ifdef __unix__
    char chars[numBytes];
    #elif defined(_WIN32) || defined(_WIN64)
    char chars[1024]; //Windows (MSVC++) does not support C99 so dynamic array sizes are not allowed
    #endif
    return PyBytes_FromString(GenRandBytes(numBytes, chars));
};

static PyMethodDef CryptoMethods[] = {
    {"_generateRandomBytes", generateRandomBytes, METH_VARARGS, "Gets random bytes."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef Crypto = {
    PyModuleDef_HEAD_INIT,
    "_crypto",
    "Python C module for as3lib's flash.crypto library",
    -1,
    CryptoMethods
};
PyMODINIT_FUNC PyInit__crypto(void) {
    PyObject *module;
    module = PyModule_Create(&Crypto);
    if (module == NULL)
        return NULL;
    return module;
}