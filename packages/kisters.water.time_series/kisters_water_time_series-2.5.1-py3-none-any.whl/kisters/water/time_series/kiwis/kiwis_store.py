from __future__ import annotations

from httpx import Auth, BasicAuth, Limits, Timeout

from kisters.water.time_series.core import TimeSeriesStore

from .async_auto_retry_client import DEFAULT_RETRY_POLICY, RetryPolicy
from .kiwis_time_series_client import DEFAULT_LIMITS, DEFAULT_TIMEOUT, KiWISTimeSeriesClient


class KiWISStore(TimeSeriesStore):
    """Connector to KiWIS backend over KiWIS REST API

    Args:
        base_url: Base url of REST API.
        data_source: Optional number identifying the data source.

    Examples:
        .. code-block:: python

            from kisters.water.time_series.kiwis import KiWISStore
            kiwis = KiWISStore('http://kiwis.kisters.de/KiWIS2/KiWIS')
            kiwis.get_by_path('DWD/07367/Precip/CmdTotal.1h')

    """

    def __init__(
        self,
        base_url: str,
        datasource: int = 0,
        user: str | None = None,
        password: str | None = None,
        auth: Auth | None = None,
        timeout: Timeout = DEFAULT_TIMEOUT,
        limits: Limits = DEFAULT_LIMITS,
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        _internal_usage_key: str | None = None,
    ) -> None:
        if user and password and not auth:
            auth = BasicAuth(user, password)
        self._client = KiWISTimeSeriesClient(
            base_url,
            datasource=datasource,
            auth=auth,
            timeout=timeout,
            limits=limits,
            retry_policy=retry_policy,
            _internal_usage_key=_internal_usage_key,
        )
