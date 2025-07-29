from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from enum import Enum, Flag, auto
from typing import Any, Optional

import numpy as np
from typing_extensions import Self

from .utils import (
    AllowExtraModel,
    ArbitraryExtraModel,
    Field,
    Model,
    field_validator,
    model_dump,
    model_validate,
)


class TimeSeriesColumn(AllowExtraModel):
    key: str
    dtype: str

    @field_validator("dtype", mode="before")
    def check_dtype(cls, value: Any) -> str:
        return str(np.dtype(value))


# Column conventions
VALUE_COLUMN_KEY = "value"
QUALITY_COLUMN_KEY = "quality"
COMMENT_COLUMN_KEY = "comment"

DEFAULT_VALUE_COLUMN = TimeSeriesColumn(key=VALUE_COLUMN_KEY, dtype="float32")
DEFAULT_QUALITY_COLUMN = TimeSeriesColumn(key=QUALITY_COLUMN_KEY, dtype="uint8")
DEFAULT_COMMENT_COLUMN = TimeSeriesColumn(key=COMMENT_COLUMN_KEY, dtype="str")

DEFAULT_TIME_SERIES_COLUMNS = [DEFAULT_VALUE_COLUMN]


class EnsembleMember(Model):
    t0: Optional[datetime] = None
    dispatch_info: Optional[str] = None
    member: Optional[str] = None

    @field_validator("t0", mode="before")
    @classmethod
    def check_t0(cls, value: Any) -> Any:
        if isinstance(value, np.datetime64):
            return value.astype("datetime64[ms]").astype(object).replace(tzinfo=timezone.utc)
        return value

    def __bool__(self) -> bool:
        return self.t0 is not None or self.member is not None or self.dispatch_info is not None

    def __str__(self) -> str:
        return f"{self.t0.isoformat() if self.t0 else self.t0}:{self.dispatch_info}:{self.member}"

    def __hash__(self) -> int:
        return hash(str(self))

    def copy_with(
        self,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
    ) -> Self:
        self_obj = model_dump(self, exclude_none=True)
        if t0 is not None:
            self_obj["t0"] = t0
        if dispatch_info is not None:
            self_obj["dispatch_info"] = dispatch_info
        if member is not None:
            self_obj["member"] = member
        return model_validate(self, self_obj)


class TimeSeriesKey(EnsembleMember):
    path: str

    def __bool__(self) -> bool:
        """Do not use the bool from EnsembleMember"""
        return bool(self.path)

    def is_ensemble(self) -> bool:
        """Explicit method for EnsembleMember bool"""
        return super().__bool__()

    def __str__(self) -> str:
        # With no ensemble information this makes the hash equivalent to the path
        if self.t0 is None and self.dispatch_info is None and self.member is None:
            return self.path
        return f"{self.path}:{super().__str__()}"

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TimeSeriesKey):
            return str(self) == str(other)
        if isinstance(other, str):
            return str(self) == other
        return False

    def __repr__(self) -> str:
        args = [f"path='{self.path}'"]
        if self.t0:
            args.append(f"t0='{self.t0.isoformat()}'")
        if self.dispatch_info:
            args.append(f"dispatch_info='{self.dispatch_info}'")
        if self.member:
            args.append(f"member='{self.member}'")
        return f"TimeSeriesKey({', '.join(args)})"


class EnsembleComponent(str, Enum):
    T0 = "t0"
    DISPATCH_INFO = "dispatch_info"
    MEMBER = "member"


class TimeSeriesMetadata(ArbitraryExtraModel):
    path: str
    columns: Sequence[TimeSeriesColumn] = Field(default_factory=lambda: [DEFAULT_VALUE_COLUMN])
    name: Optional[str] = None
    short_name: Optional[str] = None
    is_forecast: bool = False
    timezone: str = "UTC"

    @field_validator("columns")
    @classmethod
    def check_columns(cls, v: Sequence[TimeSeriesColumn]) -> Sequence[TimeSeriesColumn]:
        """Ensure value column exists and it's the first"""
        if v[0].key != "value":
            value_column = DEFAULT_VALUE_COLUMN
            non_value_columns = []
            for col in v:
                if col.key == "value":
                    value_column = col
                else:
                    non_value_columns.append(col)
            return [value_column] + non_value_columns
        return v


class TimeSeriesComment(AllowExtraModel):
    comment: str
    start: datetime
    end: datetime
    id: Optional[str] = None


class CommentSupport(Flag):
    UNSUPPORTED = 0
    READ = auto()
    WRITE = auto()
    DELETE = auto()
