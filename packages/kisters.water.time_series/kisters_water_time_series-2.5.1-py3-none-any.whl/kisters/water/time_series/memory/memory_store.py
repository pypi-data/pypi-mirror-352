from __future__ import annotations

from kisters.water.time_series.core import TimeSeriesStore

from .memory_time_series_client import MemoryTimeSeriesClient


class MemoryStore(TimeSeriesStore):
    """MemoryStore provides a TimeSeriesStore for in memory data

    Examples:
        .. code-block:: python
            import numpy as np
            import pandas as pd
            from kisters.water.time_series.memory import MemoryStore

            store = MemoryStore()
            ts = store.create_time_series("my_ts")
            index = pd.date_range(start="2022-01-01", end="2022-02-01", freq="1H", utc=True)
            ts.write_data_frame(pd.DataFrame({"value": np.arange(index.shape[0])}, index=index)
    """

    def __init__(self) -> None:
        self._client = MemoryTimeSeriesClient()
