from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any
from warnings import warn

import pandas as pd
from typing_extensions import deprecated

from .schema import CommentSupport, TimeSeriesKey, TimeSeriesMetadata
from .time_series import TimeSeries
from .time_series_client import OldTimeSeriesClient, SynchronousTimeSeriesClient, TimeSeriesClient
from .utils import make_iterable


class TimeSeriesStore:
    """
    This is the main class to use in order to access time series data via
    its corresponding TimeSeriesClient implementation.
    """

    _client: TimeSeriesClient

    async def __aenter__(self) -> TimeSeriesClient:
        """Enter the async context and get a TimeSeriesClient"""
        await self._client.__aenter__()
        return self._client

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the async context"""
        await self._client.__aexit__(exc_type, exc_val, exc_tb)

    def __enter__(self) -> SynchronousTimeSeriesClient:
        self._sync_client = SynchronousTimeSeriesClient(self._client)
        self._sync_client.__enter__()
        return self._sync_client

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if hasattr(self, "_sync_client") and self._sync_client:
            self._sync_client.__exit__(exc_type, exc_val, exc_tb)

    @property
    @deprecated("Using Store.client is deprecated, switch to the new `async with store as client:`")
    def client(self) -> OldTimeSeriesClient:
        warn(
            "Using Store.client is deprecated, switch to the new `async with store as client:`",
            category=DeprecationWarning,
            stacklevel=4,
        )
        return OldTimeSeriesClient(self._client)

    @property
    def comment_support(self) -> CommentSupport:
        """
        Get information about the comment support of the backend.

        Returns:
            The comment support information.
        """
        return self._client.comment_support

    def get_by_path(
        self,
        *path: str,
        metadata_keys: list[str] | None = None,
        **kwargs: Any,
    ) -> TimeSeries | list[TimeSeries]:
        """
        Get the time series by path.

        Args:
            *path: The full qualified TimeSeries path.
            metadata_keys: list of metadata keys to read.  Set to None to request all metadata.
            **kwargs: The additional keyword arguments which are passed to the backend.

        Returns:
            The TimeSeries object.

        Examples:
            .. code-block:: python

                ts = store.get_by_path("W7AgentTest/20003/S/cmd")
                ts1, ts2 = store.get_by_path("example_path_1", "example_path_2")
        """
        return self._client.run_sync(
            self._client.read_time_series,
            paths=path[0] if len(path) == 1 else path,
            metadata_keys=metadata_keys,
            **kwargs,
        )

    def get_by_filter(
        self,
        *ts_filter: str | None,
        metadata_keys: list[str] | None = None,
        **kwargs: Any,
    ) -> list[TimeSeries]:
        """
        Get time series by filter.

        Args:
            *ts_filter: An iterable of TimeSeries paths or filters.
            metadata_keys: list of metadata keys to read.  Set to None to request all metadata.
            **kwargs: The additional keyword arguments, which are passed to the backend.

        Returns:
            The list of the found TimeSeries objects.

        Examples:
            .. code-block:: python

                store.get_by_filter("W7AgentTest/20004/S/*")
                store.get_by_filter("*Test", "*Ensemble")
        """
        return self._client.run_sync(
            self._client.read_time_series,
            ts_filters=ts_filter,
            metadata_keys=metadata_keys,
            **kwargs,
        )

    def create_time_series(
        self,
        path: str,
        *,
        metadata: dict[str, Any] | TimeSeriesMetadata | None = None,
        **kwargs: Any,
    ) -> TimeSeries:
        """
        Create an empty time series.

        Args:
            path: The time series path.
            metadata: The metadata of the TimeSeries.
            **kwargs: Additional keyword arguments supported by the backend.
        """
        return self._client.run_sync(
            self._client.create_time_series,
            self._client.sanitize_metadata(path=path, metadata=metadata),
            error_handling="raise",
            **kwargs,
        )

    def delete_time_series(self, path: str, **kwargs: Any) -> None:
        """
        Delete a time series.

        Args:
            path: The time series path.
            **kwargs: Additional keyword arguments supported by the backend.

        """
        self._client.run_sync(self._client.delete_time_series, [path], error_handling="raise", **kwargs)

    def read_data_frames(
        self,
        paths: Iterable[TimeSeriesKey | str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        **kwargs: Any,
    ) -> dict[TimeSeriesKey, pd.DataFrame]:
        """
        Read multiple time series as data frames.

        The keyword arguments: 't0', 'dispatch_info' and 'member' are deprecated in favor of
        passing directly TimeSeriesKey objects instead of paths.

        Args:
            paths: An iterable of TimeSeriesKey or time series paths.
            start: An optional iterable of datetimes representing the date from which data will be written,
                if a single datetime is passed it is used for all the TimeSeries.
            end: An optional iterable of datetimes representing the date until (included) which data will be
                written, if a single datetime is passed it is used for all the TimeSeries.
            t0: Deprecated. An optional iterable of datetimes used to select the t0 in an ensemble TimeSeries,
                if a single datetime is passed it is used for all the TimeSeries.
            dispatch_info: Deprecated. An optional iterable of str used to select the dispatch info in an ensemble
                TimeSeries, if a single str is passed it is used for all the TimeSeries.
            member: Deprecated. An optional iterable of str used to select the member in an ensemble TimeSeries,
                if a single str is passed it is used for all the TimeSeries.
            **kwargs: The additional keyword arguments which are passed to the backend.
        """
        if t0 or dispatch_info or member:
            warn(
                "The keyword arguments: 't0', 'dispatch_info' and 'member' are deprecated"
                " in favor of passing directly TimeSeriesKey objects",
                category=DeprecationWarning,
                stacklevel=4,
            )
        keys = [
            k if isinstance(k, TimeSeriesKey) else TimeSeriesKey(path=k, t0=t, dispatch_info=di, member=m)
            for k, t, di, m in zip(
                paths, make_iterable(t0), make_iterable(dispatch_info), make_iterable(member)
            )
        ]
        return self._client.run_sync(self._client.read_data_frame, keys, start=start, end=end, **kwargs)

    def write_data_frames(
        self,
        paths: Iterable[str | TimeSeriesKey] | dict[str | TimeSeriesKey, pd.DataFrame],
        *,
        data_frames: Iterable[tuple[TimeSeriesKey | str, pd.DataFrame]] | None = None,
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Write multiple data frames to time series.

        The keyword arguments: 'data_frames', 't0', 'dispatch_info' and 'member' are deprecated in favor
        of passing directly tuples with TimeSeriesKey and pd.DataFrame objects.

        Args:
            paths: A dictionary with TimeSeriesKey as keys and pd.DataFrame as values.
            data_frames: Deprecated. An iterable of pd.DataFrame objects, that must match to the 'paths'
                argument being an iterable of paths or TimeSeriesKey objects.
            t0: Deprecated. An optional iterable of datetimes used to select the t0 in an ensemble TimeSeries,
                if a single datetime is passed it is used for all the TimeSeries.
            dispatch_info: Deprecated. An optional iterable of str used to select the dispatch info in an ensemble
                TimeSeries, if a single str is passed it is used for all the TimeSeries.
            member: Deprecated. An optional iterable of str used to select the member in an ensemble TimeSeries,
                if a single str is passed it is used for all the TimeSeries.
            **kwargs: The additional keyword arguments which are passed to the backend.

        """
        if data_frames or t0 or dispatch_info or member:
            warn(
                "The keyword arguments: 'data_frames', 't0', 'dispatch_info' and 'member' are deprecated"
                " in favor of passing directly tuples with TimeSeriesKey and pd.DataFrame objects",
                category=DeprecationWarning,
                stacklevel=4,
            )
        if isinstance(paths, dict):
            data_frames = paths  # type: ignore
        else:
            data_frames = {
                p
                if isinstance(p, TimeSeriesKey)
                else TimeSeriesKey(path=p, t0=t, dispatch_info=di, member=m): df  # type: ignore
                for p, df, t, di, m in zip(
                    paths,
                    make_iterable(data_frames),
                    make_iterable(t0),
                    make_iterable(dispatch_info),
                    make_iterable(member),
                )
            }
        self._client.run_sync(self._client.write_data_frame, data_frames, **kwargs)
