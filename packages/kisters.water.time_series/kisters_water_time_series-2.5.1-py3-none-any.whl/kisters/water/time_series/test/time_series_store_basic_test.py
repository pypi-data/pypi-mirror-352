from __future__ import annotations

import itertools
import uuid
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
import pytest

from kisters.water.time_series.core import EnsembleMember, TimeSeries, TimeSeriesStore
from kisters.water.time_series.core.schema import TimeSeriesKey
from kisters.water.time_series.core.utils import model_dump


class TimeSeriesStoreBasicTest:
    STORE: TimeSeriesStore
    TS_PATH = f"{str(uuid.uuid4())}"
    TIME_SERIES_MAP: dict[str, TimeSeries | None] = {}
    TS_METADATA: dict[str, Any] = {}
    ENSEMBLE_TS_PATH = f"{str(uuid.uuid4())}"
    ENSEMBLE_MEMBERS = [
        EnsembleMember(
            t0=datetime(year=2020, month=1, day=1, tzinfo=timezone.utc),
            dispatch_info="info1",
            member="0",
        ),
        EnsembleMember(
            t0=datetime(year=2020, month=1, day=1, tzinfo=timezone.utc),
            dispatch_info="info1",
            member="1",
        ),
        EnsembleMember(
            t0=datetime(year=2020, month=1, day=1, tzinfo=timezone.utc),
            dispatch_info="info2",
            member="0",
        ),
        EnsembleMember(
            t0=datetime(year=2020, month=1, day=1, tzinfo=timezone.utc),
            dispatch_info="info2",
            member="1",
        ),
        EnsembleMember(
            t0=datetime(year=2020, month=1, day=1, hour=12, tzinfo=timezone.utc),
            dispatch_info="info1",
            member="0",
        ),
        EnsembleMember(
            t0=datetime(year=2020, month=1, day=1, hour=12, tzinfo=timezone.utc),
            dispatch_info="info1",
            member="1",
        ),
        EnsembleMember(
            t0=datetime(year=2020, month=1, day=1, hour=12, tzinfo=timezone.utc),
            dispatch_info="info2",
            member="0",
        ),
        EnsembleMember(
            t0=datetime(year=2020, month=1, day=1, hour=12, tzinfo=timezone.utc),
            dispatch_info="info2",
            member="1",
        ),
    ]
    TS_ENSEMBLE_METADATA = {"is_forecast": True}
    WRITE_KWARGS: dict[str, Any] = {}

    @pytest.mark.parametrize("path", [TS_PATH, ENSEMBLE_TS_PATH])
    def test_01_create_time_series(self, path: str) -> None:
        metadata = self.TS_METADATA if path == self.TS_PATH else self.TS_ENSEMBLE_METADATA
        ts = self.STORE.create_time_series(path=path, metadata=metadata)
        self.TIME_SERIES_MAP[path] = ts
        assert ts is not None
        assert ts.path in path
        assert ts.metadata is not None
        assert ts.columns is not None

    @pytest.mark.parametrize("path", [TS_PATH, ENSEMBLE_TS_PATH])
    def test_02_get_by_path(self, path: str) -> None:
        ts = self.STORE.get_by_path(path)
        assert isinstance(ts, TimeSeries)
        mapped_ts = self.TIME_SERIES_MAP[path]
        assert mapped_ts
        assert ts.path == mapped_ts.path
        assert ts.metadata == mapped_ts.metadata
        assert ts.columns == mapped_ts.columns

    def test_03_get_by_path_multiple(self) -> None:
        ts_path = f"{str(uuid.uuid4())}"
        ts_path2 = f"{ts_path}/sub"
        self.STORE.create_time_series(path=ts_path, metadata=self.TS_METADATA)
        self.STORE.create_time_series(path=ts_path2, metadata=self.TS_METADATA)
        paths = [self.TS_PATH, ts_path, ts_path2]
        ts_list = self.STORE.get_by_path(*paths)
        assert not isinstance(ts_list, TimeSeries)
        retrieved_paths = {ts.path for ts in ts_list}
        assert set(paths) == retrieved_paths

    def test_04_filter_time_series(self) -> None:
        ts_list = list(self.STORE.get_by_filter(self.TS_PATH))
        assert len(ts_list) == 1
        assert ts_list[0].path == self.TS_PATH
        ts_list = list(self.STORE.get_by_filter("*"))
        assert len(ts_list) == 4
        ts_list = list(self.STORE.get_by_filter(self.TS_PATH, "*"))
        assert len(ts_list) == 5

    def test_05_update_ts_metadata(self) -> None:
        ts = self.TIME_SERIES_MAP[self.TS_PATH]
        assert ts
        metadata = ts.metadata
        metadata["attr1"] = 1234
        metadata["attr2"] = "value"
        metadata["attr3"] = True
        metadata["attr4"] = 288.5
        ts.update_metadata(metadata)
        assert ts.metadata["attr1"] == 1234
        assert ts.metadata["attr2"] == "value"
        assert ts.metadata["attr3"]
        assert ts.metadata["attr4"] == 288.5

    def test_06_delete_ts_metadata(self) -> None:
        ts = self.TIME_SERIES_MAP[self.TS_PATH]
        assert ts
        assert "attr1" in ts.metadata
        assert "attr2" in ts.metadata
        assert "attr3" in ts.metadata
        assert "attr4" in ts.metadata
        metadata = ts.metadata
        del metadata["attr1"]
        del metadata["attr2"]
        del metadata["attr3"]
        del metadata["attr4"]
        ts.update_metadata(metadata)
        assert "attr1" not in ts.metadata
        assert "attr2" not in ts.metadata
        assert "attr3" not in ts.metadata
        assert "attr4" not in ts.metadata

    def test_07_write_data_frame(self) -> None:
        index = pd.date_range("2020-01-01", "2020-03-01", freq="5min", tz="utc")
        df = pd.DataFrame({"value": np.linspace(0, 100, index.shape[0])}, index=index)
        ts = self.TIME_SERIES_MAP[self.TS_PATH]
        assert ts
        ts.write_data_frame(data_frame=df, **self.WRITE_KWARGS)
        read_df = ts.read_data_frame()
        assert np.allclose(df.values, read_df.loc[:, ["value"]].values)

    def test_08_read_coverage(self) -> None:
        ts = self.TIME_SERIES_MAP[self.TS_PATH]
        assert ts
        coverage = ts.coverage()
        coverage_from = ts.coverage_from()
        coverage_until = ts.coverage_until()
        date_from = datetime(year=2020, month=1, day=1, tzinfo=timezone.utc)
        date_until = datetime(year=2020, month=3, day=1, tzinfo=timezone.utc)
        assert coverage[0] == date_from == coverage_from
        assert coverage[1] == date_until == coverage_until

    def test_09_read_data_frame(self) -> None:
        start = pd.to_datetime("2020-02-01", utc=True)
        end = pd.to_datetime("2020-02-15", utc=True)
        ts = self.TIME_SERIES_MAP[self.TS_PATH]
        assert ts
        df = ts.read_data_frame(start=start, end=end)
        assert df.index[0] == start
        assert df.index[-1] == end

    def test_10_bulk_write(self) -> None:
        ts_list = [self.TIME_SERIES_MAP[self.ENSEMBLE_TS_PATH]] * len(self.ENSEMBLE_MEMBERS)
        t0s, dispatch_infos, members = [], [], []
        for ensemble in self.ENSEMBLE_MEMBERS:
            t0s.append(ensemble.t0)
            dispatch_infos.append(ensemble.dispatch_info)
            members.append(ensemble.member)
        paths = [self.ENSEMBLE_TS_PATH] * len(self.ENSEMBLE_MEMBERS)
        index = pd.date_range("2020-03-01", "2020-04-01", freq="5min", tz="utc")
        df = pd.DataFrame({"value": np.linspace(0, 100, index.shape[0])}, index=index)
        data_frames = {
            TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member): df
            for path, t0, dispatch_info, member, df in zip(
                paths, t0s, dispatch_infos, members, itertools.repeat(df)
            )
        }
        self.STORE.write_data_frames(data_frames, **self.WRITE_KWARGS)
        ts = ts_list[0]
        assert ts
        for ensemble in self.ENSEMBLE_MEMBERS:
            assert ts.coverage_until(**model_dump(ensemble)) == index[-1].to_pydatetime()

    def test_11_bulk_read(self) -> None:
        paths = [self.TS_PATH] + [self.ENSEMBLE_TS_PATH] * len(self.ENSEMBLE_MEMBERS)
        t0s: list[datetime | None] = [None]
        dispatch_infos: list[str | None] = [None]
        members: list[str | None] = [None]
        start = datetime(year=2020, month=2, day=1, tzinfo=timezone.utc)
        end = datetime(year=2020, month=3, day=15, tzinfo=timezone.utc)
        for ensemble in self.ENSEMBLE_MEMBERS:
            t0s.append(ensemble.t0)
            dispatch_infos.append(ensemble.dispatch_info)
            members.append(ensemble.member)
        bulk_map = self.STORE.read_data_frames(
            (
                TimeSeriesKey(path=path, t0=t0, dispatch_info=dispatch_info, member=member)
                for path, t0, dispatch_info, member in zip(paths, t0s, dispatch_infos, members)
            ),
            start=start,
            end=end,
        )
        for df in bulk_map.values():
            assert df.loc[df.index < start].shape[0] == 0
            assert df.loc[df.index > end].shape[0] == 0

    def test_12_read_ensembles(self) -> None:
        ts = self.TIME_SERIES_MAP[self.ENSEMBLE_TS_PATH]
        assert ts
        start_00 = datetime(year=2020, month=1, day=1, tzinfo=timezone.utc)
        start_12 = datetime(year=2020, month=1, day=1, hour=12, tzinfo=timezone.utc)
        ensembles = list(ts.ensemble_members())
        assert len(ensembles) == 8
        for i in range(len(ensembles)):
            date = start_00 if i // 4 % 2 == 0 else start_12
            ensemble = ensembles[i]
            assert ensemble.t0
            assert ensemble.t0.isoformat() == date.isoformat()
            info = "info1" if i // 2 % 2 == 0 else "info2"
            assert ensemble.dispatch_info == info
            member = "0" if i % 2 == 0 else "1"
            assert ensemble.member == member

    def test_13_filter_ensembles(self) -> None:
        ts = self.TIME_SERIES_MAP[self.ENSEMBLE_TS_PATH]
        assert ts
        start_00 = datetime(year=2020, month=1, day=1, tzinfo=timezone.utc)
        ensembles = list(ts.ensemble_members(t0_start=start_00, t0_end=start_00))
        assert len(ensembles) == 4
        for i in range(len(ensembles)):
            ensemble = ensembles[i]
            assert ensemble.t0
            assert ensemble.t0.isoformat() == start_00.isoformat()
            info = "info1" if i // 2 % 2 == 0 else "info2"
            assert ensemble.dispatch_info == info
            member = "0" if i % 2 == 0 else "1"
            assert ensemble.member == member

    def test_14_delete_time_series(self) -> None:
        for ts in self.STORE.get_by_filter("*"):
            self.STORE.delete_time_series(path=ts.path)
        assert len(list(self.STORE.get_by_filter("*"))) == 0
