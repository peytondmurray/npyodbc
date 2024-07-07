project(
  'npyodbc',
  'cpp',
  version: run_command(['python', '-m', 'setuptools_scm'], check: true).stdout().strip(),
)

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

add_project_arguments('-DPYODBC_VERSION=' + meson.project_version(), language: 'cpp')

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
)
