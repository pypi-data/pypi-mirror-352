from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncIterator, Awaitable, Callable, Coroutine, Iterable, Iterator, Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Literal, TypeVar

import pandas as pd

from ..schema import CommentSupport, EnsembleMember, TimeSeriesComment, TimeSeriesKey, TimeSeriesMetadata
from ..time_series import TimeSeries
from ..utils import make_iterable
from .time_series_client import TimeSeriesClient

T = TypeVar("T")


class OldTimeSeriesClient:
    def __init__(self, client: TimeSeriesClient):
        self.client = client

    @property
    def comment_support(self) -> CommentSupport:
        return self.client.comment_support

    @property
    def time_series_schema(self) -> type[TimeSeriesMetadata]:
        return self.client.time_series_schema

    def sanitize_metadata(
        self,
        *,
        path: str | None = None,
        metadata: dict[str, Any] | TimeSeriesMetadata | None = None,
    ) -> TimeSeriesMetadata:
        return self.client.sanitize_metadata(path=path, metadata=metadata)

    async def __aenter__(self) -> OldTimeSeriesClient:
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    def run_sync(self, coroutine: Callable[..., Coroutine[Any, Any, T]], *args: Any, **kwargs: Any) -> T:
        return self.client.run_sync(coroutine=coroutine, *args, **kwargs)  # type: ignore # noqa: B026

    def iter_over_async(
        self, coroutine: Callable[..., AsyncIterator[T]], *args: Any, **kwargs: Any
    ) -> Iterator[T]:
        """
        This method safely calls an async iterator from a sync context.

        It mostly follows the same strategy as the run_sync method, adapted to handle
        the async iterator use case. Still not sure why we do this to ourselves.
        """
        if not inspect.isasyncgenfunction(coroutine):
            msg = f"{coroutine} is not an async generator"
            raise ValueError(msg)

        ait = coroutine(*args, **kwargs)

        external_loop = asyncio.new_event_loop()

        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(asyncio.set_event_loop, external_loop).result()
            external_loop_future = executor.submit(external_loop.run_forever)
            try:
                asyncio.run_coroutine_threadsafe(self.__aenter__(), external_loop).result()
                try:
                    while True:
                        next_obj_future = asyncio.run_coroutine_threadsafe(ait.__anext__(), external_loop)
                        try:
                            next_obj: T = next_obj_future.result()
                        except StopAsyncIteration:
                            break
                        else:
                            yield next_obj
                finally:
                    asyncio.run_coroutine_threadsafe(
                        self.__aexit__(None, None, None), external_loop
                    ).result()
            finally:
                external_loop.call_soon_threadsafe(external_loop.stop)
            external_loop_future.result()

    async def _bulk_concurrent(
        self,
        awaitables: list[Awaitable[Any]],
        concurrency_limit: int = 32,
        error_handling: Literal["default", "return", "raise"] = "default",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
    ) -> list[Any]:
        return await self.client._bulk_concurrent(
            awaitables=awaitables,
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
        )

    async def create_time_series(
        self,
        path: str,
        *,
        metadata: dict[str, Any] | TimeSeriesMetadata | None = None,
        **kwargs: Any,
    ) -> TimeSeries:
        metadata = self.sanitize_metadata(path=path, metadata=metadata)
        return await self.client.create_time_series(metadatas=metadata, error_handling="raise", **kwargs)

    async def create_time_series_bulk(
        self,
        paths: list[str],
        *,
        metadatas: list[dict[str, Any] | TimeSeriesMetadata | None],
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[TimeSeries]:
        return await self.client.create_time_series(
            metadatas=[self.sanitize_metadata(path=p, metadata=m) for p, m in zip(paths, metadatas)],
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
            **kwargs,
        )

    async def read_time_series(
        self, path: str, *, metadata_keys: list[str] | None = None, **kwargs: Any
    ) -> TimeSeries:
        return await self.client.read_time_series(
            paths=path,
            metadata_keys=metadata_keys,
            error_handling="raise",
            **kwargs,
        )

    async def filter_time_series(
        self,
        ts_filter: str | None,
        *,
        metadata_keys: list[str] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[TimeSeries]:
        for ts in await self.client.read_time_series(
            ts_filters=[ts_filter] if ts_filter else None, metadata_keys=metadata_keys, **kwargs
        ):
            yield ts

    async def read_time_series_bulk(
        self,
        *,
        paths: list[str] | None = None,
        ts_filters: list[str] | None = None,
        metadata_keys: list[str] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[TimeSeries]:
        for ts in await self.client.read_time_series(
            paths=paths,
            ts_filters=ts_filters,
            metadata_keys=metadata_keys,
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
            **kwargs,
        ):
            yield ts

    async def update_time_series(
        self, path: str, metadata: dict[str, Any] | TimeSeriesMetadata, **kwargs: Any
    ) -> None:
        await self.client.update_time_series(metadatas={path: metadata}, error_handling="raise", **kwargs)

    async def update_time_series_bulk(
        self,
        paths: list[str],
        metadatas: list[dict[str, Any] | TimeSeriesMetadata],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        return await self.client.update_time_series(
            metadatas=dict(zip(paths, metadatas)),
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
            **kwargs,
        )

    async def delete_time_series(self, *, path: str, **kwargs: Any) -> None:
        await self.client.delete_time_series(paths=[path], error_handling="raise", **kwargs)

    async def delete_time_series_bulk(
        self,
        paths: list[str],
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        return await self.client.delete_time_series(
            paths,
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
            **kwargs,
        )

    async def read_coverage(
        self,
        path: str,
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> tuple[datetime | None, datetime | None]:
        return list(
            (
                await self.client.read_coverage(
                    [TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member)],
                    error_handling="raise",
                    **kwargs,
                )
            ).values()
        )[0]

    async def read_coverage_bulk(
        self,
        paths: Iterable[str],
        *,
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = (None, None),
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> Sequence[tuple[datetime | None, datetime | None]]:
        return list(
            (
                await self.client.read_coverage(
                    [
                        TimeSeriesKey(path=p, t0=t, dispatch_info=di, member=m)
                        for p, t, di, m in zip(
                            paths, make_iterable(t0), make_iterable(dispatch_info), make_iterable(member)
                        )
                    ],
                    concurrency_limit=concurrency_limit,
                    error_handling=error_handling,
                    default_value=default_value,
                    default_factory=default_factory,
                    **kwargs,
                )
            ).values()
        )

    async def read_ensemble_members(
        self,
        path: str,
        *,
        t0_start: datetime | None = None,
        t0_end: datetime | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[EnsembleMember]:
        for ensemble in list(
            (
                await self.client.read_ensemble_members(
                    [path], t0_start=t0_start, t0_end=t0_end, error_handling="raise", **kwargs
                )
            ).values()
        )[0]:
            yield ensemble

    async def read_ensemble_members_bulk(
        self,
        paths: list[str],
        *,
        t0_start: list[datetime] | datetime | None = None,
        t0_end: list[datetime] | datetime | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[list[EnsembleMember]]:
        return list(
            (
                await self.client.read_ensemble_members(
                    paths,
                    t0_start=t0_start,
                    t0_end=t0_end,
                    concurrency_limit=concurrency_limit,
                    error_handling=error_handling,
                    default_value=default_value,
                    default_factory=default_factory,
                    **kwargs,
                )
            ).values()
        )

    async def read_data_frame(
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
        return list(
            (
                await self.client.read_data_frame(
                    [TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member)],
                    start=start,
                    end=end,
                    columns=columns,
                    error_handling="raise",
                    **kwargs,
                )
            ).values()
        )[0]

    async def read_data_frame_bulk(
        self,
        paths: Iterable[str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = lambda: pd.DataFrame(
            index=pd.DatetimeIndex([], dtype="datetime64[ms, UTC]")
        ),
        **kwargs: Any,
    ) -> dict[str, pd.DataFrame]:
        return {
            key.path: df
            for key, df in (
                await self.client.read_data_frame(
                    [
                        TimeSeriesKey(path=p, t0=t, dispatch_info=di, member=m)
                        for p, t, di, m in zip(
                            paths, make_iterable(t0), make_iterable(dispatch_info), make_iterable(member)
                        )
                    ],
                    start=start,
                    end=end,
                    concurrency_limit=concurrency_limit,
                    error_handling=error_handling,
                    default_value=default_value,
                    default_factory=default_factory,
                    **kwargs,
                )
            ).items()
        }

    async def read_data_frames(
        self,
        paths: Iterable[str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        **kwargs: Any,
    ) -> dict[str, pd.DataFrame]:
        return await self.read_data_frame_bulk(
            paths=paths, start=start, end=end, t0=t0, dispatch_info=dispatch_info, member=member, **kwargs
        )

    async def write_data_frame(
        self,
        path: str,
        data_frame: pd.DataFrame,
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        await self.client.write_data_frame(
            {TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member): data_frame},
            error_handling="raise",
            **kwargs,
        )

    async def write_data_frame_bulk(
        self,
        paths: Iterable[str],
        data_frames: Iterable[pd.DataFrame],
        *,
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        return await self.client.write_data_frame(
            {
                TimeSeriesKey(path=p, t0=t, dispatch_info=di, member=m): df
                for p, t, di, m, df in zip(
                    paths,
                    make_iterable(t0),
                    make_iterable(dispatch_info),
                    make_iterable(member),
                    data_frames,
                )
            },
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
            **kwargs,
        )

    async def write_data_frames(
        self,
        paths: Iterable[str],
        *,
        data_frames: Iterable[pd.DataFrame],
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        **kwargs: Any,
    ) -> None:
        await self.write_data_frame_bulk(
            paths=paths,
            data_frames=data_frames,
            t0=t0,
            dispatch_info=dispatch_info,
            member=member,
            **kwargs,
        )

    async def delete_data_range(
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
        await self.client.delete_data_range(
            [TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member)],
            start=start,
            end=end,
            error_handling="raise",
            **kwargs,
        )

    async def delete_data_range_bulk(
        self,
        paths: list[str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        return await self.client.delete_data_range(
            [
                TimeSeriesKey(path=p, t0=t, dispatch_info=di, member=m)
                for p, t, di, m in zip(
                    paths, make_iterable(t0), make_iterable(dispatch_info), make_iterable(member)
                )
            ],
            start=start,
            end=end,
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
            **kwargs,
        )

    async def read_comments(
        self,
        path: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[TimeSeriesComment]:
        for comment in list(
            (
                await self.client.read_comments(
                    [TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member)],
                    start=start,
                    end=end,
                    error_handling="raise",
                    **kwargs,
                )
            ).values()
        )[0]:
            yield comment

    async def read_comments_bulk(
        self,
        paths: list[str],
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        t0: datetime | Iterable[datetime | None] | None = None,
        dispatch_info: str | Iterable[str | None] | None = None,
        member: str | Iterable[str | None] | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[list[TimeSeriesComment]]:
        return list(
            (
                await self.client.read_comments(
                    [
                        TimeSeriesKey(path=p, t0=t, dispatch_info=di, member=m)
                        for p, t, di, m in zip(
                            paths, make_iterable(t0), make_iterable(dispatch_info), make_iterable(member)
                        )
                    ],
                    start=start,
                    end=end,
                    concurrency_limit=concurrency_limit,
                    error_handling=error_handling,
                    default_value=default_value,
                    default_factory=default_factory,
                    **kwargs,
                )
            ).values()
        )

    async def write_comments(
        self,
        path: str,
        comments: list[TimeSeriesComment],
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        await self.client.write_comments(
            {TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member): comments},
            error_handling="raise",
            **kwargs,
        )

    async def write_comments_bulk(
        self,
        paths: list[str],
        comments: list[list[TimeSeriesComment]],
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        return await self.client.write_comments(
            {
                TimeSeriesKey(path=p, t0=t, dispatch_info=di, member=m): c
                for p, t, di, m, c in zip(
                    paths, make_iterable(t0), make_iterable(dispatch_info), make_iterable(member), comments
                )
            },
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
            **kwargs,
        )

    async def delete_comments(
        self,
        path: str,
        comments: list[TimeSeriesComment],
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        await self.client.delete_comments(
            {TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member): comments},
            error_handling="raise",
            **kwargs,
        )

    async def delete_comments_bulk(
        self,
        paths: list[str],
        comments: list[list[TimeSeriesComment]],
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        return await self.client.delete_comments(
            {
                TimeSeriesKey(path=p, t0=t, dispatch_info=di, member=m): c
                for p, t, di, m, c in zip(
                    paths, make_iterable(t0), make_iterable(dispatch_info), make_iterable(member), comments
                )
            },
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
            **kwargs,
        )

    async def info(self) -> dict[str, Any]:
        return await self.client.info()
