#include <Python.h>
#include "methodobject.h"
#include "modsupport.h"
#include "pyodbc.h"
#include "wrapper.h"
#include "textenc.h"
#include "connection.h"
#include "pyodbcmodule.h"

#include "numpy/numpyconfig.h"
#include <sql.h>
#include <sqlext.h>

PyMODINIT_FUNC
PyInit__npyodbc(void)
{
    PyObject *mod = initialize_pyodbc();
    if (mod == NULL) {
        PyErr_SetString(PyExc_ImportError, "Error initializing pyodbc.");
        return NULL;
    }

    // Add the numpy ABI version this package was compiled against
    PyModule_AddIntConstant(
        mod,
        "numpy_abi_version",
        NPY_VERSION
    );

    return mod;
}
