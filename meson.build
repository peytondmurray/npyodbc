project('pyodbc_numpy', 'cpp')

python = import('python').find_installation(pure: false)
python_dependency = python.dependency()

compiler = meson.get_compiler('cpp')
odbc_dependeny = compiler.find_library('odbc', required: false)

numpy_include_directory = run_command(
  python,
  [
    '-c',
    'import os, numpy; print(os.path.relpath(numpy.get_include()))'
  ],
  check: true,
).stdout().strip()
numpy_dependency = declare_dependency(include_directories: numpy_include_directory)

pyodbc_dependency = dependency('pyodbc', fallback: ['pyodbc', 'pyodbc_dep'])

python.extension_module(
  'pyodbc_numpy',
  ['src/pyodbc_numpy/pyodbc_numpy.cpp'],
  dependencies: [
      python_dependency,
      odbc_dependeny,
      numpy_dependency,
      pyodbc_dependency,
  ],
  install: true,
)
