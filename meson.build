project('npyodbc', 'cpp', version : '0.1.0')

python = import('python').find_installation()
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

pyodbc = subproject('pyodbc')
pyodbc_inc = pyodbc.get_variable('pyodbc_inc')

npyodbc_inc = include_directories('include')

python.extension_module(
  'npyodbc',
  ['src/npyodbcmodule.cpp'],
  dependencies : [
      python_dep,
      odbc_dep,
      numpy_dep,
  ],
  include_directories : [npyodbc_inc, pyodbc_inc],
  install : true,
)
