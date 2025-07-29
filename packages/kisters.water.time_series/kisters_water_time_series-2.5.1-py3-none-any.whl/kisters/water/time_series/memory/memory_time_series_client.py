from __future__ import annotations

import re
import uuid
from datetime import datetime
from sys import getsizeof
from typing import Any

import pandas as pd
from typing_extensions import Self

from kisters.water.time_series.core import (
    TimeSeries,
    TimeSeriesComment,
    TimeSeriesMetadata,
    TimeSeriesNotFoundError,
    TimeSeriesUserError,
)
from kisters.water.time_series.core.schema import CommentSupport, EnsembleMember
from kisters.water.time_series.core.time_series_client import TimeSeriesClientHelper
from kisters.water.time_series.core.utils import model_copy, model_dump, model_validate


class MemoryTimeSeriesClient(TimeSeriesClientHelper):
    comment_support = CommentSupport.READ | CommentSupport.WRITE | CommentSupport.DELETE
    minimum_metadata_keys = {"path", "columns", "short_name", "is_forecast", " timezone"}

    def __init__(self) -> None:
        self._ts_metadata: dict[str, TimeSeriesMetadata] = {}
        self._ts_data: dict[str, dict[EnsembleMember, pd.DataFrame]] = {}
        self._ts_comments: dict[str, dict[EnsembleMember, dict[str, TimeSeriesComment]]] = {}

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """"""

    async def _create_time_series(self, metadata: TimeSeriesMetadata, **kwargs: Any) -> TimeSeries:
        self._ts_metadata[metadata.path] = metadata
        self._ts_data[metadata.path] = {}
        self._ts_comments[metadata.path] = {}
        return TimeSeries(self, metadata=metadata)

    async def _read_time_series(
        self, path: str, metadata_keys: list[str] | None = None, **kwargs: Any
    ) -> TimeSeries:
        metadata = self._ts_metadata[path]
        if metadata_keys is not None:
            metadata = model_validate(
                self.time_series_schema,
                model_dump(metadata, include=set(metadata_keys) | self.minimum_metadata_keys),
            )
        try:
            return TimeSeries(self, metadata=metadata)
        except KeyError as e:
            raise TimeSeriesNotFoundError(path) from e

    async def _filter_time_series(
        self, ts_filter: str | None, metadata_keys: list[str] | None = None, **kwargs: Any
    ) -> list[TimeSeries]:
        if ts_filter is None:
            return [TimeSeries(self, metadata=metadata) for metadata in self._ts_metadata.values()]

        exp = re.compile(
            "^"
            + ts_filter.replace(".", "\\.").replace("/", "\\/").replace("?", "\\?").replace("*", ".*")
            + "$"
        )
        return [
            TimeSeries(self, metadata=metadata)
            for path, metadata in self._ts_metadata.copy().items()
            if exp.match(path)
        ]

    async def _update_time_series(self, metadata: TimeSeriesMetadata, **kwargs: Any) -> None:
        await self._create_time_series(metadata=metadata)

    async def _delete_time_series(self, path: str, **kwargs: Any) -> None:
        try:
            del self._ts_metadata[path]
            del self._ts_data[path]
            del self._ts_comments[path]
        except KeyError as e:
            raise TimeSeriesNotFoundError(path) from e

    def _get_data_frame(self, path: str, ensemble_member: EnsembleMember) -> pd.DataFrame:
        try:
            ts_data = self._ts_data[path]
        except KeyError as e:
            raise TimeSeriesNotFoundError(path) from e
        return ts_data.get(
            ensemble_member, pd.DataFrame(index=pd.DatetimeIndex([], dtype="datetime64[ms, UTC]"))
        )

    async def _read_coverage(
        self,
        path: str,
        *,
        t0: datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> tuple[datetime | None, datetime | None]:
        ensemble_member = EnsembleMember(t0=t0, dispatch_info=dispatch_info, member=member)
        ensemble_df = self._get_data_frame(path, ensemble_member)
        assert isinstance(ensemble_df.index, pd.DatetimeIndex)
        return (
            ensemble_df.index[0].to_pydatetime() if ensemble_df.shape[0] > 0 else None,
            ensemble_df.index[-1].to_pydatetime() if ensemble_df.shape[0] > 0 else None,
        )

    async def _read_ensemble_members(
        self,
        path: str,
        *,
        t0_start: datetime | None = None,
        t0_end: datetime | None = None,
        **kwargs: Any,
    ) -> list[EnsembleMember]:
        try:
            ts_data = self._ts_data[path]
        except KeyError as err:
            raise TimeSeriesNotFoundError(path) from err
        return [
            ensemble
            for ensemble in ts_data
            if (t0_start is None or ensemble.t0 is not None and t0_start <= ensemble.t0)
            and (t0_end is None or ensemble.t0 is not None and ensemble.t0 <= t0_end)
        ]

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
        ensemble_df = self._get_data_frame(
            path, EnsembleMember(t0=t0, dispatch_info=dispatch_info, member=member)
        )

        columns_loc = columns if columns else slice(None)
        assert isinstance(ensemble_df.index, pd.DatetimeIndex)
        if start is not None and end is not None:
            return ensemble_df.loc[
                (ensemble_df.index >= start) & (ensemble_df.index <= end), columns_loc  # type:ignore
            ].copy()
        if start is not None:
            return ensemble_df.loc[ensemble_df.index >= start, columns_loc].copy()  # type:ignore
        if end is not None:
            return ensemble_df.loc[ensemble_df.index <= end, columns_loc].copy()  # type:ignore
        return ensemble_df.loc[:, columns_loc].copy()

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
        if data_frame.shape[0] == 0:
            return
        self._ts_data.setdefault(path, {})
        ensemble_member = EnsembleMember(t0=t0, dispatch_info=dispatch_info, member=member)
        ensemble_df = self._get_data_frame(path, ensemble_member)

        assert isinstance(data_frame.index, pd.DatetimeIndex)
        if data_frame.index.tz is None:
            msg = "The data_frame time index doesn't have timezone"
            raise TimeSeriesUserError(msg, path)

        if ensemble_df.shape[0] == 0:
            ensemble_df = data_frame
        else:
            is_in = data_frame.index.isin(ensemble_df.index)
            ensemble_df.loc[ensemble_df.index.isin(data_frame.index), data_frame.columns] = data_frame.loc[
                is_in
            ].astype(ensemble_df[data_frame.columns].dtypes)
            if (not_in_df := data_frame.loc[~is_in]).shape[0] != 0:
                ensemble_df = pd.concat([ensemble_df, not_in_df])
                ensemble_df = ensemble_df.reindex(ensemble_df.index.sort_values())
        self._ts_data[path][ensemble_member] = ensemble_df

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
        self._ts_data.setdefault(path, {})
        ensemble_member = EnsembleMember(t0=t0, dispatch_info=dispatch_info, member=member)
        try:
            ts_data = self._ts_data[path]
        except KeyError as e:
            raise TimeSeriesNotFoundError(path) from e

        if start is None and end is None:
            del ts_data[ensemble_member]
        else:
            try:
                ensemble_df = ts_data[ensemble_member]
                if start is not None and end is not None:
                    ts_data[ensemble_member] = ensemble_df.loc[
                        (ensemble_df.index < start) | (end < ensemble_df.index)
                    ]
                elif start is not None:
                    ts_data[ensemble_member] = ensemble_df.loc[ensemble_df.index < start]
                elif end is not None:
                    ts_data[ensemble_member] = ensemble_df.loc[end < ensemble_df.index]
            except KeyError:
                pass

    def _get_comments(self, path: str, ensemble_member: EnsembleMember) -> dict[str, TimeSeriesComment]:
        try:
            ts_comments = self._ts_comments[path]
        except KeyError as e:
            raise TimeSeriesNotFoundError(path) from e
        try:
            return ts_comments[ensemble_member]
        except KeyError:
            return {}

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
        ensemble_member = EnsembleMember(t0=t0, dispatch_info=dispatch_info, member=member)
        ts_comments = self._get_comments(path, ensemble_member)
        return [
            comment
            for comment in ts_comments.values()
            if (start is None or start <= comment.end) and (end is None or end >= comment.start)
        ]

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
        ensemble_member = EnsembleMember(t0=t0, dispatch_info=dispatch_info, member=member)
        ts_comments = self._get_comments(path, ensemble_member)

        for new_comment in comments:
            written = False
            if new_comment.id is not None:
                if new_comment.id in ts_comments:
                    ts_comments[new_comment.id] = new_comment.copy()
                    written = True
            else:
                new_comment.id = str(uuid.uuid4())
            if not written:
                comment_ids_to_remove = []
                for comment in ts_comments.values():
                    if (
                        comment.comment == new_comment.comment
                        and new_comment.start <= comment.end
                        and new_comment.end >= comment.start
                    ):
                        new_comment.start = min(new_comment.start, comment.start)
                        new_comment.end = max(new_comment.end, comment.end)
                        if new_comment.start == comment.start and new_comment.end == comment.end:
                            continue
                        assert comment.id
                        comment_ids_to_remove.append(comment.id)
                for id_ in comment_ids_to_remove:
                    del ts_comments[id_]
                ts_comments[new_comment.id] = model_copy(new_comment)
        self._ts_comments[path][ensemble_member] = ts_comments

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
        ensemble_member = EnsembleMember(t0=t0, dispatch_info=dispatch_info, member=member)
        ts_comments = self._get_comments(path, ensemble_member)
        if ts_comments and comments:
            comment_ids = [c.id for c in comments if c.id]
            if comment_ids:
                for id in comment_ids:
                    del ts_comments[id]
            comments_without_id = [c for c in comments if not c.id]
            for remove_c in comments_without_id:
                if remove_c.comment:
                    exp = re.compile(
                        "^"
                        + remove_c.comment.replace(".", "\\.")
                        .replace("/", "\\/")
                        .replace("?", "\\?")
                        .replace("*", ".*")
                        + "$"
                    )
                    comment_ids_to_remove = []
                    new_comments: list[TimeSeriesComment] = []
                    start, end = remove_c.start, remove_c.end
                    for comment in ts_comments.values():
                        if exp.match(comment.comment):
                            if (start_is_none := start is None or start < comment.end) and (
                                end_is_none := end is None or end > comment.start
                            ):
                                if (
                                    not start_is_none
                                    and start > comment.start
                                    and not end_is_none
                                    and end < comment.end
                                ):
                                    comment_ids_to_remove.append(comment.id)
                                    new_comments.extend(
                                        [
                                            TimeSeriesComment(
                                                comment="",
                                                id=str(uuid.uuid4()),
                                                start=comment.start,
                                                end=start,
                                            ),
                                            TimeSeriesComment(
                                                comment="",
                                                id=str(uuid.uuid4()),
                                                start=end,
                                                end=comment.end,
                                            ),
                                        ]
                                    )
                                elif (end_is_in_between := start_is_none or start <= comment.start) and (
                                    end_is_none or end <= comment.end
                                ):
                                    comment_ids_to_remove.append(comment.id)
                                elif end_is_in_between:
                                    comment.start = end
                                elif end_is_none or end <= comment.end:
                                    comment.end = start

                            if (start is None or start < comment.start) and (
                                end is None or end > comment.end
                            ):
                                comment_ids_to_remove.append(comment.id)
                            elif start is not None and start < comment.end:
                                comment.start = start

    async def info(self) -> dict[str, Any]:
        """This is just a close approximation to the memory consumed by the store"""
        overhead_dict_size = getsizeof(self._ts_data)
        df_size = 0
        for ensemble_dict_data in self._ts_data.values():
            overhead_dict_size += getsizeof(ensemble_dict_data)
            for df in ensemble_dict_data.values():
                df_size += df.values.size * df.values.itemsize
        metadata_size = sum(getsizeof(k) + getsizeof(model_dump(v)) for k, v in self._ts_metadata.items())
        overhead_dict_size += getsizeof(self._ts_comments)
        comment_size = 0
        for ensemble_dict_comments in self._ts_comments.values():
            overhead_dict_size += getsizeof(ensemble_dict_comments)
            for comments in ensemble_dict_comments.values():
                overhead_dict_size += getsizeof(comments)
                for c in comments.values():
                    comment_size += getsizeof(model_dump(c))
        return {"memory-used (bytes)": overhead_dict_size + df_size + metadata_size + comment_size}
