# npyodbc

`pyodbc` extended to use NumPy.

## Installation

The development installations below includes Microsoft SQL Server 2022. The password for
the server can be found in the Dockerfile and is `StrongPassword2022!`, which is not
secure. It is automatically installed when if you use the `devcontainer` in VSCode, or
if you build the Docker container. See the [Getting Started intro]() in the
documentation for more information on how to set up the server for testing purposes.

### Dev install using VSCode

Choose to open the repo in the supplied container if you use VSCode.

### Dev install using Docker

Run the following commands using docker to install the project into a container. This is
similar to the `devcontainer` in VSCode.

```bash
# Build the image
docker build . --tag npyodbc
# Start a container
docker run -p 1401:1433 --name npyodbc --hostname npyodbc -m 16GB -d npyodbc
# (OPTIONAL) Log into the container
docker exec -it npyodbc bash
```

### Dev install using conda

Local development using `conda` can be done with the following commands.

```bash
conda env create --file environment.yaml
conda activate npyodbc-dev
pip install .
```
