from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np
import pandas as pd
import pytest

from kisters.water.time_series.core import (
    EnsembleMember,
    TimeSeries,
    TimeSeriesColumn,
    TimeSeriesKey,
    TimeSeriesMetadata,
    TimeSeriesStore,
)
from kisters.water.time_series.core.utils import model_copy, model_dump


class TimeSeriesClientAsyncTest:
    STORE: TimeSeriesStore
    TS_PATH = str(uuid.uuid4())
    ENSEMBLE_TS_PATH = str(uuid.uuid4())
    MULTI_COLUMN_TS_PATH = str(uuid.uuid4())
    EMPTY_TS_PATH = str(uuid.uuid4())
    TIME_SERIES_MAP: dict[str, TimeSeries] = {}
    START_00 = datetime(year=2020, month=1, day=1, tzinfo=timezone.utc)
    START_12 = datetime(year=2020, month=1, day=1, hour=12, tzinfo=timezone.utc)
    ENSEMBLE_MEMBERS = [
        EnsembleMember(t0=START_00, dispatch_info="info1", member="0"),
        EnsembleMember(t0=START_00, dispatch_info="info1", member="1"),
        EnsembleMember(t0=START_00, dispatch_info="info2", member="0"),
        EnsembleMember(t0=START_00, dispatch_info="info2", member="1"),
        EnsembleMember(t0=START_12, dispatch_info="info1", member="0"),
        EnsembleMember(t0=START_12, dispatch_info="info1", member="1"),
        EnsembleMember(t0=START_12, dispatch_info="info2", member="0"),
        EnsembleMember(t0=START_12, dispatch_info="info2", member="1"),
    ]
    END_00 = datetime(year=2020, month=1, day=3, tzinfo=timezone.utc)
    END_12 = datetime(year=2020, month=1, day=3, hour=12, tzinfo=timezone.utc)
    TS_METADATA = TimeSeriesMetadata(path=TS_PATH)
    TS_ENSEMBLE_METADATA = TimeSeriesMetadata(path=ENSEMBLE_TS_PATH, is_forecast=True)
    WRITE_KWARGS: dict[str, Any] = {}

    async def test_01_create_time_series(self) -> None:
        multi_col_ts_metadata = model_copy(self.TS_ENSEMBLE_METADATA)
        multi_col_ts_metadata.columns = [
            TimeSeriesColumn(key="value", dtype="float32"),
            TimeSeriesColumn(key="value.1", dtype="float32"),
            TimeSeriesColumn(key="value.2", dtype="float32"),
        ]
        multi_col_ts_metadata.path = self.MULTI_COLUMN_TS_PATH
        empty_ts_metadata = model_copy(self.TS_METADATA)
        empty_ts_metadata.columns = [TimeSeriesColumn(key="value", dtype="float32")]
        empty_ts_metadata.path = self.EMPTY_TS_PATH
        async with self.STORE as client:
            ts = await client.create_time_series(self.TS_METADATA)
            self.TIME_SERIES_MAP[ts.path] = ts
            for ts in await client.create_time_series(
                [
                    self.TS_ENSEMBLE_METADATA,
                    multi_col_ts_metadata,
                    empty_ts_metadata,
                ]
            ):
                self.TIME_SERIES_MAP[ts.path] = ts

        async with self.STORE as client:
            index = pd.date_range(self.START_00, self.END_00, freq="5min", tz="utc")
            df = pd.DataFrame({"value": np.linspace(0, 100, index.shape[0])}, index=index)
            await client.write_data_frame({self.TS_PATH: df})
            df2 = await client.read_data_frame(self.TS_PATH)
            assert isinstance(df2.index, pd.DatetimeIndex)
            pd.testing.assert_frame_equal(df, df2, check_freq=False, check_index_type=False)
            write_map = {}
            for t0 in (self.START_00, self.START_12):
                end = self.END_00 if t0 == self.START_00 else self.END_12
                index = pd.date_range(t0, end, freq="5min", tz="utc")
                for info in ("info1", "info2"):
                    for member in ("0", "1"):
                        df = pd.DataFrame({"value": np.linspace(0, 100, index.shape[0])}, index=index)
                        write_map[
                            TimeSeriesKey(
                                path=self.ENSEMBLE_TS_PATH, t0=t0, dispatch_info=info, member=member
                            )
                        ] = df
                data_multi_col = np.linspace(0, 100, index.shape[0])
                multi_col_df = pd.DataFrame(
                    {
                        "value": data_multi_col,
                        "value.1": data_multi_col,
                        "value.2": data_multi_col,
                    },
                    index=index,
                )
                write_map[TimeSeriesKey(path=self.MULTI_COLUMN_TS_PATH, t0=t0)] = multi_col_df
            await client.write_data_frame(write_map)
            read_map = await client.read_data_frame(list(write_map.keys()))
            for key in write_map:
                assert isinstance(read_map[key].index, pd.DatetimeIndex)
                pd.testing.assert_frame_equal(
                    write_map[key], read_map[key], check_freq=False, check_index_type=False
                )

    async def test_02_read_bulk_mixed(self) -> None:
        start = datetime(year=2020, month=1, day=2, tzinfo=timezone.utc)
        end = datetime(year=2020, month=1, day=2, hour=12, tzinfo=timezone.utc)
        starts = [None, start, None, None]
        ends = [None, end, None, None]
        keys = [
            TimeSeriesKey(path=self.EMPTY_TS_PATH),
            TimeSeriesKey(path=self.TS_PATH),
            TimeSeriesKey(path=self.ENSEMBLE_TS_PATH, t0=self.START_12, dispatch_info="info1", member="0"),
            TimeSeriesKey(path=self.MULTI_COLUMN_TS_PATH, t0=self.START_12),
        ]
        async with self.STORE as client:
            data_frames = await client.read_data_frame(
                keys,
                start=starts,
                end=ends,
            )
        df_empty, df, df_ensemble, df_multi_column = [data_frames[k] for k in keys]
        assert df_empty.shape[0] == 0
        assert isinstance(df.index, pd.DatetimeIndex)
        assert isinstance(df_ensemble.index, pd.DatetimeIndex)
        assert isinstance(df_multi_column.index, pd.DatetimeIndex)
        assert start.isoformat() == df.index[0].isoformat()
        assert end.isoformat() == df.index[-1].isoformat()
        assert self.START_12.isoformat() == df_ensemble.index[0].isoformat()
        assert self.END_12.isoformat() == df_ensemble.index[-1].isoformat()
        assert self.START_12.isoformat() == df_multi_column.index[0].isoformat()
        assert self.END_12.isoformat() == df_multi_column.index[-1].isoformat()
        assert "value" in df_multi_column.columns
        assert "value.1" in df_multi_column.columns
        assert "value.2" in df_multi_column.columns

    async def test_03_write_bulk_mixed(self) -> None:
        start = datetime(year=2020, month=1, day=2, tzinfo=timezone.utc)
        end = datetime(year=2020, month=1, day=2, hour=12, tzinfo=timezone.utc)
        keys = [
            TimeSeriesKey(path=self.EMPTY_TS_PATH),
            TimeSeriesKey(path=self.TS_PATH),
            TimeSeriesKey(path=self.ENSEMBLE_TS_PATH, t0=self.START_12, dispatch_info="info1", member="0"),
            TimeSeriesKey(path=self.MULTI_COLUMN_TS_PATH, t0=self.START_12),
        ]
        async with self.STORE as client:
            data_frames = await client.read_data_frame(keys, start=start, end=end)
        df_empty, df, df_ensemble, df_multi_column = [data_frames[k] for k in keys]
        with pytest.raises(ValueError):
            df_empty.loc[:, "value"] = 22.0
        df.loc[:, "value"] = 25.0
        df_ensemble.loc[:, "value"] = 27.0
        df_multi_column.loc[:, "value"] = 0.0
        df_multi_column.loc[:, "value.1"] = 1.0
        df_multi_column.loc[:, "value.2"] = 2.0
        async with self.STORE as client:
            await client.write_data_frame(data_frames)
        async with self.STORE as client:
            data_frames = await client.read_data_frame(keys, start=start, end=end)
        df_empty, df, df_ensemble, df_multi_column = [data_frames[k] for k in keys]
        assert df_empty.shape[0] == 0
        assert (df["value"] == 25.0).all()
        assert (df_ensemble["value"] == 27.0).all()
        assert (df_multi_column["value"] == 0.0).all()
        assert (df_multi_column["value.1"] == 1.0).all()
        assert (df_multi_column["value.2"] == 2.0).all()

    async def test_05_read_missing_ensemble_with_scalar(self) -> None:
        keys = [
            TimeSeriesKey(
                path=self.ENSEMBLE_TS_PATH, t0=datetime(year=2018, month=1, day=1, tzinfo=timezone.utc)
            ),
            TimeSeriesKey(path=self.TS_PATH),
        ]
        async with self.STORE as client:
            data_frames = await client.read_data_frame(keys)
        missing_df, scalar_df = [data_frames[k] for k in keys]
        assert missing_df.shape[0] == 0
        assert scalar_df.shape[0] != 0

    async def test_06_partial_reads(self) -> None:
        key = TimeSeriesKey(path=self.MULTI_COLUMN_TS_PATH, t0=self.START_12)
        async with self.STORE as client:
            df_1 = await client.read_data_frame(key, columns=["value.1"])
            df_1_2 = await client.read_data_frame(key, columns=["value.1", "value.2"])
            assert df_1.columns == ["value.1"]
            assert all(df_1_2.columns == ["value.1", "value.2"])
            pd.testing.assert_frame_equal(df_1, df_1_2.loc[:, ["value.1"]], check_freq=False)

    async def test_07_reads_outside_coverage(self) -> None:
        key = TimeSeriesKey(path=self.MULTI_COLUMN_TS_PATH, t0=self.START_12)
        async with self.STORE as client:
            df_1 = (await client.read_data_frame([key], start=self.END_12 + timedelta(days=1)))[key]
            df_1_2 = (
                await client.read_data_frame(
                    [key], start=self.END_12 + timedelta(days=1), end=self.END_12 + timedelta(days=2)
                )
            )[key]
        assert df_1.shape[0] == 0
        assert df_1_2.shape[0] == 0

    async def test_08_partial_writes(self) -> None:
        ts_path = f"{str(uuid.uuid4())}"
        metadata = model_copy(self.TS_METADATA)
        metadata.path = ts_path
        metadata.columns = [
            TimeSeriesColumn(key="value", dtype="float32"),
            TimeSeriesColumn(key="quality", dtype="uint8"),
        ]
        async with self.STORE as client:
            await client.create_time_series(metadata)
            index = pd.date_range("2020-01-01", "2020-03-01", freq="5min", tz="utc")
            df = pd.DataFrame(
                {
                    "value": np.linspace(0, 100, index.shape[0]),
                    "quality": [100] * index.shape[0],
                },
                index=index,
            )
            await client.write_data_frame({ts_path: df}, **self.WRITE_KWARGS)
            df = pd.DataFrame({"quality": [200] * index.shape[0]}, index=index)
            await client.write_data_frame({ts_path: df}, **self.WRITE_KWARGS)
            read_df = await client.read_data_frame(ts_path)
            assert np.allclose(df["quality"].values, read_df["quality"].values)  # type:ignore
            await client.delete_time_series([ts_path])

    async def test_09_utility_queries(self) -> None:
        async with self.STORE as client:
            ts_list = await client.read_time_series(ts_filters=["*"])
            assert len(ts_list) == 4
            ensembles = await client.read_ensemble_members(self.ENSEMBLE_TS_PATH, t0_end=self.START_00)
            assert len(ensembles) == 4

    async def test_10_utility_bulk_queries(self) -> None:
        async with self.STORE as client:
            ts_list = await client.read_time_series(
                paths=[self.TS_PATH],
                ts_filters=[f"{self.ENSEMBLE_TS_PATH[:-2]}*", "fake_path*"],
            )
            assert len(ts_list) == 2
            ensemble_map = await client.read_ensemble_members(
                paths=[self.ENSEMBLE_TS_PATH, self.MULTI_COLUMN_TS_PATH],
                t0_end=self.START_00,
            )
            assert len(ensemble_map) == 2
            # Following type ignores are to test that str indexing works
            assert len(ensemble_map[self.ENSEMBLE_TS_PATH]) == 4  # type: ignore
            assert len(ensemble_map[self.MULTI_COLUMN_TS_PATH]) == 1  # type: ignore
            keys = [
                TimeSeriesKey(path=self.TS_PATH),
                TimeSeriesKey(path=self.MULTI_COLUMN_TS_PATH, t0=self.START_00),
                TimeSeriesKey(path=self.ENSEMBLE_TS_PATH, **model_dump(self.ENSEMBLE_MEMBERS[0])),
            ]
            coverages = await client.read_coverage(keys)
            assert len(coverages) == 3

    async def test_11_delete_data(self) -> None:
        async with self.STORE as client:
            start = datetime(year=2020, month=1, day=2, tzinfo=timezone.utc)
            await client.delete_data_range([self.TS_PATH], start=start, end=self.END_00)
            df = await client.read_data_frame(self.TS_PATH)
            assert df.index[0] == self.START_00
            assert df.index[-1] == datetime(
                year=2020, month=1, day=1, hour=23, minute=55, tzinfo=timezone.utc
            )

    async def test_12_delete_data_range_bulk(self) -> None:
        starts = [None, self.START_12]
        ends = [None, self.END_12]
        keys = [
            TimeSeriesKey(path=self.ENSEMBLE_TS_PATH, t0=self.START_12, dispatch_info="info1", member="0"),
            TimeSeriesKey(path=self.MULTI_COLUMN_TS_PATH, t0=self.START_12),
        ]
        async with self.STORE as client:
            data_frames = await client.read_data_frame(keys, start=starts, end=ends)
            assert all(not df.empty for df in data_frames.values())
            await client.delete_data_range(keys, start=starts, end=ends, error_handling="raise")
            data_frames = await client.read_data_frame(keys, start=starts, end=ends)
            assert all(df.empty for df in data_frames.values())

    async def test_13_delete_time_series(self) -> None:
        async with self.STORE as client:
            await client.delete_time_series(
                [self.TS_PATH, self.ENSEMBLE_TS_PATH, self.MULTI_COLUMN_TS_PATH, self.EMPTY_TS_PATH],
            )
            ts_list = await client.read_time_series(ts_filters=["*"])
            assert len(ts_list) == 0
