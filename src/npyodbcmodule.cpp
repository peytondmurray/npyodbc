#include <Python.h>
#include <sql.h>
#include <sqlext.h>

#include "npcontainer.h"
#include "pyodbcmodule.h"

static PyObject *check_connection(PyObject *self) {
    SQLHENV env;
    SQLRETURN ret;

    ret = SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, &env);
    if (ret == SQL_SUCCESS || ret == SQL_ROW_SUCCESS_WITH_INFO) {
        return PyUnicode_FromString("env allocation worked");
    } else {
        return PyUnicode_FromString("env allocation failed");
    }
    SQLFreeHandle(SQL_HANDLE_ENV, env);
}

static PyMethodDef methods[] = {
        {"check_connection", (PyCFunction)check_connection, METH_NOARGS, NULL},
        {NULL, NULL, 0, NULL},
};

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT, "npyodbc", NULL, -1, methods, NULL, NULL, NULL, NULL,
};

PyMODINIT_FUNC PyInit_npyodbc(void) {
    PyObject *module = PyModule_Create(&moduledef);
    if (!module) {
        return NULL;
    }
    return module;
}
