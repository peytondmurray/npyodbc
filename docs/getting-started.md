# Getting Started

## Background

`npyodbc` builds on top of [`pyodbc`](https://github.com/mkleehammer/pyodbc),
extending it to write directly to [NumPy](https://numpy.org) arrays without
passing through Python object types. This yields substantial performance
benefits, but it comes at the cost of a slightly more complex build system. We
use `pyodbc` as a subproject within the `npyodbc` project, and leverage
[`meson`](https://mesonbuild.com) as the build system to help patch and extend
`pyodbc`. With the help of `meson` we can use the latest release of `pyodbc` and
extend it to include returning result sets from an ODBC compliant SQL server as
NumPy arrays.

Documentation for `pyodbc` can be found on their
[wiki](https://github.com/mkleehammer/pyodbc/wiki). We will only include
components of that wiki that directly relate to how to use `npyodbc`. For
advanced `pyodbc` usage, please refer to the `pyodbc` wiki.

## Introduction

All example code will assume you have Microsoft SQL 2022 running locally in a
Docker container. Start the npyodbc Docker container by navigating to
`./containers/` and executing the following command in your
terminal:

```bash
# Build the Docker image and tag it as npyodbc docker
build . --tag npyodbc

# Start a container using the npyodbc image and name it npyodbc as well docker
run -p 1401:1433 --name npyodbc --hostname npyodbc -m 16GB -d npyodbc

# (OPTIONAL) Log into the container docker exec -it npyodbc bash
```

If you log into the container, you can access the SQL 2022 command line by
navigating to it and running the `sqlcmd` command. Below we include the user
name and password for logging into the SQL 2022 server.

```bash
# Navigate to the SQL bin directory cd
/opt/mssql-tools/bin

# Open the SQL command line utility ./sqlcmd -U SA -P StrongPassword2022! -S localhost
```

You can now add a test table manually here that you can access using `npyodbc`.

```sql
DROP TABLE test;
CREATE TABLE test (columnA VARBINARY(20), columnB VARBINARY(20));
INSERT INTO test VALUES(CAST('zort' AS VARBINARY(20)), CAST('troz' AS VARBINARY(20)));
INSERT INTO test VALUES(CAST('poit' AS VARBINARY(20)), CAST('rubber pants' AS VARBINARY(20)));
GO;
```

You must supply the `GO` command otherwise the commands will not get executed by
SQL 2022. The `QUIT` command will exit out of `sqlcmd` if you so wish to do so.

## Creating a Table With `npyodbc`

```python
import npyodbc

driver = "ODBC Driver 17 for SQL Server"
server = "localhost,1401"
uid = "SA"
# NOTE: This is not secure and should not be used only for testing purposes.
pwd = "StrongPassword2022!"
connection_string = f"DRIVER={driver};SERVER={server};UID={uid};PWD={pwd}"
# Connect to the database running in Docker, or in the VSCode devcontainer.
connection = npyodbc.connect(connection_string)

# Create a test table.
with connection as conn:
    try:
        conn.execute("DROP TABLE test;")
    except ProgrammingError:
        print("Table `test` already exists.")
with connection as conn:
    conn.execute("CREATE TABLE test (columnA VARBINARY(20), columnB VARBINARY(20));")

# Add data to the test table.
with connection as conn:
    conn.execute(
        "INSERT INTO test "
        "VALUES(CAST('zort' AS VARBINARY(20)), CAST('troz' AS VARBINARY(20)));"
    )
    conn.execute(
        "INSERT INTO test "
        "VALUES(CAST('poit' AS VARBINARY(20)), CAST('rubber pants' AS VARBINARY(20)));"
    )

# Retrieve the data from the test table.
connection.execute("SELECT * FROM test;").fetchall()
```

We have used the `with` context in Python for executing commands to the connected
database. If you want, you can also create a cursor with the statement to execute, and
then commit the command to the connection, example below.

```python
import npyodbc

driver = "ODBC Driver 17 for SQL Server"
server = "localhost,1401"
uid = "SA"
# NOTE: This is not secure and should not be used only for testing purposes.
pwd = "StrongPassword2022!"
connection_string = f"DRIVER={driver};SERVER={server};UID={uid};PWD={pwd}"
# Connect to the database running in Docker, or in the VSCode devcontainer.
connection = npyodbc.connect(connection_string)

# Create a cursor
cursor = connection.cursor()
sql = "CREATE TABLE test (columnA VARBINARY(20), columnB VARBINARY(20));"
cursor.execute(sql)
connection.commit()
```

## Creating a Table Using `sqlcmd`

If instead you want to use `sqlcmd` to create the table, you can do so. You will
need to log into Docker container, or use the terminal in the VSCode
devcontainer.

```bash
# Change directory to the tool
cd /opt/mssql-tools/bin
# Start the sqlcmd tool
./sqlcmd -S localhost -U SA -P StrongPassword2022!
```

Below we will create a test table and add data to it.

```sql
1> CREATE TABLE test (columnA VARBINARY(20), columnB VARBINARY(20));
2> INSERT INTO test VALUES(CAST('zort' AS VARBINARY(20)), CAST('troz' AS VARBINARY(20)));
3> INSERT INTO test VALUES(CAST('poit' AS VARBINARY(20)), CAST('rubber pants' AS VARBINARY(20)));
4> GO;
```

Finally we can query the table.

```sql
1> SELECT * FROM test;
```

```bash
columnA                                    columnB
------------------------------------------ ------------------------------------------
0x7A6F7274                                 0x74726F7A
0x706F6974                                 0x7275626265722070616E7473

```

Note that what is returned is `BINARY`. If you want the string representation of what is
in the table, you need to convert it.

```sql
1> SELECT CONVERT(VARCHAR(20), columnA) AS columnA,
2>        CONVERT(VARCHAR(20), columnB) AS columnB
3> FROM test;
2> GO;
```

```bash
columnA              columnB
-------------------- --------------------
zort                 troz
poit                 rubber pants
```
