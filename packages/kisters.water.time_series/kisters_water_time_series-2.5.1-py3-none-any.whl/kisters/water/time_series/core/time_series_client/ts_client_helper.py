from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Iterable, Sequence
from datetime import datetime
from typing import Any, Literal, overload
from warnings import warn

import pandas as pd

from .. import TimeSeriesUserError
from ..schema import CommentSupport, EnsembleMember, TimeSeriesComment, TimeSeriesKey, TimeSeriesMetadata
from ..time_series import TimeSeries
from ..utils import make_iterable, model_dump
from .time_series_client import (
    DataFrameTypedDicts,
    SequenceNotStr,
    TimeSeriesClient,
    TimeSeriesMetadataType,
    TSCommentsTypedDicts,
)


class TimeSeriesClientHelper(TimeSeriesClient):
    """
    This class implements the TimeSeriesClient but has a generic bulk
    implementation abusing the bulk_concurrent method. For this case

    This solely exist to ease up transitioning into the new API
    for already existing clients, they only need to rename the
    existing single access method with a prefixed underscore and
    inherit from this class instead of the standard TimeSeriesClient.
    """

    @abstractmethod
    async def _create_time_series(self, metadata: TimeSeriesMetadata, **kwargs: Any) -> TimeSeries:
        """"""

    @abstractmethod
    async def _read_time_series(
        self, path: str, *, metadata_keys: list[str] | None = None, **kwargs: Any
    ) -> TimeSeries:
        """"""

    @abstractmethod
    async def _filter_time_series(
        self, ts_filter: str, *, metadata_keys: list[str] | None = None, **kwargs: Any
    ) -> list[TimeSeries]:
        """"""

    @abstractmethod
    async def _update_time_series(self, metadata: TimeSeriesMetadata, **kwargs: Any) -> None:
        """"""

    @abstractmethod
    async def _delete_time_series(self, path: str, **kwargs: Any) -> None:
        """"""

    @abstractmethod
    async def _read_coverage(
        self,
        path: str,
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> tuple[datetime | None, datetime | None]:
        """"""

    @abstractmethod
    async def _read_ensemble_members(
        self,
        path: str,
        *,
        t0_start: datetime | None = None,
        t0_end: datetime | None = None,
        **kwargs: Any,
    ) -> list[EnsembleMember]:
        """"""

    @abstractmethod
    async def _read_data_frame(
        self,
        path: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        columns: list[str] | None = None,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """"""

    @abstractmethod
    async def _write_data_frame(
        self,
        path: str,
        *,
        data_frame: pd.DataFrame,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        """"""

    @abstractmethod
    async def _delete_data_range(
        self,
        path: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        """"""

    async def _read_comments(
        self,
        path: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> list[TimeSeriesComment]:
        raise NotImplementedError

    async def _write_comments(
        self,
        path: str,
        *,
        comments: list[TimeSeriesComment],
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError

    async def _delete_comments(
        self,
        path: str,
        comments: list[TimeSeriesComment],
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError

    @overload
    async def create_time_series(
        self,
        metadatas: TimeSeriesMetadataType,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> TimeSeries:
        """"""

    @overload
    async def create_time_series(
        self,
        metadatas: Iterable[TimeSeriesMetadataType],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[TimeSeries]:
        """"""

    async def create_time_series(
        self,
        metadatas: TimeSeriesMetadataType | Iterable[TimeSeriesMetadataType],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> TimeSeries | list[TimeSeries]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(metadatas, (TimeSeries, TimeSeriesMetadata, dict)):
            metadata = self.sanitize_metadata(metadata=metadatas)
            return await self._create_time_series(metadata=metadata)

        results = await self._bulk_concurrent(
            awaitables=[
                self._create_time_series(metadata, **kwargs)
                for metadata in [self.sanitize_metadata(metadata=m) for m in metadatas]
            ],
            **bulk_kwargs,
        )
        errors = []
        filtered_results = []
        for result in results:
            if isinstance(result, Exception):
                errors.append(result)
            else:
                filtered_results.append(result)
        if errors:
            warn(f"Encountered {len(errors)} errors while creating time series: {errors}", stacklevel=4)
        return filtered_results

    @overload
    async def read_time_series(
        self,
        *,
        paths: str,
        ts_filters: None = None,
        metadata_keys: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> TimeSeries:
        """"""

    @overload
    async def read_time_series(
        self,
        *,
        paths: SequenceNotStr[str] | None = None,
        ts_filters: Iterable[str] | None = None,
        metadata_keys: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[TimeSeries]:
        """"""

    async def read_time_series(
        self,
        *,
        paths: str | Iterable[str] | None = None,
        ts_filters: str | Iterable[str] | None = None,
        metadata_keys: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> TimeSeries | list[TimeSeries]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(paths, str) and not ts_filters:
            return await self._read_time_series(paths, metadata_keys=metadata_keys, **kwargs)

        errors = []
        results = []
        if paths:
            for ts in await self._bulk_concurrent(
                awaitables=[self._read_time_series(path=path, **kwargs) for path in paths],
                **bulk_kwargs,
            ):
                if isinstance(ts, Exception):
                    errors.append(ts)
                else:
                    results.append(ts)
        if ts_filters:
            ts_filters = [ts_filters] if isinstance(ts_filters, str) else ts_filters
            for ts_list in await self._bulk_concurrent(
                awaitables=[
                    self._filter_time_series(ts_filter=ts_filter, metadata_keys=metadata_keys, **kwargs)
                    for ts_filter in ts_filters
                ],
                **bulk_kwargs,
            ):
                if isinstance(ts_list, Exception):
                    errors.append(ts_list)
                else:
                    results += ts_list
        if errors:
            warn(f"Encountered {len(errors)} errors while reading time series: {errors}", stacklevel=4)
        return results

    async def update_time_series(
        self,
        metadatas: TimeSeriesMetadataType
        | Iterable[TimeSeriesMetadataType]
        | dict[str, TimeSeriesMetadataType],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(metadatas, (TimeSeries, TimeSeriesMetadata, dict)):
            await self._update_time_series(self.sanitize_metadata(metadata=metadatas), **kwargs)
            return None

        errors = [
            r
            for r in await self._bulk_concurrent(
                awaitables=[
                    self._update_time_series(metadata=metadata, **kwargs)
                    for metadata in [self.sanitize_metadata(metadata=m) for m in metadatas]
                ],
                **bulk_kwargs,
            )
            if isinstance(r, Exception)
        ]
        if errors:
            warn(f"Encountered {len(errors)} errors while updating time series: {errors}", stacklevel=4)
        return errors

    async def delete_time_series(
        self,
        paths: str | Iterable[str],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        if isinstance(paths, str):
            await self._delete_time_series(paths, **kwargs)
            return None

        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        errors = [
            r
            for r in await self._bulk_concurrent(
                awaitables=[self._delete_time_series(path=path, **kwargs) for path in paths],
                **bulk_kwargs,
            )
            if isinstance(r, Exception)
        ]
        if errors:
            warn(f"Encountered {len(errors)} errors while deleting time series: {errors}", stacklevel=4)
        return errors

    @overload
    async def read_coverage(
        self,
        keys: TimeSeriesKey | str,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = (None, None),
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> tuple[datetime | None, datetime | None]:
        """"""

    @overload
    async def read_coverage(
        self,
        keys: SequenceNotStr[TimeSeriesKey | str],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = (None, None),
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> dict[TimeSeriesKey, tuple[datetime | None, datetime | None]]:
        """"""

    async def read_coverage(
        self,
        keys: TimeSeriesKey | str | Iterable[TimeSeriesKey | str],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = (None, None),
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> (
        tuple[datetime | None, datetime | None]
        | dict[TimeSeriesKey, tuple[datetime | None, datetime | None]]
    ):
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(keys, (TimeSeriesKey, str)):
            key = keys if isinstance(keys, TimeSeriesKey) else TimeSeriesKey(path=keys)
            return await self._read_coverage(**model_dump(key), **kwargs)

        ts_keys = [key if isinstance(key, TimeSeriesKey) else TimeSeriesKey(path=key) for key in keys]
        results = {}
        errors = []
        for key, coverage in zip(
            ts_keys,
            await self._bulk_concurrent(
                awaitables=[self._read_coverage(**model_dump(key), **kwargs) for key in ts_keys],
                **bulk_kwargs,
            ),
        ):
            if isinstance(coverage, Exception):
                errors.append(coverage)
            else:
                results[key] = coverage
        if errors:
            warn(f"Encountered {len(errors)} errors while reading coverages: {errors}", stacklevel=4)
        return results

    @overload
    async def read_ensemble_members(
        self,
        paths: str,
        *,
        t0_start: Iterable[datetime | None] | datetime | None = None,
        t0_end: Iterable[datetime | None] | datetime | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[EnsembleMember]:
        """"""

    @overload
    async def read_ensemble_members(
        self,
        paths: SequenceNotStr[str],
        *,
        t0_start: Iterable[datetime | None] | datetime | None = None,
        t0_end: Iterable[datetime | None] | datetime | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> dict[TimeSeriesKey, list[EnsembleMember]]:
        """"""

    async def read_ensemble_members(
        self,
        paths: str | Iterable[str],
        *,
        t0_start: Iterable[datetime | None] | datetime | None = None,
        t0_end: Iterable[datetime | None] | datetime | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[EnsembleMember] | dict[TimeSeriesKey, list[EnsembleMember]]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(paths, str):
            if (t0_start is None or isinstance(t0_start, datetime)) and (
                t0_end is None or isinstance(t0_end, datetime)
            ):
                return await self._read_ensemble_members(paths, t0_start=t0_start, t0_end=t0_end, **kwargs)
            msg = "When providing a single path, t0_start and t0_end cannot be iterables"
            raise TimeSeriesUserError(msg, paths)

        errors = []
        results: dict[TimeSeriesKey, list[EnsembleMember]] = {}
        for key, ensemble_list in zip(
            [TimeSeriesKey(path=path) for path in paths],
            await self._bulk_concurrent(
                awaitables=[
                    self._read_ensemble_members(path=path, t0_start=t0_start_i, t0_end=t0_end_i, **kwargs)
                    for path, t0_start_i, t0_end_i in zip(
                        paths, make_iterable(t0_start), make_iterable(t0_end)
                    )
                ],
                **bulk_kwargs,
            ),
        ):
            if isinstance(ensemble_list, Exception):
                errors.append(ensemble_list)
            else:
                results[key] = ensemble_list

        if errors:
            warn(f"Encountered {len(errors)} errors while reading ensembles: {errors}", stacklevel=4)
        return results

    @overload
    async def read_data_frame(
        self,
        keys: TimeSeriesKey | str,
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        columns: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = lambda: pd.DataFrame(
            index=pd.DatetimeIndex([], dtype="datetime64[ms, UTC]")
        ),
        **kwargs: Any,
    ) -> pd.DataFrame:
        """"""

    @overload
    async def read_data_frame(
        self,
        keys: SequenceNotStr[TimeSeriesKey | str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        columns: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = lambda: pd.DataFrame(
            index=pd.DatetimeIndex([], dtype="datetime64[ms, UTC]")
        ),
        **kwargs: Any,
    ) -> dict[TimeSeriesKey, pd.DataFrame]:
        """"""

    async def read_data_frame(
        self,
        keys: TimeSeriesKey | str | Iterable[TimeSeriesKey | str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        columns: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = lambda: pd.DataFrame(
            index=pd.DatetimeIndex([], dtype="datetime64[ms, UTC]")
        ),
        **kwargs: Any,
    ) -> pd.DataFrame | dict[TimeSeriesKey, pd.DataFrame]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(keys, (TimeSeriesKey, str)):
            key = keys if isinstance(keys, TimeSeriesKey) else TimeSeriesKey(path=keys)
            if (start is None or isinstance(start, datetime)) and (
                end is None or isinstance(end, datetime)
            ):
                return await self._read_data_frame(
                    **model_dump(key), start=start, end=end, columns=columns, **kwargs
                )
            msg = "When providing a single time series key or path, start and end cannot be iterables"
            raise TimeSeriesUserError(msg, key)

        ts_keys = [TimeSeriesKey(path=key) if isinstance(key, str) else key for key in keys]
        dfs = await self._bulk_concurrent(
            awaitables=[
                self._read_data_frame(
                    path=key.path,
                    start=start_i,
                    end=end_i,
                    t0=key.t0,
                    dispatch_info=key.dispatch_info,
                    member=key.member,
                    columns=columns,
                    **kwargs,
                )
                for key, start_i, end_i in zip(ts_keys, make_iterable(start), make_iterable(end))
            ],
            **bulk_kwargs,
        )
        errors = []
        results = {}
        for key, df in zip(ts_keys, dfs):
            if isinstance(df, Exception):
                errors.append(df)
            else:
                results[key] = df
        if errors:
            warn(f"Encountered {len(errors)} errors while reading data frames: {errors}", stacklevel=4)
        return results

    async def write_data_frame(
        self,
        data_frames: DataFrameTypedDicts,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "raise",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        errors = [
            r
            for r in await self._bulk_concurrent(
                awaitables=[
                    self._write_data_frame(
                        **{"path": key} if isinstance(key, str) else model_dump(key),
                        data_frame=df,
                        **kwargs,
                    )
                    for key, df in data_frames.items()
                ],
                **bulk_kwargs,
            )
            if isinstance(r, Exception)
        ]
        if errors:
            warn(f"Encountered {len(errors)} errors while writing data frames: {errors}", stacklevel=4)
        return errors

    async def delete_data_range(
        self,
        keys: TimeSeriesKey | str | Iterable[TimeSeriesKey | str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(keys, (TimeSeriesKey, str)):
            key = keys if isinstance(keys, TimeSeriesKey) else TimeSeriesKey(path=keys)
            if (start is None or isinstance(start, datetime)) and (
                end is None or isinstance(end, datetime)
            ):
                await self._delete_data_range(**model_dump(key), start=start, end=end, **kwargs)
                return None
            msg = "When providing a single time series key or path, start and end cannot be iterables"
            raise TimeSeriesUserError(msg, key)

        errors = [
            r
            for r in await self._bulk_concurrent(
                awaitables=[
                    self._delete_data_range(
                        **{"path": key} if isinstance(key, str) else model_dump(key),
                        start=start_i,
                        end=end_i,
                        **kwargs,
                    )
                    for key, start_i, end_i in zip(keys, make_iterable(start), make_iterable(end))
                ],
                **bulk_kwargs,
            )
            if isinstance(r, Exception)
        ]
        if errors:
            warn(f"Encountered {len(errors)} errors while writing data frames: {errors}", stacklevel=4)
        return errors

    @overload
    async def read_comments(
        self,
        keys: TimeSeriesKey | str,
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[TimeSeriesComment]:
        """"""

    @overload
    async def read_comments(
        self,
        keys: SequenceNotStr[TimeSeriesKey | str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> dict[TimeSeriesKey, list[TimeSeriesComment]]:
        """"""

    async def read_comments(
        self,
        keys: TimeSeriesKey | str | Iterable[TimeSeriesKey | str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[TimeSeriesComment] | dict[TimeSeriesKey, list[TimeSeriesComment]]:
        """
        Read time series comments in bulk

        Args:
            keys: An iterable of time series keys or paths.
            start: An optional iterable of datetimes representing the date from which data will be written,
                if a single datetime is passed it is used for all the TimeSeries.
            end: An optional iterable of datetimes representing the date until (included) which data will be
                written, if a single datetime is passed it is used for all the TimeSeries.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.

        Returns:
            A list per each path with a list of comments.
        """
        if CommentSupport.READ not in self.comment_support:
            raise NotImplementedError
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(keys, (TimeSeriesKey, str)):
            key = keys if isinstance(keys, TimeSeriesKey) else TimeSeriesKey(path=keys)
            if (start is None or isinstance(start, datetime)) and (
                end is None or isinstance(end, datetime)
            ):
                return await self._read_comments(**model_dump(key), start=start, end=end, **kwargs)
            msg = "When providing a single time series key or path, start and end cannot be iterables"
            raise TimeSeriesUserError(msg, key)

        ts_keys = [TimeSeriesKey(path=key) if isinstance(key, str) else key for key in keys]
        errors = []
        results = {}
        for key, comments in zip(
            ts_keys,
            await self._bulk_concurrent(
                awaitables=[
                    self._read_comments(
                        **model_dump(k),
                        start=start_i,
                        end=end_i,
                        **kwargs,
                    )
                    for k, start_i, end_i in zip(
                        ts_keys,
                        make_iterable(start),
                        make_iterable(end),
                    )
                ],
                **bulk_kwargs,
            ),
        ):
            if isinstance(comments, Exception):
                errors.append(comments)
            else:
                results[key] = comments

        if errors:
            warn(f"Encountered {len(errors)} errors while reading comments: {errors}", stacklevel=4)
        return results

    async def write_comments(
        self,
        comments: TSCommentsTypedDicts,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        """
        Write time series comments in bulk

        Args:
            keys: An iterable of time series keys or paths.
            comments: A list containing a list of comment per each time series path.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.
        """
        if CommentSupport.WRITE not in self.comment_support:
            raise NotImplementedError
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return [
            r
            for r in await self._bulk_concurrent(
                awaitables=[
                    self._write_comments(
                        **{"path": key} if isinstance(key, str) else model_dump(key),
                        comments=comments_i,
                        **kwargs,
                    )
                    for key, comments_i in comments.items()
                ],
                **bulk_kwargs,
            )
            if isinstance(r, Exception)
        ]

    async def delete_comments(
        self,
        comments: TSCommentsTypedDicts,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        """
        Delete time series comments in bulk

        Args:
            comments: An iterable of tuples with time series keys or paths and comments.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.
        """
        if CommentSupport.DELETE not in self.comment_support:
            raise NotImplementedError
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return [
            r
            for r in await self._bulk_concurrent(
                awaitables=[
                    self._delete_comments(
                        **{"path": key} if isinstance(key, str) else model_dump(key),
                        comments=comments_i,
                        **kwargs,
                    )
                    for key, comments_i in comments.items()
                ],
                **bulk_kwargs,
            )
            if isinstance(r, Exception)
        ]
