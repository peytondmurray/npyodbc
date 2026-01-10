from numpy.typing import DTypeLike, NDArray

from ._npyodbc import *  # noqa: F403

class Cursor:
    def fetchdictarray(
        self,
        size: int = -1,
        null_suffix: str | None = None,
        target_dtypes: dict[str, DTypeLike] | None = None,
    ) -> dict[str, NDArray]:
        """Fetch a dictionary mapping SQL column names to numpy arrays.

        Fetch as many rows as specified by size into a dictionary of NumPy
        ndarrays (dictarray). The dictionary will contain a key for each column,
        with its value being a NumPy ndarray holding its value for the fetched
        rows. Optionally, extra columns will be added to signal nulls on
        nullable columns.

        Parameters
        ----------
        size : int
            The number of rows to fetch. Use -1 (the default) to fetch all
            remaining rows.
        null_suffix : Optional[str]
            If specified, a new boolean column named `<column_name><null_suffix>` will be
            included in the output, with values indicating which values in `<column_name>` were
            null in the original array. If None, no such column will be included.
        target_dtypes : Optional[dict[str, numpy.typing.DTypeLike]]
            If provided, this mapping between {column name: dtype} coerces
            the values read from the database into arrays of the requested
            dtypes.

        Returns
        -------
        dict[str, numpy.typing.NDArray]
            A dictionary mapping column names to an ndarray holding its values
            for the fetched rows. The dictionary will use the column name as
            key for the ndarray containing values associated to that column.
            Optionally, null information for nullable columns will be provided
            by adding additional boolean columns named after the nullable column
            concatenated to null_suffix

        Notes
        -----
        Similar to fetchmany(size), but returning a dictionary of NumPy ndarrays
        for the results instead of a Python list of tuples of objects, reducing
        memory footprint as well as improving performance.
        fetchdictarray is overall more efficient that fetchsarray.

        See Also
        --------
        fetchmany : Fetch rows into a Python list of rows.
        fetchall : Fetch the remaining rows into a Python list of rows.
        """
