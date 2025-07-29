from importlib.metadata import version

from .exceptions import (
    TimeSeriesEnsembleMemberNotFoundError,
    TimeSeriesException,
    TimeSeriesNotFoundError,
    TimeSeriesUserError,
)
from .schema import (
    COMMENT_COLUMN_KEY,
    DEFAULT_COMMENT_COLUMN,
    DEFAULT_QUALITY_COLUMN,
    DEFAULT_TIME_SERIES_COLUMNS,
    DEFAULT_VALUE_COLUMN,
    QUALITY_COLUMN_KEY,
    VALUE_COLUMN_KEY,
    CommentSupport,
    EnsembleComponent,
    EnsembleMember,
    TimeSeriesColumn,
    TimeSeriesComment,
    TimeSeriesKey,
    TimeSeriesMetadata,
)
from .time_series import TimeSeries
from .time_series_client import TimeSeriesClient, TimeSeriesClientHelper
from .time_series_store import TimeSeriesStore

__all__ = [
    "CommentSupport",
    "EnsembleComponent",
    "EnsembleMember",
    "TimeSeriesException",
    "TimeSeriesUserError",
    "TimeSeriesNotFoundError",
    "TimeSeriesEnsembleMemberNotFoundError",
    "TimeSeriesMetadata",
    "TimeSeries",
    "TimeSeriesComment",
    "TimeSeriesColumn",
    "TimeSeriesClient",
    "TimeSeriesClientHelper",
    "TimeSeriesKey",
    "TimeSeriesStore",
    "DEFAULT_VALUE_COLUMN",
    "DEFAULT_COMMENT_COLUMN",
    "DEFAULT_QUALITY_COLUMN",
    "DEFAULT_TIME_SERIES_COLUMNS",
    "VALUE_COLUMN_KEY",
    "QUALITY_COLUMN_KEY",
    "COMMENT_COLUMN_KEY",
]

try:
    __version__ = version("kisters.water.time_series")
except ImportError:
    __version__ = "unknown"
