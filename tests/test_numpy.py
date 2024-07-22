import string

import hypothesis.strategies as st
import npyodbc
import numpy as np
import pytest
from hypothesis import given, settings
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


@pytest.mark.sqlite()
def test_cursor_fetchdictarray_method_exists():
    """Test that npyodbc.Cursor.fetchdictarray exists."""
    assert hasattr(npyodbc.Cursor, 'fetchdictarray')


@pytest.mark.sqlite()
@settings(deadline=500)
@given(
    st.lists(
        st.tuples(
            st.text(alphabet=string.printable, max_size=10),
            st.integers(min_value=-(2**32)//2, max_value=(2**32)//2 - 1),
            st.floats(allow_nan=False, allow_infinity=False, min_value=-1.79e308, max_value=1.79e308),
        ),
        min_size=1,
        max_size=100,
    )
)
def test_fetchdictarray(cursor, values):
    """Test that fetchdictarray returns the expected values from the database.

    - Text is restricted to printable characters because that's tested separately.
    - Integers are restricted to the 64-bit range (-2**63, 2**63 - 1) because otherwise
      the values get wrapped in the database.
    - Floats are restricted to non-nan, non-inf values between (-1.79e308, 1.79e308),
      which is the range covered by a double precision (64-bit) float. If you try to
      store values larger than this in a REAL column, it gets converted to +/- inf.
    """
    cursor.execute('DROP TABLE IF EXISTS t1;')

    cursor.execute('CREATE TABLE t1(a text, b int, c real);')

    for value in values:
        cursor.execute('INSERT INTO t1 values(?,?,?);', *value)

    inserted = cursor.execute('SELECT * from t1;').fetchdictarray()
    expected = {col[0]: np.array(arr) for col, arr in zip(cursor.description, zip(*values))}
    for key, value in expected.items():
        assert_result_close(inserted[key], value)

    cleanup(cursor)


@pytest.mark.sqlite()
@pytest.mark.skip(reason="FDA doesn't handle unicode currently")
def test_fetchdictarray_unicode(cursor):
    """Test that fetchdictarray correctly handles unicode strings."""
    cursor.execute('DROP TABLE IF EXISTS t1;')

    cursor.execute('CREATE TABLE t1(a text, b int);')
    cursor.execute('INSERT INTO t1 values(?,?);', '𐀀', 0)

    inserted = cursor.execute('SELECT * from t1;').fetchdictarray()
    expected = {'a': np.array(['𐀀']), 'b': np.array([0])}

    for key, value in expected.items():
        assert_allclose(inserted[key], value)

    cleanup(cursor)
