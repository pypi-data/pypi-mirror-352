from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import numpy as np
import orjson
from httpx import (
    AsyncClient,
    ConnectTimeout,
    HTTPError,
    HTTPStatusError,
    PoolTimeout,
    ProtocolError,
    ReadError,
    ReadTimeout,
    Response,
    WriteError,
    WriteTimeout,
)
from pandas import Timestamp
from pydantic import BaseModel

from kisters.water.time_series.core.utils import model_dump

from .exceptions import KiWISDataSourceError, KiWISError, KiWISNoResultsError


def default_handler(v: Any) -> Any:
    if isinstance(v, np.ndarray):
        if v.shape == ():
            return v.tolist()
        if not v.flags["C_CONTIGUOUS"]:
            return np.ascontiguousarray(v)
        return list(v)
    if isinstance(v, bytes):
        return v.hex()
    if isinstance(v, Timestamp):
        return v.isoformat()
    return v


def orjson_dumps(content: Any) -> bytes:
    if isinstance(content, BaseModel):
        content = model_dump(content)
    return orjson.dumps(
        content,
        default=default_handler,
        option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC,
    )


@dataclass
class RetryPolicy:
    max_tries: int = 3
    retry_delay: float = 0.05
    timeout_increase_factor: int = 2
    timeout_soft_limit: int = 600


DEFAULT_RETRY_POLICY = RetryPolicy()


class AsyncAutoRetryClient(AsyncClient):
    def __init__(
        self,
        *args: Any,
        retry_policy: RetryPolicy,
        _internal_usage_key: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._retry_policy = retry_policy
        self._internal_usage_key = _internal_usage_key

    async def request(self, *args: Any, **kwargs: Any) -> Response:
        if self._internal_usage_key:
            if not kwargs.get("headers"):
                kwargs["headers"] = {}
            kwargs["headers"]["InternalUsageKey"] = self._internal_usage_key
        for i in range(self._retry_policy.max_tries):
            try:
                return await self.request_and_retry_lost_connections(*args, **kwargs)
            except (ReadTimeout, WriteTimeout, PoolTimeout) as e:
                self._raise_if_max_tries_exceeded(i)
                timeout = self.timeout
                if (
                    isinstance(e, ReadTimeout)
                    and timeout.read is not None
                    and timeout.read < self._retry_policy.timeout_soft_limit
                ):
                    timeout.read = timeout.read * self._retry_policy.timeout_increase_factor
                if (
                    isinstance(e, WriteTimeout)
                    and timeout.write is not None
                    and timeout.write < self._retry_policy.timeout_soft_limit
                ):
                    timeout.write = timeout.write * self._retry_policy.timeout_increase_factor
                self.timeout = timeout
                await asyncio.sleep(self._retry_policy.retry_delay)
            except HTTPError as e:
                self._raise_if_max_tries_exceeded(i)
                if isinstance(e, HTTPStatusError) and e.response.status_code == 503:
                    await asyncio.sleep(5)
                else:
                    await asyncio.sleep(self._retry_policy.retry_delay)
            except Exception:
                self._raise_if_max_tries_exceeded(i)
                await asyncio.sleep(self._retry_policy.retry_delay)
        return None  # type: ignore

    def _raise_if_max_tries_exceeded(self, i: int) -> None:
        if i == self._retry_policy.max_tries - 1:
            raise

    async def request_and_retry_lost_connections(self, *args: Any, **kwargs: Any) -> Response:
        try:
            response = await super().request(*args, **kwargs)
        except (WriteError, ReadError, ConnectTimeout, PoolTimeout, ProtocolError):
            response = await super().request(*args, **kwargs)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            try:
                json = self.to_json(response)
                message = json["message"]
                if json["code"] == "InvalidParameterValue" and "no results" in message:
                    raise KiWISNoResultsError(message) from e
                if (
                    json["code"] == "DatasourceError" and message == "Error getting tsdata from WDP."
                ) or json["code"] == "TooManyResults":
                    raise KiWISDataSourceError(message) from e
                message = f"{json['code']}: {message}"
                raise KiWISError(message) from e
            except orjson.JSONDecodeError:
                raise
        return response

    @staticmethod
    def to_json(response: Response) -> Any:
        return orjson.loads(response.content)
