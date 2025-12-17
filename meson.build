project(
  'npyodbc',
  'cpp',
  version: run_command(['python', '-m', 'setuptools_scm'], check: true).stdout().strip(),
)

python = import('python').find_installation(pure: false)
python_dep = python.dependency()

# ODBC driver needs to be installed by the OS.
compiler = meson.get_compiler('cpp')

numpy_inc = include_directories(
  run_command(
    python,
    ['-c', 'import os, numpy; print(os.path.relpath(numpy.get_include()))'],
    check : true,
  ).stdout().strip()
)
numpy_dep = declare_dependency(include_directories: numpy_inc)

subproject('pyodbc')
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

includes = []
deps = []
cflags = []
lflags = []

if host_machine.system() == 'windows'
  # Copy additional windows cflags from setup.py
  cflags += [
    '/Wall',
    '/wd4514',
    '/wd4820',
    '/wd4668',
    '/wd4711',
    '/wd4100',
    '/wd4127',
    '/wd4191',
    '/d2FH4-',
  ]

  lflags = ['/d2:-FH4-']
  deps += [
    compiler.find_library('odbc32', required: true),
    compiler.find_library('advapi32', required: true),
  ]
else # Unix

  # First try to detect odbc via meson
  odbc_dep = compiler.find_library('odbc', required: false)
  if odbc_dep.found()
    # If we can find odbc via meson, no other action is needed
    deps += [odbc_dep]

  else
    # Otherwise, we try to use odbc_config
    odbc_config = find_program('odbc_config', required: false)
    if odbc_config.found()
      cflags += run_command([odbc_config, '--cflags'], check: true).stdout().strip().split()
      lflags += run_command([odbc_config, '--libs'], check: true).stdout().strip().split()
    else
      error('Cannot find either the odbc library or the odbc_config binary. Aborting.')
    endif
  endif
endif


# Build the npyodbc module
python.extension_module(
  'npyodbc',
  npyodbc_sources,
  dependencies : [
    python_dep,
    numpy_dep,
    pyodbc_dep,
    icu_dep,
  ] + deps,
  include_directories : [npyodbc_inc] + includes,
  install : true,
  cpp_args : cflags,
  link_args : lflags,
)
