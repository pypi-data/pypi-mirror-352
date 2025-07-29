from __future__ import annotations

import asyncio
import inspect
import time
from asyncio import AbstractEventLoop
from collections.abc import Callable, Coroutine, Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from queue import Queue
from typing import Any, Literal, TypeVar, overload

import pandas as pd

from ..schema import CommentSupport, EnsembleMember, TimeSeriesComment, TimeSeriesKey, TimeSeriesMetadata
from ..time_series import TimeSeries
from .time_series_client import (
    DataFrameTypedDicts,
    SequenceNotStr,
    TimeSeriesClient,
    TimeSeriesMetadataType,
    TSCommentsTypedDicts,
)

T = TypeVar("T")


class Server:
    """
    Here we have a tricky situation, we want more efficiency than in our standard run_sync workarounds,
    if possible, we would like to avoid calling the underlying __aenter__/__aexit__ every time we do
    something. The problem is that the first time __aenter__ gets called in some backends it will call
    async functionality creating objects (Sessions) which are attached to the event loop in the ThreadPool
    of our first pool which gets destroyed if used via the standard asyncio.run.

    This class starts an event loop and starts listening for tasks to complete until the field running
    is set to False. The `serve` method is meant to be run inside a Thread, while in the main Thread you
    submit coroutines and wait for them to finish via the `run` method.
    """

    def __init__(self) -> None:
        self._loop: AbstractEventLoop | None = None
        self._task_queue: Queue[Coroutine[Any, Any, Any]] = Queue()
        self._result_queue: Queue[Any] = Queue()
        self.running = True
        self.finished = False

    def serve(self) -> None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self.main_loop())
        else:
            msg = "There is already an event loop running"
            raise RuntimeError(msg)
        finally:
            if self._loop is not None:
                try:
                    asyncio.runners._cancel_all_tasks(self._loop)  # type: ignore
                    self._loop.run_until_complete(self._loop.shutdown_asyncgens())
                    self._loop.run_until_complete(self._loop.shutdown_default_executor())
                finally:
                    asyncio.set_event_loop(None)
                    self._loop.close()
        self.finished = True

    async def main_loop(self) -> None:
        while self.running:
            task = self._task_queue.get()
            try:
                result = await task
            except Exception as e:
                result = e
            self._result_queue.put(result)

    def run_coroutine(self, coroutine: Coroutine[Any, Any, T]) -> T:
        self._task_queue.put(coroutine)
        result = self._result_queue.get()
        if isinstance(result, Exception):
            raise result from None
        return result  # type: ignore

    @staticmethod
    async def _noop() -> None:
        return None

    def stop(self) -> None:
        self.running = False
        self._task_queue.put(self._noop())


class SynchronousTimeSeriesClient:
    def __init__(self, client: TimeSeriesClient) -> None:
        self._client = client
        self._active_contexts = 0
        self._executor: ThreadPoolExecutor | None = None
        self._server: Server | None = None

    @property
    def comment_support(self) -> CommentSupport:
        return self._client.comment_support

    @property
    def time_series_schema(self) -> type[TimeSeriesMetadata]:
        return self._client.time_series_schema

    def _run_sync(self, coroutine: Callable[..., Coroutine[Any, Any, T]], *args: Any, **kwargs: Any) -> T:
        """
        This method safely calls async methods from a sync context.

        Full details on this method can be found in .time_series_client.py, this is
        just an adaption where we do not keep opening the async context.
        """
        if not inspect.iscoroutinefunction(coroutine):
            msg = f"{coroutine} is not a coroutine"
            raise ValueError(msg)

        return self._server.run_coroutine(coroutine(*args, **kwargs))  # type: ignore

    def __enter__(self) -> SynchronousTimeSeriesClient:
        self._active_contexts += 1
        if self._active_contexts == 1:
            try:
                self._executor = ThreadPoolExecutor(max_workers=1)
                self._executor.__enter__()
                self._server = Server()
                self._executor.submit(self._server.serve)
            except Exception:
                self._active_contexts = 0
                self._executor = None
                self._server = None
                raise
        self._run_sync(self._client.__aenter__)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._server is not None:
            self._run_sync(self._client.__aexit__, exc_type, exc_val, exc_tb)
        self._active_contexts -= 1
        if self._active_contexts == 0 and self._executor is not None and self._server is not None:
            self._server.stop()
            while not self._server.finished:
                time.sleep(0.01)
            self._executor.__exit__(exc_type, exc_val, exc_tb)
            self._executor = None
            self._server = None

    @overload
    def create_time_series(
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
    def create_time_series(
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

    def create_time_series(
        self,
        metadatas: TimeSeriesMetadataType | Iterable[TimeSeriesMetadataType],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> TimeSeries | list[TimeSeries]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(self._client.create_time_series, metadatas, **bulk_kwargs, **kwargs)

    @overload
    def read_time_series(
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
    def read_time_series(
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

    def read_time_series(
        self,
        *,
        paths: str | Iterable[str] | None = None,
        ts_filters: str | Iterable[str] | None = None,
        metadata_keys: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> TimeSeries | list[TimeSeries]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(
            self._client.read_time_series,
            paths=paths,
            ts_filters=ts_filters,
            metadata_keys=metadata_keys,
            **bulk_kwargs,
            **kwargs,
        )

    def update_time_series(
        self,
        metadatas: TimeSeriesMetadataType
        | Iterable[TimeSeriesMetadataType]
        | dict[str, TimeSeriesMetadataType],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(self._client.update_time_series, metadatas, **bulk_kwargs, **kwargs)

    def delete_time_series(
        self,
        paths: str | Iterable[str],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(self._client.delete_time_series, paths, **bulk_kwargs, **kwargs)

    @overload
    def read_coverage(
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
    def read_coverage(
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

    def read_coverage(
        self,
        keys: TimeSeriesKey | str | Iterable[TimeSeriesKey | str],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = (None, None),
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> (
        tuple[datetime | None, datetime | None]
        | dict[TimeSeriesKey, tuple[datetime | None, datetime | None]]
    ):
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(self._client.read_coverage, keys, **bulk_kwargs, **kwargs)

    @overload
    def read_ensemble_members(
        self,
        paths: str,
        *,
        t0_start: datetime | None = None,
        t0_end: datetime | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[EnsembleMember]:
        """"""

    @overload
    def read_ensemble_members(
        self,
        paths: SequenceNotStr[str],
        *,
        t0_start: Iterable[datetime] | datetime | None = None,
        t0_end: Iterable[datetime] | datetime | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> dict[TimeSeriesKey, list[EnsembleMember]]:
        """"""

    def read_ensemble_members(
        self,
        paths: str | Iterable[str],
        *,
        t0_start: Iterable[datetime] | datetime | None = None,
        t0_end: Iterable[datetime] | datetime | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[EnsembleMember] | dict[TimeSeriesKey, list[EnsembleMember]]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(
            self._client.read_ensemble_members,
            paths,
            t0_start=t0_start,
            t0_end=t0_end,
            **bulk_kwargs,
            **kwargs,
        )

    @overload
    def read_data_frame(
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
    def read_data_frame(
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

    def read_data_frame(
        self,
        keys: TimeSeriesKey | str | Iterable[TimeSeriesKey | str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        columns: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> pd.DataFrame | dict[TimeSeriesKey, pd.DataFrame]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(
            self._client.read_data_frame,
            keys,
            start=start,
            end=end,
            columns=columns,
            **bulk_kwargs,
            **kwargs,
        )

    def write_data_frame(
        self,
        data_frames: DataFrameTypedDicts,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(self._client.write_data_frame, data_frames, **bulk_kwargs, **kwargs)

    def delete_data_range(
        self,
        keys: TimeSeriesKey | str | Iterable[TimeSeriesKey | str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(
            self._client.delete_data_range, keys, start=start, end=end, **bulk_kwargs, **kwargs
        )

    @overload
    def read_comments(
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
    def read_comments(
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

    def read_comments(
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
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(
            self._client.read_comments, keys, start=start, end=end, **bulk_kwargs, **kwargs
        )

    def write_comments(
        self,
        comments: TSCommentsTypedDicts,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(self._client.write_comments, comments, **bulk_kwargs, **kwargs)

    def delete_comments(
        self,
        comments: TSCommentsTypedDicts,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        bulk_kwargs = self._client.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        return self._run_sync(self._client.delete_comments, comments, **bulk_kwargs, **kwargs)

    def info(self) -> dict[str, Any]:
        return self._run_sync(self._client.info)
