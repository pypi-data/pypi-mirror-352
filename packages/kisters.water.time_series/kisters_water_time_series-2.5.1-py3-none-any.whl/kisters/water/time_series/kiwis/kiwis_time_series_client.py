from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable, Sequence
from datetime import datetime
from typing import Any, Literal, Optional, TypeVar, overload
from warnings import warn

import pandas as pd
from httpx import Auth, Limits, Timeout

from kisters.water.time_series.core import (
    EnsembleMember,
    TimeSeries,
    TimeSeriesClient,
    TimeSeriesComment,
    TimeSeriesKey,
    TimeSeriesMetadata,
    TimeSeriesNotFoundError,
    TimeSeriesUserError,
)
from kisters.water.time_series.core.time_series_client.time_series_client import (
    DataFrameTypedDicts,
    SequenceNotStr,
    TimeSeriesMetadataType,
)
from kisters.water.time_series.core.utils import model_dump, model_validate, model_validator

from .async_auto_retry_client import DEFAULT_RETRY_POLICY, AsyncAutoRetryClient, RetryPolicy, orjson_dumps
from .exceptions import KiWISDataSourceError, KiWISNoResultsError

DEFAULT_TIMEOUT = Timeout(30.0)
DEFAULT_LIMITS = Limits(max_keepalive_connections=20, max_connections=20)
T = TypeVar("T")
CommentType = Literal["station", "parameter", "timeseries", "data", "agent", "all"]


class KiWISTimeSeriesMetadata(TimeSeriesMetadata):
    @model_validator(mode="before")
    @classmethod
    def validate_metadata(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["path"] = values.pop("ts_path")
        values["name"] = values.pop("ts_name")
        values["short_name"] = values.pop("ts_shortname")
        values["is_forecast"] = "ensemble" in values["short_name"]
        return values

    def to_kiwis_dict(self) -> dict[str, Any]:
        kiwis_dict = model_dump(self, exclude={"columns", "is_forecast", "timezone"})
        kiwis_dict["ts_path"] = kiwis_dict.pop("path")
        kiwis_dict["ts_name"] = kiwis_dict.pop("name")
        kiwis_dict["ts_shortname"] = kiwis_dict.pop("short_name")
        return kiwis_dict


DEFAULT_METADATA_RETURNFIELDS = {
    "station_name",
    "station_no",
    "station_id",
    "ts_id",
    "ts_name",
    "ts_path",
    "ts_shortname",
    "parametertype_id",
    "parametertype_name",
}
MAX_DATA_READ_DEPTH = 10
MAX_TS_PATH_FOR_META = 40
MAX_TS_PATH_FOR_DATA = 10


def isoparse(isodate: str | None) -> datetime | None:
    if not isodate:
        return None
    if isodate.lower().endswith("z"):
        isodate = f"{isodate[:-1]}+00:00"
    return datetime.fromisoformat(isodate)


class KiWISTimeSeries(TimeSeries):
    def __init__(self, client: TimeSeriesClient, metadata: dict[str, Any] | TimeSeriesMetadata):
        metadata = model_validate(KiWISTimeSeriesMetadata, metadata)
        super().__init__(client, metadata)
        start = getattr(self._metadata, "from", None)
        end = getattr(self._metadata, "to", None)
        if start and end:
            self._coverages[EnsembleMember()] = (isoparse(start), isoparse(end))


class KiWISTimeSeriesClient(TimeSeriesClient):
    """
    Notes:
    It is unclear how to implement ensemble functionality at the moment.
    On a quick read of the KiWIS documentation seems like reading the coverage
    of specific ensemble members is not possible.
    Reading of ensemble data seems possible via getTimeseriesEnsembleValues, but seems
    like you can't filter for specific ensemble members in the call parameters.

    Seems like you can retrieve a list of t0 via getTimeseriesValues with param
    getensembletimestampsonly=true if all ts_ids are ensmeble time series.

    getTimeseriesEnsembleValues, allows to filter t0 via date range, unclear if it's possible
    to hide/avoid retrieving the time series data to list/filter ensemble members.

    The dto returned should look like:
    dict[str(ts_id), list[EnsembleDict]]
    EnsembleDict(TypedDict):
        ensembledate: str  # t0 isodate
        ensembledispatchinfo: str
        timeseries: dict
            columns: list[str]  # (member1)timestamp,(member1)value,(member2)timestamp,(member2)value,...
            data: list
    """

    def __init__(
        self,
        base_url: str,
        datasource: int = 0,
        auth: Auth | None = None,
        timeout: Timeout = DEFAULT_TIMEOUT,
        limits: Limits = DEFAULT_LIMITS,
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        _internal_usage_key: str | None = None,
    ):
        self._base_url, self._endpoint = base_url.strip("/").rsplit("/", 1)
        self._datasource = datasource
        self._auth = auth
        self._timeout = timeout
        self._limits = limits
        self._retry_policy = retry_policy
        self._internal_usage_key = _internal_usage_key
        self._active_contexts = 0
        self._session_lock: asyncio.Lock | None = None

    def get_httpx_client(self) -> AsyncAutoRetryClient:
        return AsyncAutoRetryClient(
            auth=self._auth,
            base_url=self._base_url,
            limits=self._limits,
            timeout=self._timeout,
            retry_policy=self._retry_policy,
            _internal_usage_key=self._internal_usage_key,
        )

    async def __aenter__(self) -> KiWISTimeSeriesClient:
        if self._session_lock is None:
            self._session_lock = asyncio.Lock()
        self._active_contexts += 1
        if self._active_contexts == 1:
            async with self._session_lock:
                try:
                    self._session = self.get_httpx_client()
                    await self._session.__aenter__()
                except Exception:
                    self._active_contexts = 0
                    self._session = None  # type: ignore
                    raise
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._active_contexts -= 1
        if self._active_contexts == 0 and self._session is not None:
            async with self._session_lock:  # type: ignore
                await self._session.__aexit__()

    async def _bulk_concurrent(
        self,
        awaitables: Iterable[Awaitable[T]],
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = None,
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
    ) -> list[T | Exception]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit=concurrency_limit or self._limits.max_connections,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
        )
        return await super()._bulk_concurrent(awaitables=awaitables, **bulk_kwargs)

    def _base_params(
        self,
        request: str,
        datasource: int | None = None,
        format: str = "objson",
        returnfields: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        params = {
            "service": "kisters",
            "type": "queryServices",
            "datasource": datasource if datasource is not None else self._datasource,
            "request": request,
            "format": format,
            **kwargs,
        }
        if returnfields:
            params["returnfields"] = returnfields
        return params

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
        raise NotImplementedError

    async def _read_time_series(
        self,
        path: str,
        *,
        metadata_keys: list[str] | None = None,
        datasource: Optional[int] = None,
        **kwargs: Any,
    ) -> TimeSeries:
        if metadata_keys:
            returnfields = ",".join(set(metadata_keys) | {"ts_path"})
        else:
            returnfields = ",".join(DEFAULT_METADATA_RETURNFIELDS)
        params = self._base_params(
            "getTimeseriesList", ts_path=path, datasource=datasource, returnfields=returnfields
        )

        try:
            response = await self._session.get(self._endpoint, params=params)
        except KiWISNoResultsError:
            raise TimeSeriesNotFoundError(path=path) from None
        json = self._session.to_json(response)
        if json:
            return KiWISTimeSeries(self, json[0])
        raise TimeSeriesNotFoundError(path=path)

    async def _filter_time_series(
        self,
        ts_filter: str,
        *,
        metadata_keys: list[str] | None = None,
        datasource: Optional[int] = None,
        **kwargs: Any,
    ) -> list[TimeSeries]:
        if metadata_keys:
            returnfields = ",".join(set(metadata_keys) | {"ts_path"})
        else:
            returnfields = ",".join(DEFAULT_METADATA_RETURNFIELDS)
        params = self._base_params(
            "getTimeseriesList",
            **{"ts_path": ts_filter} if ts_filter else kwargs,
            datasource=datasource,
            returnfields=returnfields,
        )

        try:
            response = await self._session.get(self._endpoint, params=params)
        except KiWISNoResultsError:
            path = ts_filter if ts_filter else orjson_dumps(kwargs)
            raise TimeSeriesNotFoundError(path) from None  # type: ignore
        json = self._session.to_json(response)
        if json:
            return [KiWISTimeSeries(self, ts) for ts in json]
        return []  # Your query is technically correct but produces no results

    @overload
    async def read_time_series(
        self,
        *,
        paths: str,
        ts_filters: None = None,
        metadata_keys: list[str] | None = None,
        timeseriesgroup_id: None = None,
        stationgroup_id: None = None,
        parametergroup_id: None = None,
        datasource: Optional[int] = None,
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
        timeseriesgroup_id: str | None = None,
        stationgroup_id: str | None = None,
        parametergroup_id: str | None = None,
        datasource: Optional[int] = None,
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
        station_id: str | None = None,
        timeseriesgroup_id: str | None = None,
        stationgroup_id: str | None = None,
        parametergroup_id: str | None = None,
        datasource: Optional[int] = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> TimeSeries | list[TimeSeries]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit, error_handling, default_value, default_factory
        )
        if isinstance(paths, str) and (
            not ts_filters and not timeseriesgroup_id and not stationgroup_id and not parametergroup_id
        ):
            return await self._read_time_series(paths, metadata_keys=metadata_keys, **kwargs)

        errors = []
        results = []
        awaitables = []
        if paths:
            paths = [paths] if isinstance(paths, str) else list(paths)
            for path_g in [
                paths[i : i + MAX_TS_PATH_FOR_META] for i in range(0, len(paths), MAX_TS_PATH_FOR_DATA)
            ]:
                if path_g:
                    awaitables.append(
                        self._filter_time_series(
                            ts_filter=",".join(path_g),
                            metadata_keys=metadata_keys,
                            datasource=datasource,
                        )
                    )
        if ts_filters:
            ts_filters = [ts_filters] if isinstance(ts_filters, str) else ts_filters
            for ts_filter in ts_filters:
                awaitables.append(
                    self._filter_time_series(
                        ts_filter=ts_filter, metadata_keys=metadata_keys, datasource=datasource
                    )
                )
        if any([station_id, timeseriesgroup_id, stationgroup_id, parametergroup_id]):
            filter_kwargs = {}
            if station_id:
                filter_kwargs["station_id"] = station_id
            if timeseriesgroup_id:
                filter_kwargs["timeseriesgroup_id"] = timeseriesgroup_id
            if stationgroup_id:
                filter_kwargs["stationgroup_id"] = stationgroup_id
            if parametergroup_id:
                filter_kwargs["parametergroup_id"] = parametergroup_id
            awaitables.append(
                self._filter_time_series(
                    ts_filter="", metadata_keys=metadata_keys, datasource=datasource, **filter_kwargs
                )
            )
        if awaitables:
            for ts_list in await self._bulk_concurrent(awaitables=awaitables, **bulk_kwargs):
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
        raise NotImplementedError

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
        raise NotImplementedError

    @staticmethod
    def _key_as_path(key: str | TimeSeriesKey) -> str:
        if isinstance(key, str):
            return key
        return key.path

    @overload
    async def read_coverage(
        self,
        keys: TimeSeriesKey | str,
        *,
        datasource: Optional[int] = None,
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
        datasource: Optional[int] = None,
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
        datasource: Optional[int] = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = (None, None),
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> (
        tuple[datetime | None, datetime | None]
        | dict[TimeSeriesKey, tuple[datetime | None, datetime | None]]
    ):
        is_single_result = False
        if isinstance(keys, (TimeSeriesKey, str)):
            keys = [keys]
            is_single_result = True
        keys = [keys] if isinstance(keys, (TimeSeriesKey, str)) else list(keys)
        params = self._base_params(
            "getTimeseriesList",
            ts_path=",".join([k if isinstance(k, str) else k.path for k in keys]),
            datasource=datasource,
            returnfields="ts_path,coverage",
        )

        try:
            response = await self._session.get(self._endpoint, params=params)
        except KiWISNoResultsError:
            raise TimeSeriesNotFoundError(params["ts_path"]) from None
        json = self._session.to_json(response)
        if json:
            if is_single_result:
                return isoparse(json[0].get("from")), isoparse(json[0].get("to"))
            return {
                TimeSeriesKey(path=ts["ts_path"]): (isoparse(ts.get("from")), isoparse(ts.get("to")))
                for ts in json
            }
        return {}  # The query is technically correct but produces no results

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
        raise NotImplementedError

    @overload
    async def read_data_frame(
        self,
        keys: TimeSeriesKey | str,
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        columns: list[str] | None = None,
        timeseriesgroup_id: str | None = None,
        transformation: str | None = None,
        datasource: int | None = None,
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
        timeseriesgroup_id: str | None = None,
        transformation: str | None = None,
        datasource: int | None = None,
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
        timeseriesgroup_id: str | None = None,
        transformation: str | None = None,
        datasource: int | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = lambda: pd.DataFrame(
            index=pd.DatetimeIndex([], dtype="datetime64[ms, UTC]")
        ),
        **kwargs: Any,
    ) -> pd.DataFrame | dict[TimeSeriesKey, pd.DataFrame]:
        """
        The paths accept transformations individually by placing the transformation after the path.
        This is the same as in KiWIS API, e.g. ["a/b/c/d;factor(3.0)", TimeSeriesKey(path="a/b/c/d;factor(2.0)")]

        You can read and transform time series groups, by specifying and empty list or empty string as keys,
        and passing the kwargs timeseriesgroup_id and transformation. Same as in KiWIS API.
        """
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit=concurrency_limit or self._limits.max_connections,
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
        )
        is_single_result = False
        if isinstance(keys, (str, TimeSeriesKey)):
            keys = [keys]
            if not timeseriesgroup_id:
                is_single_result = True
        paths = [k.path if isinstance(k, TimeSeriesKey) else k for k in keys]
        if not columns:
            returnfields = "Timestamp,Value,Quality Code"
        else:
            if "Timestamp" not in columns:
                columns = ["Timestamp"] + columns
            for i, col in enumerate(columns):
                if col == "value":
                    columns[i] = "Value"
                if "quality" in col:
                    columns[i] = "Quality Code"
                if "interpolation" in col:
                    columns[i] = "Interpolation Type"
            returnfields = ",".join(columns)
        params = self._base_params(
            "getTimeseriesValues",
            datasource=datasource,
            format="dajson",
            returnfields=returnfields,
            metadata=True,
            md_returnfields="ts_path",
        )

        param_queries = []
        if (start is None or isinstance(start, datetime)) and (end is None or isinstance(end, datetime)):
            if paths:
                for path_g in [
                    ",".join(paths[i : i + MAX_TS_PATH_FOR_DATA])
                    for i in range(0, len(paths), MAX_TS_PATH_FOR_DATA)
                ]:
                    if path_g:
                        param_queries.append({**params, "ts_path": path_g})
            if timeseriesgroup_id:
                if transformation:
                    param_queries.append(
                        {
                            **params,
                            "timeseriesgroup_id": timeseriesgroup_id,
                            "transformation": transformation,
                        }
                    )
                else:
                    param_queries.append({**params, "timeseriesgroup_id": timeseriesgroup_id})

            if not param_queries:
                return {}
            results = await self._bulk_concurrent(
                (self._read_data(p, start=start, end=end) for p in param_queries),
                **bulk_kwargs,
            )
        elif timeseriesgroup_id:
            msg = (
                f"When providing a list of time ranges to read, 'timeseriesgroup_id'"
                f" must be None (was {timeseriesgroup_id})"
            )
            raise TimeSeriesUserError(msg, timeseriesgroup_id)
        elif len(paths) != len(list(start)) or len(paths) != len(list(end)):  # type: ignore
            msg = (
                f"When providing a list of time ranges to read (start_len={len(list(start))},"  # type: ignore
                f" end_len={len(list(end))}), they must match the paths (len={len(paths)})"  # type: ignore
            )
            raise TimeSeriesUserError(msg, ",".join(paths))
        elif paths:
            results = await self._bulk_concurrent(
                (
                    self._read_data(params={**params, "ts_path": p}, start=st, end=en)
                    for p, st, en in zip(paths, start, end)  # type: ignore
                ),
                **bulk_kwargs,
            )
        else:
            msg = f"No paths to read {','.join(paths)}"
            raise TimeSeriesUserError(msg, ",".join(paths))

        data_frames = {}
        errors = []
        for result in results:
            if isinstance(result, Exception):
                errors.append(result)
            else:
                data_frames.update(result)
        if errors:
            warn(f"Encountered {len(errors)} errors while reading data frames: {errors}", stacklevel=4)
        if is_single_result:
            if data_frames:
                return list(data_frames.values())[0]
            if errors:
                raise errors[0]
            return pd.DataFrame(index=pd.DatetimeIndex([], dtype="datetime64[ms, UTC]"))
        return data_frames

    async def _read_data(
        self, params: dict[str, Any], start: datetime | None, end: datetime | None, current_depth: int = 0
    ) -> dict[TimeSeriesKey, pd.DataFrame]:
        if start:
            params["from"] = start.isoformat()
        if end:
            params["to"] = end.isoformat()
        try:
            response = await self._session.get(self._endpoint, params=params)
        except KiWISDataSourceError:
            if current_depth <= MAX_DATA_READ_DEPTH and start and end:
                mid = start + (end - start) / 2
                new_depth = current_depth + 1
                half1 = await self._read_data(params, start=start, end=mid, current_depth=new_depth)
                half2 = await self._read_data(params, start=mid, end=end, current_depth=new_depth)
                joint_results = {}
                for key in half1.keys() - half2.keys():
                    joint_results[key] = half1[key]
                for key in half2.keys() - half1.keys():
                    joint_results[key] = half2[key]
                for key in half1.keys() & half2.keys():
                    df = pd.concat([half1[key], half2[key]], sort=True)
                    joint_results[key] = df[~df.index.duplicated(keep="first")]
                return joint_results
            raise
        json = self._session.to_json(response)
        if json:
            results = {}
            for data in json:
                columns = data["columns"].split(",")
                df = pd.DataFrame(data["data"], columns=columns)
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], utc=True)
                df = df.set_index("Timestamp")
                results[TimeSeriesKey(path=data["ts_path"])] = df[columns[1:]]
            return results
        return {}

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
        raise NotImplementedError

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
        raise NotImplementedError

    @overload
    async def read_comments(
        self,
        keys: TimeSeriesKey | str,
        *,
        start: datetime | Iterable[datetime | None] | None = None,
        end: datetime | Iterable[datetime | None] | None = None,
        comment_type: CommentType | list[CommentType] = "all",
        datasource: int | None = None,
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
        comment_type: CommentType | list[CommentType] = "all",
        datasource: int | None = None,
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
        comment_type: CommentType | list[CommentType] = "all",
        datasource: int | None = None,
        concurrency_limit: int | None = None,
        error_handling: Literal["default", "return", "raise"] | None = "return",
        default_value: Any = None,
        default_factory: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> list[TimeSeriesComment] | dict[TimeSeriesKey, list[TimeSeriesComment]]:
        bulk_kwargs = self.build_bulk_kwargs(
            concurrency_limit=concurrency_limit or self._limits.max_connections // 2,  # type: ignore
            error_handling=error_handling,
            default_value=default_value,
            default_factory=default_factory,
        )
        is_single_result = False
        if isinstance(keys, (TimeSeriesKey, str)):
            keys = [keys]
            is_single_result = True
        keys = [keys] if isinstance(keys, (TimeSeriesKey, str)) else list(keys)
        ts_paths = [k if isinstance(k, str) else k.path for k in keys]
        params = self._base_params(
            "getTimeseriesComments",
            datasource=datasource,
            comment_type=comment_type if isinstance(comment_type, str) else ",".join(comment_type),
        )
        if isinstance(start, Iterable) or isinstance(end, Iterable):
            msg = "Read comments for different time ranges for each time series is not yet implemented"
            raise NotImplementedError(msg)
        if start:
            params["from"] = start.isoformat()
        if end:
            params["to"] = end.isoformat()
        path_groups = [
            ",".join(ts_paths[i : i + MAX_TS_PATH_FOR_META])
            for i in range(0, len(ts_paths), MAX_TS_PATH_FOR_META)
        ]
        path_groups = [p for p in path_groups if p]

        ts_list_result, comments_results = await asyncio.gather(
            self._bulk_concurrent(
                (
                    self._session.get(
                        self._endpoint,
                        params=self._base_params(
                            "getTimeseriesList",
                            ts_path=paths,
                            datasource=datasource,
                            returnfields="ts_id,ts_path",
                        ),
                    )
                    for paths in path_groups
                ),
                **bulk_kwargs,
            ),
            self._bulk_concurrent(
                (
                    self._session.get(self._endpoint, params={"ts_path": paths, **params})
                    for paths in path_groups
                ),
                **bulk_kwargs,
            ),
        )

        ts_id_to_path = {}
        for ts_list in ts_list_result:
            if isinstance(ts_list, Exception):
                msg = f"Reading time series comments failed because {ts_list}"
                raise RuntimeError(msg) from ts_list
            for ts in self._session.to_json(ts_list):
                ts_id_to_path["ts_id"] = ts["ts_path"]
        if is_single_result:
            kiwis_comments = []
            for comments in comments_results:
                if isinstance(comments, Exception):
                    msg = f"Reading time series comments failed because {comments}"
                    raise RuntimeError(msg) from comments
                kiwis_comments += [self._parse_kiwis_comment(c) for c in self._session.to_json(comments)]
            return kiwis_comments

        comments_map: dict[TimeSeriesKey, list[TimeSeriesComment]] = {}
        errors = []
        for comment_list in comments_results:
            if isinstance(comment_list, Exception):
                if error_handling == "raise":
                    raise comment_list
                errors.append(comment_list)
            else:
                try:
                    for c in self._session.to_json(comment_list):
                        ts_path = ts_id_to_path[c["ts_id"]]
                        comments_map.setdefault(TimeSeriesKey(path=ts_path), [])
                        comments_map[TimeSeriesKey(path=ts_path)].append(self._parse_kiwis_comment(c))
                except Exception as e:
                    if error_handling == "raise":
                        raise
                    errors.append(e)
        if errors:
            warn(f"Encountered {len(errors)} errors while reading comments: {errors}", stacklevel=4)
        return comments_map

    @staticmethod
    def _parse_kiwis_comment(comment: dict[str, Any]) -> TimeSeriesComment:
        comment.pop("ts_id")
        comment["start"] = comment.pop("from")
        comment["end"] = comment.pop("to")
        return model_validate(TimeSeriesComment, comment)
