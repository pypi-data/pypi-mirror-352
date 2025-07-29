from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import orjson
import pandas as pd
import pyarrow as pa  # type: ignore
from pyarrow import parquet as pq

from kisters.water.time_series.core import (
    EnsembleComponent,
    EnsembleMember,
    TimeSeries,
    TimeSeriesComment,
    TimeSeriesMetadata,
)
from kisters.water.time_series.core.schema import CommentSupport
from kisters.water.time_series.core.utils import model_dump
from kisters.water.time_series.memory.memory_time_series_client import (
    MemoryTimeSeriesClient,
)


class ParquetTimeSeriesClient(MemoryTimeSeriesClient):
    comment_support = CommentSupport.UNSUPPORTED

    path_column_key = "path"
    timestamp_column_key = "ts"
    index_columns = [
        path_column_key,
        EnsembleComponent.T0,
        EnsembleComponent.MEMBER,
        EnsembleComponent.DISPATCH_INFO,
        timestamp_column_key,
    ]
    categorical_columns = [
        path_column_key,
        EnsembleComponent.T0,
        EnsembleComponent.MEMBER,
        EnsembleComponent.DISPATCH_INFO,
    ]
    ts_metadata_field = b"tsMetadata"

    def __init__(self, filename: str | Path):
        super().__init__()

        self._filename = Path(filename).resolve()
        if self._filename.is_file():
            self._load_table()
        self._data_changed = False

    def _load_table(self) -> None:
        # Load Parquet file
        master_table = pq.read_table(self._filename)

        # Extract metadata
        master_metadata = orjson.loads(master_table.schema.metadata[self.ts_metadata_field])
        for path, metadata in master_metadata.items():
            self._ts_metadata[path] = self.sanitize_metadata(path=path, metadata=metadata)

        # Convert to pandas
        master_df = master_table.to_pandas(self_destruct=True)
        del master_table

        # Set index
        master_df.set_index(
            self.index_columns,
            inplace=True,
        )

        # Partition into traces
        for (path, t0, member, dispatch_info), group in master_df.groupby(
            level=self.categorical_columns, observed=True
        ):
            df_ts = (
                group.reset_index()
                .drop(columns=self.categorical_columns)
                .set_index(self.timestamp_column_key)
            )

            self._ts_data.setdefault(path, {})
            self._ts_data[path][
                EnsembleMember(
                    t0=pd.to_datetime(t0) if t0 else None,
                    dispatch_info=dispatch_info or None,
                    member=member or None,
                )
            ] = df_ts

    async def __aenter__(self) -> ParquetTimeSeriesClient:
        self._data_changed = False
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._data_changed:
            self._save_table()
            self._data_changed = False

    def _save_table(self) -> None:
        # Build master data frame
        data_frames = []
        metadata = {}
        for ts_path, ts_metadata in self._ts_metadata.items():
            metadata[ts_path] = model_dump(ts_metadata)
            for member_info, df in self._ts_data[ts_path].items():
                if not df.index.name:
                    df.index.name = self.timestamp_column_key
                df_copy = df.reset_index()
                df_copy.insert(0, self.path_column_key, ts_path)
                df_copy.insert(
                    1,
                    EnsembleComponent.T0,
                    member_info.t0.isoformat() if member_info.t0 else "",
                )  # Don't use a datetime column here as it triggers some undesirable magic inside pandas.
                df_copy.insert(
                    2,
                    EnsembleComponent.MEMBER,
                    member_info.member if member_info.member else "",
                )
                df_copy.insert(
                    3,
                    EnsembleComponent.DISPATCH_INFO,
                    member_info.dispatch_info if member_info.dispatch_info else "",
                )
                data_frames.append(df_copy)
        if len(data_frames) > 0:
            master_df = pd.concat(data_frames)
        else:
            master_df = pd.DataFrame(data={index_column: [] for index_column in self.index_columns})
        for column in self.categorical_columns:
            master_df[column] = master_df[column].astype("category")  # Save memory

        # Convert master data frame to arrow table
        table = pa.Table.from_pandas(master_df, preserve_index=False)

        # Add metadata
        table = table.replace_schema_metadata(
            {
                **table.schema.metadata,
                self.ts_metadata_field: orjson.dumps(
                    metadata, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC
                ),
            }
        )

        # Save
        pq.write_table(table, self._filename)

    async def _create_time_series(
        self,
        metadata: TimeSeriesMetadata,
        **kwargs: Any,
    ) -> TimeSeries:
        self._data_changed = True
        return await super()._create_time_series(metadata=metadata, **kwargs)

    async def _update_time_series(self, metadata: TimeSeriesMetadata, **kwargs: Any) -> None:
        self._data_changed = True
        await super()._update_time_series(metadata=metadata, **kwargs)

    async def _delete_time_series(self, path: str, **kwargs: Any) -> None:
        self._data_changed = True
        return await super()._delete_time_series(path, **kwargs)

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
        self._data_changed = True
        await super()._write_data_frame(
            path,
            data_frame=data_frame,
            t0=t0,
            dispatch_info=dispatch_info,
            member=member,
            **kwargs,
        )

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
        self._data_changed = True
        await super()._delete_data_range(
            path,
            start=start,
            end=end,
            t0=t0,
            dispatch_info=dispatch_info,
            member=member,
            **kwargs,
        )

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

    async def info(self) -> dict[str, Any]:
        stat = self._filename.stat()
        return {
            "file-size": stat.st_size,
            "last-modified": stat.st_mtime,
        }
