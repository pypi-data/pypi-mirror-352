from __future__ import annotations

import asyncio
import inspect
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Coroutine, Iterable, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from typing import Any, Iterator, Literal, Protocol, SupportsIndex, Type, TypeVar, Union, overload

import pandas as pd
from pydantic import ValidationError

from ..exceptions import TimeSeriesUserError
from ..schema import CommentSupport, EnsembleMember, TimeSeriesComment, TimeSeriesKey, TimeSeriesMetadata
from ..time_series import TimeSeries
from ..utils import bulk_concurrent, model_dump, model_validate

T = TypeVar("T")
TimeSeriesMetadataType = Union[TimeSeries, TimeSeriesMetadata, dict[str, Any]]
# To avoid mypy complaining if you pass a dict[TimeSeriesKey, pd.DataFrame]
DataFrameTypedDicts = Union[
    dict[str, pd.DataFrame],
    dict[TimeSeriesKey, pd.DataFrame],
    dict[Union[str, TimeSeriesKey], pd.DataFrame],
]
TSCommentsTypedDicts = Union[
    dict[str, list[TimeSeriesComment]],
    dict[TimeSeriesKey, list[TimeSeriesComment]],
    dict[Union[str, TimeSeriesKey], list[TimeSeriesComment]],
]

# The following types are needed to partially solve the problem of differentiating
# str from Iterable/Sequence[str] in overloaded methods. It solves our problem only
# for Sequence, which does not cover the case of passing just an Iterable.
# Source from https://github.com/hauntsaninja/useful_types
_T_co = TypeVar("_T_co", covariant=True)


# Source from https://github.com/python/typing/issues/256#issuecomment-1442633430
# This works because str.__contains__ does not accept object (either in typeshed or at runtime)
class SequenceNotStr(Protocol[_T_co]):
    @overload
    def __getitem__(self, index: SupportsIndex, /) -> _T_co: ...

    @overload
    def __getitem__(self, index: slice, /) -> Sequence[_T_co]: ...

    def __contains__(self, value: object, /) -> bool: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[_T_co]: ...

    def index(self, value: Any, /, start: int = 0, stop: int = ...) -> int: ...

    def count(self, value: Any, /) -> int: ...

    def __reversed__(self) -> Iterator[_T_co]: ...


class TimeSeriesClient(ABC):
    """
    This abstract class defines the API of the TimeSeriesClient, and it's the main
    class to implement in order to support a new time series backend.

    The comment access methods are optional and the supported methods should be
    reflected in the class attribute `comment_support`.

    In case your backend needs a custom TimeSeriesMetadata class, you can override
    the class attribute `time_series_schema` with your custom pydantic model.

    All the methods to implement are for bulk operations, this is to simplify the
    amount of methods to implement in each specific backend. In case that the
    backend you develop against doesn't have any bulk support you can use the generic
    bulk_concurrent method.

    Since we are doing bulk operations by default now, there are several ways on
    how you can handle errors and partial errors. As much as possible the user
    should have total control over that behavior via the standard keyword arguments:
    'error_handling', 'default_value' and 'default_factory'. Nonetheless, the standard
    behavior should always throw a warning in case there was any number of errors,
    if it was a read operation it should omit the result or replace by a suitable default
    and if it was a write operation it should return a list of exceptions.
    """

    comment_support: CommentSupport = CommentSupport.UNSUPPORTED
    time_series_schema: Type[TimeSeriesMetadata] = TimeSeriesMetadata

    @classmethod
    def sanitize_metadata(
        cls,
        *,
        path: str | None = None,
        metadata: TimeSeriesMetadataType | None = None,
    ) -> TimeSeriesMetadata:
        """
        Sanitize the metadata validating it against the TimeSeriesClient.time_series_schema model,
        and return a TimeSeriesMetadata object.

        Args:
            path: The time series path.
            metadata: The metadata to sanitize.

        Returns:
            The sanitized metadata.
        """
        if isinstance(metadata, TimeSeries):
            metadata = metadata.metadata
        elif isinstance(metadata, TimeSeriesMetadata):
            metadata = model_dump(metadata)
        if metadata and path:
            try:
                metadata = model_validate(cls.time_series_schema, {**metadata, "path": path})
            except ValidationError as e:
                msg = f"Invalid metadata {metadata} for time series {path}"
                raise TimeSeriesUserError(msg, str(path)) from e
        elif path:
            metadata = cls.time_series_schema(path=path)
        elif metadata:
            metadata = model_validate(cls.time_series_schema, metadata)
        else:
            msg = "Invalid arguments: path and metadata cannot be both None"
            raise TimeSeriesUserError(msg, str(path))
        return metadata

    @abstractmethod
    async def __aenter__(self) -> TimeSeriesClient:
        """Enter the async context"""

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the async context"""

    def run_sync(self, coroutine: Callable[..., Coroutine[Any, Any, T]], *args: Any, **kwargs: Any) -> T:
        """
        This method safely calls async methods from a sync context.

        So it has come to this...

        We could be in one of several states:

        1. It's a fully sync context, it's the main thread and no event loop is
           running.
        2. There might be an event loop running, but it is in a different
           thread.
        3. There is an event loop running in our thread, but this is a sync
           function, so we can't await.

        To run the coroutine, we need to take into account that:

        1. Using asyncio.run() in our current thread is not safe, because it
           starts and then cleans up event loops. This modifies global state and
           can break the assumptions of other packages.
        2. Using asyncio.get_event_loop() will create an event loop, but only if
           it's in the main thread. It will also leave the loop running, even when
           it's not needed anymore. This also modifies global state and can break
           the assumptions of other packages. Moreover, it is known to have
           complex behaviour, so it's best to avoid this method when possible.

        Taking these into consideration, the best solution seems to be just
        spawning a new loop in a temporary thread, and using asyncio.run there.

        While not optimal from a performance perspective, it ensures that both
        sync and async contexts can work as a high-level user would expect.

        In performance-critical contexts, the overhead can be reduced by
        gathering multiple async operations into the same coroutine. Of course,
        the overhead would be avoided completely by just using the async API
        correctly...
        """
        if not inspect.iscoroutinefunction(coroutine):
            msg = f"{coroutine} is not a coroutine"
            raise ValueError(msg)

        async def dispatched_execution() -> T:
            # This function bundles the dispatched operations into a single
            # top-level awaitable, so that we only need to call
            # executor.submit() and asyncio.run() once.
            async with self:
                return await coroutine(*args, **kwargs)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future: Future[T] = executor.submit(asyncio.run, dispatched_execution())
            return future.result()

    async def _bulk_concurrent(
        self,
        awaitables: Iterable[Awaitable[T]],
        concurrency_limit: int = 32,
        error_handling: Literal["default", "return", "raise"] = "default",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
    ) -> list[T | Exception]:
        """
        Utility method to asyncio gather awaitables without exceeding the concurrency_limit.

        Args:
            awaitables: The list of awaitables.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.

        Returns:
            The list of results.
        """
        return await bulk_concurrent(
            awaitables,
            concurrency_limit=concurrency_limit,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
        )

    @staticmethod
    def build_bulk_kwargs(
        concurrency_limit: int | None,
        error_handling: Literal["default", "return", "raise"] | None,
        default_value: Any | None,
        default_factory: Callable[[], Any] | None,
    ) -> dict[str, Any]:
        bulk_kwargs: dict[str, Any] = {}
        if concurrency_limit:
            bulk_kwargs["concurrency_limit"] = concurrency_limit
        if error_handling:
            bulk_kwargs["error_handling"] = error_handling
        if default_value:
            bulk_kwargs["default_value"] = default_value
        if default_factory:
            bulk_kwargs["default_factory"] = default_factory
        return bulk_kwargs

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

    @abstractmethod
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
        """
        Create all time series.

        Args:
            metadatas: The time series metadata or an iterable of metadata.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.

        Returns:
            The list of TimeSeries objects.
        """

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

    @abstractmethod
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
        """
        Read time series in bulk, from either paths, time series filters or both.

        Args:
            paths: A list of time series paths.
            ts_filters: A list of time series filters.
            metadata_keys: A list of metadata keys to read. Set to None to request all metadata.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional keyword arguments to be passed to the backend.

        Returns:
            An AsyncIterator over the resulting TimeSeries objects.
        """

    @abstractmethod
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
        """
        Update time series metadata in bulk.

        Args:
            metadatas: A list of time series metadatas or a dictionary with time series paths
              as keys and metadata as values.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.
        """

    @abstractmethod
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
        """
        Delete time series in bulk.

        Args:
            paths: A time series path or a list of them.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.
        """

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

    @abstractmethod
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
        """
        Get the time series coverages.

        Args:
            keys: A time series key/path or a list of them.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.

        Returns:
            A list of coverages.
        """

    @overload
    async def read_ensemble_members(
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

    @abstractmethod
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
        """
        Read the ensemble members for multiple time series.

        Args:
            paths: A list of time series paths.
            t0_start: A list of t0 start times to filter for.
            t0_end: A listr of t0 end time to filter for.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.

        Returns:
            A list with the list of ensembles per each time series path.
        """

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

    @abstractmethod
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
        """
        Read multiple TimeSeries as data frames.

        Notes:
            This method can be overwritten on backends which support bulk operations.

        Args:
            keys: An iterable of time series keys or paths.
            start: An optional iterable of datetimes representing the date from which data will be written,
                if a single datetime is passed it is used for all the TimeSeries.
            end: An optional iterable of datetimes representing the date until (included) which data will be
                written, if a single datetime is passed it is used for all the TimeSeries.
            columns: The list of column keys to read.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.
        """

    @abstractmethod
    async def write_data_frame(
        self,
        data_frames: DataFrameTypedDicts,
        *,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> None | Sequence[Exception]:
        """
        Write multiple data frames to TimeSeries

        Notes:
            This method can be overwritten on backends which support bulk operations.

        Args:
            data_frames: A dictionary with TimeSeriesKey or path as keys and pd.DataFrame as values.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.
        """

    @abstractmethod
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
        """
        Delete time series data in a bulk

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
        """

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
        Read time series comments.

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
            A dictionary of time series keys and comments.
        """
        raise NotImplementedError

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
            comments: A dictionary with TimeSeriesKey or path as keys and comments as values.
            concurrency_limit: The maximum concurrency tolerated.
            error_handling: If "default" return a default value, if "return" will return error objects
              and if "raise" will raise on first encountered error.
            default_value: The default value.
            default_factory: The default factory provider.
            **kwargs: Additional backend specific keyword arguments.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    async def info(self) -> dict[str, Any]:
        """
        Return information of the store or fail if the store has any problem.

        NOTE: this default implementation should be overwritten on each implementation.
        """
        return {}
