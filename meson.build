project('npyodbc', 'cpp', version : '0.1.0')

python = import('python').find_installation(pure: false)
python_dep = python.dependency()

# ODBC driver needs to be installed by the OS.
compiler = meson.get_compiler('cpp')
odbc_dep = compiler.find_library('odbc')

numpy_inc = run_command(
  python,
  ['-c', 'import os, numpy; print(os.path.relpath(numpy.get_include()))'],
  check : true,
).stdout().strip()
numpy_dep = declare_dependency(include_directories : numpy_inc)

pyodbc_proj = subproject('pyodbc')
pyodbc_dep = dependency('pyodbc')

npyodbc_inc = include_directories('include')
npyodbc_sources = [
  'src/npcontainer.cpp',
  'src/npyodbcmodule.cpp'
]

python.install_sources(
  [
    'tests/__init__.py',
    'tests/conftest.py',
    'tests/mysql_test.py',
    'tests/postgresql_test.py',
    'tests/sqlserver_test.py',
  ],
  subdir: 'npyodbc/tests',
)
python.install_sources(
  [
    'tests/old/README.md',
    'tests/old/accesstests.py',
    'tests/old/empty.accdb',
    'tests/old/empty.mdb',
    'tests/old/exceltests.py',
    'tests/old/informix_test.py',
    'tests/old/sparktests.py',
    'tests/old/sqldwtests.py',
    'tests/old/sqlitetests.py',
  ],
  subdir: 'npyodbc/tests/old',
)

# Build the npyodbc module
python.extension_module(
  'npyodbc',
  npyodbc_sources,
  dependencies : [
    python_dep,
    odbc_dep,
    numpy_dep,
    pyodbc_dep,
  ],
  include_directories : [npyodbc_inc],
  install : true,
  subdir: 'npyodbc',
)
