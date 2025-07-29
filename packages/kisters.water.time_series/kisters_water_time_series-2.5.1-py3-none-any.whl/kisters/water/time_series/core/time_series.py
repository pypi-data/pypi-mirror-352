from __future__ import annotations

import datetime
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

import pandas as pd

from .schema import (
    CommentSupport,
    EnsembleMember,
    TimeSeriesColumn,
    TimeSeriesComment,
    TimeSeriesKey,
    TimeSeriesMetadata,
)
from .utils import model_dump, model_validate

if TYPE_CHECKING:
    from .time_series_client import TimeSeriesClient


class TimeSeries:
    """This class provides the interface of TimeSeries."""

    def __init__(self, client: TimeSeriesClient, metadata: dict[str, Any] | TimeSeriesMetadata):
        if isinstance(metadata, TimeSeriesMetadata):
            self._metadata = metadata
        else:
            self._metadata = model_validate(TimeSeriesMetadata, metadata)
        self._client = client
        self._coverages: dict[
            EnsembleMember, tuple[datetime.datetime | None, datetime.datetime | None]
        ] = {}
        self._tzinfo: datetime.tzinfo | None = None

    def __str__(self) -> str:
        """Return the string representations for the TimeSeries."""
        return self.path

    def __repr__(self, *args: Any, **kwargs: Any) -> str:
        return f"{self.__class__.__name__} {self.path}"

    @property
    def path(self) -> str:
        return self._metadata.path

    @property
    def metadata(self) -> dict[str, Any]:
        """
        The metadata dictionary.

        Returns:
            A dict object holding the TimeSeries metadata.
        """
        return model_dump(self._metadata, by_alias=True)

    @property
    def tzinfo(self) -> datetime.tzinfo | None:
        if not self._tzinfo:
            try:
                self._tzinfo = ZoneInfo(self._metadata.timezone)
            except Exception:
                self._tzinfo = datetime.timezone.utc
        return self._tzinfo

    @property
    def columns(self) -> Sequence[TimeSeriesColumn]:
        return self._metadata.columns

    def update_metadata(self, metadata: dict[str, Any] | TimeSeriesMetadata) -> None:
        """
        Update the time series metadata in the backend.
        """
        self._client.run_sync(self._client.update_time_series, metadata, error_handling="raise")
        self._metadata = self._client.run_sync(
            self._client.read_time_series, paths=self.path, error_handling="raise"
        )._metadata

    @property
    def supports_comments(self) -> CommentSupport:
        return self._client.comment_support

    def coverage_from(
        self,
        *,
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
    ) -> datetime.datetime | None:
        """
        Get the coverage from which the TimeSeries data starts.

        Args:
            Only needed for ensemble TimeSeries.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier.

        Returns:
            The datetime.
        """
        return self.coverage(t0=t0, dispatch_info=dispatch_info, member=member)[0]

    def coverage_until(
        self,
        *,
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
    ) -> datetime.datetime | None:
        """
        Get the coverage until which the TimeSeries data covers.

        Args:
            Only needed for ensemble TimeSeries.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier.

        Returns:
            The datetime.
        """
        return self.coverage(t0=t0, dispatch_info=dispatch_info, member=member)[1]

    def coverage(
        self,
        *,
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
    ) -> tuple[datetime.datetime | None, datetime.datetime | None]:
        """
        Get the time series data coverage.

        Args:
            Only needed for ensemble TimeSeries.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier.

        Returns:
            The datetime.
        """
        key = TimeSeriesKey(path=self.path, t0=t0, dispatch_info=dispatch_info, member=member)
        tuple_key = EnsembleMember(t0=t0, dispatch_info=dispatch_info, member=member)
        if tuple_key not in self._coverages:
            self._coverages[tuple_key] = self._client.run_sync(
                self._client.read_coverage, key, error_handling="raise"
            )
        return self._coverages[tuple_key]

    def ensemble_members(
        self,
        *,
        t0_start: datetime.datetime | None = None,
        t0_end: datetime.datetime | None = None,
        **kwargs: Any,
    ) -> list[EnsembleMember]:
        """
        Returns a list of ensemble members.

        Args:
            t0_start: The starting date from which to look for ensembles.
            t0_end: The ending date until which to look for ensembles.
            **kwargs: Additional backend specific keyword arguments.

        Returns:
            A list of EnsembleMember objects.
        """
        return self._client.run_sync(
            self._client.read_ensemble_members,
            self.path,
            t0_start=t0_start,
            t0_end=t0_end,
            error_handling="raise",
            **kwargs,
        )

    def _localize_datetime(self, dt: datetime.datetime | None) -> datetime.datetime | None:
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt
        return dt.replace(tzinfo=self.tzinfo)

    def read_data_frame(
        self,
        *,
        start: datetime.datetime | None = None,
        end: datetime.datetime | None = None,
        columns: list[str] | None = None,
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        This method returns the TimeSeries data between the start and end dates (both dates included)
        structured as a pandas DataFrame, the DataFrame index is localized in the TimeSeries timezone.

        Args:
            start: The starting date from which the data will be returned, if it doesn't have tzinfo,
                it assumes the timezone of the TimeSeries.
            end: The ending date until which the data will be covered (end date included),
                if it doesn't have tzinfo, it assumes the timezone of the TimeSeries.
            columns: The list of column keys to read.
            t0: The t0 timestamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier.
            **kwargs: Additional backend specific keyword arguments.

        Returns:
            The DataFrame containing the TimeSeries data
        """
        start, end = self._localize_datetime(start), self._localize_datetime(end)
        ts_key = TimeSeriesKey(path=self.path, t0=t0, dispatch_info=dispatch_info, member=member)
        return self._client.run_sync(
            self._client.read_data_frame,
            ts_key,
            start=start,
            end=end,
            columns=columns,
            error_handling="raise",
            **kwargs,
        )

    def write_data_frame(
        self,
        *,
        data_frame: pd.DataFrame,
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        This method writes the data from the data_frame into this time series.

        Args:
            data_frame: The TimeSeries data to be written in the form of a pandas DataFrame.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier
            **kwargs: Additional backend specific keyword arguments.
        """
        assert isinstance(data_frame.index, pd.DatetimeIndex)
        if data_frame.index.tz is None:
            data_frame.index = data_frame.index.tz_localize(self.tzinfo)
        ts_key = TimeSeriesKey(path=self.path, t0=t0, dispatch_info=dispatch_info, member=member)
        self._client.run_sync(
            self._client.write_data_frame,
            {ts_key: data_frame},
            error_handling="raise",
            **kwargs,
        )

    def delete_data_range(
        self,
        *,
        start: datetime.datetime | None = None,
        end: datetime.datetime | None = None,
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        This method deletes a range of data and/or an ensemble member from a time series.

        Args:
            start: The starting date from which the data will be returned, if it doesn't have tzinfo,
                it assumes the timezone of the TimeSeries.
            end: The ending date until which the data will be covered (end date included),
                if it doesn't have tzinfo, it assumes the timezone of the TimeSeries.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier
            **kwargs: Additional backend specific keyword arguments.
        """
        start, end = self._localize_datetime(start), self._localize_datetime(end)
        ts_key = TimeSeriesKey(path=self.path, t0=t0, dispatch_info=dispatch_info, member=member)
        self._client.run_sync(
            self._client.delete_data_range,
            ts_key,
            start=start,
            end=end,
            error_handling="raise",
            **kwargs,
        )

    def read_comments(
        self,
        *,
        start: datetime.datetime | None = None,
        end: datetime.datetime | None = None,
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> list[TimeSeriesComment]:
        """
        Read the time series comments.

        Args:
            start: The datetime from which to retrieve comments.
            end: The datetime until which to retrieve comments.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier
            **kwargs: Additional backend specific keyword arguments.

        Returns:
            An iterable of TimeSeriesComment objects.
        """
        ts_key = TimeSeriesKey(path=self.path, t0=t0, dispatch_info=dispatch_info, member=member)
        return self._client.run_sync(
            self._client.read_comments,
            ts_key,
            start=start,
            end=end,
            error_handling="raise",
            **kwargs,
        )

    def write_comments(
        self,
        *,
        comments: list[TimeSeriesComment],
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Write a list of time series comments.

        Args:
            comments: The list of time series comments.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier
            **kwargs: Additional backend specific keyword arguments.
        """
        ts_key = TimeSeriesKey(path=self.path, t0=t0, dispatch_info=dispatch_info, member=member)
        self._client.run_sync(
            self._client.write_comments,
            {ts_key: comments},
            error_handling="raise",
            **kwargs,
        )

    def delete_comments(
        self,
        *,
        comments: list[TimeSeriesComment] | None = None,
        t0: datetime.datetime | None = None,
        dispatch_info: str | None = None,
        member: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Delete time series comments.

        Args:
            comments: The time series comments to delete.
            t0: The t0 timestamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier
            **kwargs: Additional backend specific keyword arguments.
        """
        ts_key = TimeSeriesKey(path=self.path, t0=t0, dispatch_info=dispatch_info, member=member)
        self._client.run_sync(
            self._client.delete_comments,
            {ts_key: comments},
            error_handling="raise",
            **kwargs,
        )
