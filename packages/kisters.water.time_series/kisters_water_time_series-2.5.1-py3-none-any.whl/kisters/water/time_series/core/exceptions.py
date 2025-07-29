from __future__ import annotations

from datetime import datetime

from .schema import TimeSeriesKey


class TimeSeriesException(Exception):
    def __init__(self, message: str, path: str | TimeSeriesKey | None):
        super().__init__(message)
        self.ts_key: TimeSeriesKey | None
        self.path: str | None
        if isinstance(path, TimeSeriesKey):
            self.ts_key = path
            self.path = path.path
        elif isinstance(path, str):
            self.ts_key = TimeSeriesKey(path=path, member=None, t0=None, dispatch_info=None)
            self.path = path
        else:
            self.ts_key = None
            self.path = None


class TimeSeriesNotFoundError(TimeSeriesException):
    """Exception raised when accessing non-existent time series."""

    def __init__(self, path: str | TimeSeriesKey):
        super().__init__(f"Time series not found with path {path}", path)


class TimeSeriesEnsembleMemberNotFoundError(TimeSeriesException):
    """Exception raised when accessing non-existent ensemble members of a forecast time series."""

    def __init__(
        self,
        ts_key: TimeSeriesKey | str,
        t0: datetime | None = None,
        member: str | None = None,
        dispatch_info: str | None = None,
    ):
        if isinstance(ts_key, str):
            ts_key = TimeSeriesKey(path=ts_key, t0=t0, dispatch_info=dispatch_info, member=member)
        super().__init__(f"Time series ensemble member not found {ts_key}", ts_key)
        self.t0 = ts_key.t0
        self.member = ts_key
        self.dispatch_info = ts_key.dispatch_info


class TimeSeriesUserError(TimeSeriesException):
    """This exception is raised when the user provides invalid data or arguments"""
