#ifndef _NPCONTAINER_H_
#define _NPCONTAINER_H_

#include <Python.h>

PyObject *Cursor_fetchdictarray(PyObject *self, PyObject *args, PyObject *kwargs);

extern char fetchdictarray_doc[];

extern Py_ssize_t iopro_text_limit;

#endif  // _NPCONTAINER_H_
