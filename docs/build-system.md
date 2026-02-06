# Build system

## Development

npyodbc uses the [meson](https://mesonbuild.com/) build system in order to both
_overlay_ (overwrite) as well as _diff_ (changes) files in pyodbc. Read more about
this in the official meson documentation
[here](https://mesonbuild.com/Wrap-dependency-system-manual.html#accepted-configuration-properties-for-wraps).

### Overlays

To create a completely new file, or to entirely replace a file in the `pyodbc`
subproject, add a new file to `subprojects/packagefiles/pyodbc/`. This will
overwrite any corresponding file in the `pyodbc` subproject during the build
process.

### Diffs

If on the other hand you want to modify a file in order to keep most if not all
of the original functionality, then you can create a diff file. The folder
`subprojects/packagefiles/patches` contains a `.clang-format` file that will not
format any files you copy there from pyodbc.

To create a diff file, make your changes to the file in the
`subprojects/pyodbc/` source, and then run the `diff` command of the modified
file.

meson does not automatically apply diff files to the subproject. You must
include a comma separated list of files that patches are supposed to be applied
to. This is done in the `subprojects/pyodbc.wrap` file, under the
`wrap-git.diff_files` key.

### C++ development

To set up the project for C++ development, it is recommended to use a debug
version of Python. Install the project with

```bash
pip install -ve . --no-build-isolation -Csetup-args=-Dbuildtype=debug -Cbuild-dir=build
```

to build the package in editable mode, and to create the meson build dir at
`build/`. Optionally, symlink the compilation database so that your dev tooling
can pick it up:

```bash
ln -sf build/compile_commands.json ./
```

This will link the `compile_commands.json` to the root of the repository,
allowing LSPs and other tools to find it.
