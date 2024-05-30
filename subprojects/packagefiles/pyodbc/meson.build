project('pyodbc', 'cpp', version : '5.1.0')

python = import('python').find_installation()
python_dependency = python.dependency()

compiler = meson.get_compiler('cpp')

# ODBC driver needs to be installed by the OS.
odbc_dependency = compiler.find_library('odbc')

pyodbc_sources = [
  'src/cnxninfo.cpp',
  'src/connection.cpp',
  'src/cursor.cpp',
  'src/decimal.cpp',
  'src/errors.cpp',
  'src/getdata.cpp',
  'src/params.cpp',
  'src/pyodbcdbg.cpp',
  'src/pyodbcmodule.cpp',
  'src/row.cpp',
  'src/textenc.cpp',
]
pyodbc_inc = include_directories('src')
# pyodbc_headers = [
#   'src/cnxninfo.h',
#   'src/connection.h',
#   'src/cursor.h',
#   'src/dbspecific.h',
#   'src/decimal.h',
#   'src/errors.h',
#   'src/getdata.h',
#   'src/params.h',
#   'src/pyodbc.h',
#   'src/pyodbcmodule.h',
#   'src/resource.h',
#   'src/row.h',
#   'src/textenc.h',
#   'src/wrapper.h',
# ]

# pyodbc_dep = declare_dependency(include_directories : include_directories('src'))

python.extension_module(
  'pyodbc',
  pyodbc_sources,
  dependencies : [
    python_dependency,
    odbc_dependency,
  ],
  install : false,
)
