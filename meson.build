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

icu_dep = dependency('icu-uc')

npyodbc_inc = include_directories('include')
npyodbc_sources = [
  'src/npcontainer.cpp',
  'src/npyodbcmodule.cpp'
]

add_project_arguments(
  [
    '-DPYODBC_VERSION=' + meson.project_version(),
    '-Wno-write-strings',
    '-Wno-deprecated-declarations',
  ],
  language: 'cpp'
)

odbc_config = find_program('odbc_config', required : false)

odbc_cflags = []
odbc_lflags = []
if odbc_config.found()
  odbc_cflags = run_command([odbc_config, '--cflags'], check : true).stdout().strip()
  odbc_lflags = run_command([odbc_config, '--libs'], check : true).stdout().strip()
endif

# Build the npyodbc module
python.extension_module(
  'npyodbc',
  npyodbc_sources,
  dependencies : [
    python_dep,
    odbc_dep,
    numpy_dep,
    pyodbc_dep,
    icu_dep
  ],
  include_directories : [npyodbc_inc],
  install : true,
  cpp_args : odbc_cflags,
  link_args : odbc_lflags,
)
