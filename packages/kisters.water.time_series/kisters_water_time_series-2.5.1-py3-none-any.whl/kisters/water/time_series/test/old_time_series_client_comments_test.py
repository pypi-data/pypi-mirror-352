from __future__ import annotations

import uuid
import warnings
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from kisters.water.time_series.core import (
    TimeSeries,
    TimeSeriesComment,
    TimeSeriesMetadata,
    TimeSeriesStore,
)
from kisters.water.time_series.core.time_series_client import OldTimeSeriesClient


class SuppressedDeprecationStore(TimeSeriesStore):
    @property
    def client(self) -> OldTimeSeriesClient:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return super().client


class OldTimeSeriesClientCommentsTest:
    STORE: TimeSeriesStore
    TS_PATH = str(uuid.uuid4())
    TIME_SERIES_MAP: dict[str, TimeSeries] = {}
    START_00 = datetime(year=2020, month=1, day=1, tzinfo=timezone.utc)
    MID_DAY_1 = datetime(year=2020, month=1, day=1, hour=12, tzinfo=timezone.utc)
    MID_DAY_2 = datetime(year=2020, month=1, day=2, hour=12, tzinfo=timezone.utc)
    END_00 = datetime(year=2020, month=1, day=3, tzinfo=timezone.utc)
    TS_METADATA = TimeSeriesMetadata(path=TS_PATH)
    WRITE_KWARGS: dict[str, Any] = {}

    async def test_01_create_time_series(self) -> None:
        self.STORE.__class__ = SuppressedDeprecationStore
        async with self.STORE.client as client:
            await client.create_time_series(path=self.TS_PATH, metadata=self.TS_METADATA)
            index = pd.date_range(self.START_00, self.END_00, freq="5min", tz="utc")
            df = pd.DataFrame({"value": np.linspace(0, 100, index.shape[0])}, index=index)
            await client.write_data_frame(path=self.TS_PATH, data_frame=df)
            assert (await client.read_time_series(path=self.TS_PATH)) is not None

    async def test_02_write_comments(self) -> None:
        async with self.STORE.client as client:
            await client.write_comments(
                path=self.TS_PATH,
                comments=[
                    TimeSeriesComment(comment="comment1", start=self.START_00, end=self.MID_DAY_1),
                    TimeSeriesComment(comment="comment2", start=self.MID_DAY_2, end=self.END_00),
                ],
            )
            comments = [c async for c in client.read_comments(path=self.TS_PATH)]
            assert len(comments) == 2

    async def test_03_read_comments(self) -> None:
        async with self.STORE.client as client:
            first_comment = [
                c
                async for c in client.read_comments(
                    path=self.TS_PATH, start=self.START_00, end=self.MID_DAY_1
                )
            ]

            assert len(first_comment) == 1
            second_comment = [
                c
                async for c in client.read_comments(
                    path=self.TS_PATH, start=self.MID_DAY_2, end=self.END_00
                )
            ]
            assert len(second_comment) == 1
            both_comments = [
                c
                async for c in client.read_comments(
                    path=self.TS_PATH, start=self.MID_DAY_1, end=self.MID_DAY_2
                )
            ]
            assert len(both_comments) == 2

    async def test_04_delete_comments(self) -> None:
        async with self.STORE.client as client:
            await client.delete_comments(
                path=self.TS_PATH,
                comments=[c async for c in client.read_comments(path=self.TS_PATH)],
            )
            comments = [c async for c in client.read_comments(path=self.TS_PATH)]
            assert len(comments) == 0
            await client.delete_time_series(path=self.TS_PATH)
