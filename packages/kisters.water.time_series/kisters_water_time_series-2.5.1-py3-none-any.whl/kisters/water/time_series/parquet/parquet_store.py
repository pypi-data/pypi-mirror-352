from __future__ import annotations

from pathlib import Path

from kisters.water.time_series.core import TimeSeriesStore

from .parquet_time_series_client import ParquetTimeSeriesClient


class ParquetStore(TimeSeriesStore):
    """ParquetStore provides a TimeSeriesStore for time series stored in Parquet files.

    Args:
        filename: The path to the Parquet file used for storage.

    Examples:
        .. code-block:: python

            from kisters.water.time_series.parquet import ParquetStore

            ts_store = ParquetStore("test.pq")
            ts = ts_store.get_by_path("validation/inner_consistency1/station1/H")
    """

    def __init__(self, filename: str | Path):
        self._client = ParquetTimeSeriesClient(filename)
