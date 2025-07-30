#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <pthread.h>
#include <stdbool.h>

#include "sear.h"

pthread_mutex_t sear_mutex = PTHREAD_MUTEX_INITIALIZER;

// Entry point to the call_sear() function
static PyObject* call_sear(PyObject* self, PyObject* args, PyObject* kwargs) {
  PyObject* result_dictionary;
  PyObject* debug_pyobj;
  const char* request_as_string;
  Py_ssize_t request_length;
  bool debug            = false;

  static char* kwlist[] = {"request", "debug", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|O", kwlist,
                                   &request_as_string, &request_length,
                                   &debug_pyobj)) {
    return NULL;
  }

  debug = PyObject_IsTrue(debug_pyobj);

  // Since SEAR manages sear_result_t as a static structure,
  // we need to use a mutex to make this thread safe.
  // Technically we shouldn't need this because the Python GIL,
  // but we will set this up anyways to be safe.
  pthread_mutex_lock(&sear_mutex);

  sear_result_t* result = sear(request_as_string, request_length, debug);

  result_dictionary      = Py_BuildValue(
      "{s:y#,s:y#,s:s#}", "raw_request", result->raw_request,
      result->raw_request_length, "raw_result", result->raw_result,
      result->raw_result_length, "result_json", result->result_json,
      result->result_json_length);

  pthread_mutex_unlock(&sear_mutex);

  return result_dictionary;
}

// Method definition
static PyMethodDef _C_methods[] = {
    {"call_sear", (PyCFunction)call_sear, METH_VARARGS | METH_KEYWORDS,
     "A unified and standardized interface to RACF callable services"},
    {NULL}
};

// Module definition
static struct PyModuleDef _C_module_def = {
    PyModuleDef_HEAD_INIT, "_C",
    "A unified and standardized interface to RACF callable services", -1,
    _C_methods};

// Module initialization function
// 'unusedFunction' is a false positive since 'PyInit__C()' is used by the
// Python interpreter
// cppcheck-suppress unusedFunction
PyMODINIT_FUNC PyInit__C(void) {
  Py_Initialize();
  return PyModule_Create(&_C_module_def);
}
