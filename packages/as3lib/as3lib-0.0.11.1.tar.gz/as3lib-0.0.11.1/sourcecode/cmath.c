#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>

double itkwcalc(int neww, int newh, int startw, int starth) {
   double xmult = (double)(100*neww)/startw;
   double ymult = (double)(100*newh)/starth;
   if (xmult > ymult)
      return ymult;
   return xmult;
};

static PyObject * itk_windowcalculate(PyObject *self, PyObject *args) {
   int sw, sh, nw, nh;
   if (!PyArg_ParseTuple(args, "iiii", &nw, &nh, &sw, &sh))
      return NULL;
   return PyFloat_FromDouble(itkwcalc(nw,nh,sw,sh));
};

static PyObject * itk_windowresizefont(PyObject *self, PyObject *args) {
   int font;
   float mult;
   if (!PyArg_ParseTuple(args, "if", &font, &mult))
      return NULL;
   return PyLong_FromLong((long)round(font*mult*0.01));
};

static PyObject * multdivide(PyObject *self, PyObject *args) {
   double a, b, c;
   if (!PyArg_ParseTuple(args, "ddd", &a, &b, &c))
      return NULL;
   return PyFloat_FromDouble(a*b/c);
};

static PyObject * roundedmultdivide(PyObject *self, PyObject *args) {
   double a, b, c;
   if (!PyArg_ParseTuple(args, "ddd", &a, &b, &c))
      return NULL;
   return PyFloat_FromDouble(round(a*b)/c);
};

static PyMethodDef cmathMethods[] = {
   {"calculate", itk_windowcalculate, METH_VARARGS, "window.calculate function in the interface_tk module."},
   {"resizefont", itk_windowresizefont, METH_VARARGS, "window.resizefont function in the interface_tk module."},
   {"multdivide", multdivide, METH_VARARGS, "a*b/c"},
   {"roundedmultdivide", roundedmultdivide, METH_VARARGS, "Originally used as a workaround to round to a specific decimal place. round(a*b)/c"},
   {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cmath = {
   PyModuleDef_HEAD_INIT,
   "cmath",
   NULL,
   -1,
   cmathMethods
};

PyMODINIT_FUNC PyInit_cmath(void) {
   return PyModule_Create(&cmath);
}
