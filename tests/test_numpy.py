import binascii
import re
import string
import warnings

import hypothesis.strategies as st
import npyodbc
import numpy as np
import pytest
from hypothesis import given, reject, settings
from numpy.testing import assert_allclose, assert_array_equal


@pytest.fixture(scope="module")
def connection() -> npyodbc.Connection:
    """Return a connection for a SQLite3 database."""
    return npyodbc.connect("Driver=SQLite3;Database=:memory:;Charset=UTF8")


@pytest.fixture(scope="module")
def cursor(connection) -> npyodbc.Cursor:
    """Return a cursor for a SQLite3 database."""
    return connection.cursor()


def cleanup(cursor: npyodbc.Cursor):
    """Drop all tables from the database.

    Use this function to clean up the database at the end of each test rather
    than a fixture because hypothesis doesn't work with test-scoped fixtures.

    Parameters
    ----------
    cursor : npyodbc.Cursor
        Cursor for the database to clean up
    """
    for table in cursor.execute('SELECT tbl_name FROM sqlite_schema;').fetchall():
        cursor.execute(f'DROP TABLE {table[0]};')
    assert len(cursor.execute('SELECT tbl_name FROM sqlite_schema;').fetchall()) == 0


def assert_result_close(a: np.ndarray, b: np.ndarray):
    """Assert that a is close to b.

    If a is a float dtype, use assert_allclose; otherwise we check for exact equality.

    Parameters
    ----------
    a : np.ndarray
        An array to check
    b : np.ndarray
        An array to check
    """
    if a.dtype.kind == np.dtype(float).kind:
        assert_allclose(a, b)
    else:
        assert_array_equal(a, b)


@pytest.mark.sqlite
def test_cursor_fetchdictarray_method_exists():
    """Test that npyodbc.Cursor.fetchdictarray exists."""
    assert hasattr(npyodbc.Cursor, 'fetchdictarray')


@pytest.mark.sqlite
@settings(deadline=None)
@given(
    st.lists(
        st.tuples(
            st.text(alphabet=string.printable, max_size=10),
            st.integers(min_value=-(2**16)//2, max_value=(2**16)//2 - 1),
            st.floats(allow_nan=False, allow_infinity=False, min_value=-1.79e308, max_value=1.79e308),
        ),
        min_size=1,
        max_size=100,
    )
)
@pytest.mark.parametrize(
    ("target_dtypes"),
    [
        {'a': 'U', 'b': 'i8', 'c': 'f8'},
        {},
    ]
)
def test_fetchdictarray(cursor, target_dtypes, values):
    """Test that fetchdictarray returns the expected values from the database.

    - Text is restricted to printable characters because that's tested separately.
    - Integers are restricted to the 32-bit range (-2**31, 2**31 - 1) because otherwise
      the values get wrapped in the database.
    - Floats are restricted to non-nan, non-inf values between (-1.79e308, 1.79e308),
      which is the range covered by a double precision (64-bit) float. If you try to
      store values larger than this in a REAL column, it gets converted to +/- inf.
    """
    cursor.execute('DROP TABLE IF EXISTS t1;')
    cursor.execute('CREATE TABLE t1(a text, b int, c real);')

    for value in values:
        cursor.execute('INSERT INTO t1 values(?,?,?);', *value)

    inserted = cursor.execute('SELECT * from t1;').fetchdictarray(
        target_dtypes=target_dtypes
    )

    expected = {col[0]: np.array(arr) for col, arr in zip(cursor.description, zip(*values))}
    for key, value in expected.items():
        assert_result_close(inserted[key], value)

    cleanup(cursor)


@pytest.mark.sqlite
@pytest.mark.parametrize(
    ("target_dtypes"),
    [
        {'a': 'U', 'b': 'i8', 'c': 'f8'},
        {},
    ]
)
def test_fetchdictarray_unicode(cursor, target_dtypes):
    """Test that fetchdictarray correctly a specific unicode string test case."""
    cursor.execute('DROP TABLE IF EXISTS t1;')
    cursor.execute('CREATE TABLE t1(a text, b int);')
    cursor.execute('INSERT INTO t1 values(?,?);', '𐀀', 0)

    inserted = cursor.execute('SELECT * from t1;').fetchdictarray(
        target_dtypes=target_dtypes
    )
    expected = {'a': np.array(['𐀀']), 'b': np.array([0])}

    for key, value in expected.items():
        assert_array_equal(inserted[key], value)

    cleanup(cursor)


@pytest.mark.sqlite
@settings(deadline=None)
@given(
    st.lists(
        st.tuples(
            st.text(max_size=30).filter(lambda x: x != '\U0010d800'),
            st.integers(min_value=-(2**32)//2, max_value=(2**32)//2 - 1),
        ),
        min_size=1,
        max_size=100,
    ),
)
@pytest.mark.parametrize(
    ("target_dtypes"),
    [
        {'a': 'U', 'b': 'i8'},
        {},
    ]
)
def test_fetchdictarray_unicode_values(cursor, target_dtypes, values):
    """Test that fetchdictarray correctly handles arrays of unicode strings."""
    cursor.execute('DROP TABLE IF EXISTS t1;')
    cursor.execute('CREATE TABLE t1(a text, b int);')

    for text, val in values:
        cursor.execute('INSERT INTO t1 values(?,?);', text, val)

    cursor.execute('SELECT * from t1;')
    inserted = cursor.fetchdictarray(target_dtypes=target_dtypes)

    try:
        cursor.execute('SELECT * from t1;')
        expected_text, expected_ints = zip(*cursor.fetchall())
    except UnicodeDecodeError:
        warnings.warn(
            "Pyodbc itself failed to decode UTF16, but npyodbc did not.\n"
            f"values: {values}",
            stacklevel=1,
        )
        reject()

    expected = {
        'a': np.array(expected_text),
        'b': np.array(expected_ints),
    }

    for key, value in expected.items():
        assert_array_equal(inserted[key], value)

    cleanup(cursor)


@pytest.mark.sqlite
@pytest.mark.parametrize(
    ('sql_type'),
    [
        ('BINARY'),
        ('VARBINARY'),
        ('LONGVARBINARY'),
    ]
)
def test_fetchdictarray_binary(cursor, sql_type):
    """Test that fetchdictarray can retrieve binary, varbinary, and longvarbinary columns."""
    binary = [
        b"foo",
        b"bar",
        b"baz",
        b"quux",
    ]
    ints = [1, 2, 3, 4]

    # Need to specify max element size for binary/varbinary/longvarbinary col. Since this is
    # sqlite, blobs are stored in hexadecimal format, so the length of the stored data is
    # not the same as the length of the bytestrings above. Let's just make it 16 bytes, which
    # is enough to hold the 4 characters in the largest bytestring, plus the extra three
    # added by sqlite, as explained below.
    elsize = 16
    cursor.execute('DROP TABLE IF EXISTS t1;')
    cursor.execute(f'CREATE TABLE t1(a {sql_type}({elsize}), b int);')

    for bval, ival in zip(binary, ints):
        cursor.execute('INSERT INTO t1 values(?,?);', bval, ival)

    cursor.execute('SELECT * from t1;')

    # Cast column 'a' to a null-terminated bytes dtype
    fda_result = cursor.fetchdictarray(target_dtypes={'a': "S", 'b': 'i8'})

    # Convert the array element to bytes. In sqlite, data is stored in hexadecimal format,
    # e.g. b'foo' -> 666F6F. Additionally it gets enclosed with an X'<value>' to signify that
    # the data is in hexadecimal format, and since we requested 16-element binary columns,
    # the hex representation also gets padded out with a bunch of null bytes to fill
    # any extra space:
    # | Python     |   hex representation    |   sqlite database entry   |
    # | b'foo'     |   666F6F                |   "X'666F6F'\x00"         |
    for bval, fda_val in zip(binary, fda_result['a']):
        match = re.match(b"X'(?P<hexval>([0-9A-F]{2})+)'(\x00)*?", fda_val.tobytes())
        if match:
            assert binascii.unhexlify(match.group('hexval')) == bval
        else:
            pytest.fail("Failed to extract hexadecimal bytestring from sqlite BLOB data.")

    cleanup(cursor)


@pytest.mark.sqlite
@pytest.mark.parametrize(
    ('sql_type'),
    [
        ('BINARY'),
        ('VARBINARY'),
        ('LONGVARBINARY'),
    ]
)
@pytest.mark.parametrize(
    ('dtype'),
    [
        '?', # boolean
        'i32', # (signed) integer
        'u16', # unsigned integer
        'f32', # floating-point
        'c64', # complex-floating point
        'm', # timedelta
        'M', # datetime
        'O', # (Python) objects
        'V', # raw data (void)
    ]
)
def test_fetchdictarray_binary_bad_type_coercion(cursor, sql_type, dtype):
    """Test that fetchdictarray fails when coercing binary data to nonsensical types."""
    binary = [
        b"foo",
        b"bar",
        b"baz",
        b"quux",
    ]
    ints = [1, 2, 3, 4]

    # Need to specify max element size for binary/varbinary/longvarbinary col. Since this is
    # sqlite, blobs are stored in hexadecimal format, so the length of the stored data is
    # not the same as the length of the bytestrings above. Let's just make it 16 bytes, which
    # is enough to hold the 4 characters in the largest bytestring, plus the extra three
    # added by sqlite, as explained below.
    elsize = 16
    cursor.execute('DROP TABLE IF EXISTS t1;')
    cursor.execute(f'CREATE TABLE t1(a {sql_type}({elsize}), b int);')

    for bval, ival in zip(binary, ints):
        cursor.execute('INSERT INTO t1 values(?,?);', bval, ival)

    cursor.execute('SELECT * from t1;')

    # Cast column 'a' to the requested dtype
    with pytest.raises((SystemError, TypeError)):
        cursor.fetchdictarray(target_dtypes={'a': dtype, 'b': 'i8'})

    cleanup(cursor)
